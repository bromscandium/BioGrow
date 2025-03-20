from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from models import my_farmer_db
from pydantic import BaseModel
from tools import logger, call_openai_api, OPENAI_API, predefined_questions, json_summary_plan_schema, summary_prompt
from handle_file import add_to_qdrant, query, delete_document_from_collection, extract_text_from_file
import asyncio
from typing import Optional
import base64
import json
import soundfile as sf
from websockets import WebSocketClientProtocol
import websockets
import uuid
from api_calls import start_scheduler
import threading

app = FastAPI()

class Conversation(BaseModel):
    person_id: Optional[str] = None
    conversation_id: Optional[str] = None
    message: str
    context: str
 

class FileItem(BaseModel):
    file_name: str
    file_data: bytes

class CommunityPost(BaseModel):
    title: str
    content: str
    image_data: bytes
    number_of_likes: int = 0
    number_of_comments: int = 0


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],  
    allow_credentials=True,
    allow_headers=["*"],  
)

@app.post("/get_openai_answer")
async def get_openai_answer(item: Conversation):
    conversation_id = item.conversation_id
    message = item.message
    collection_name = item.person_id
    context = item.context

    logger.info("Received conversation_id: %s, message: %s", conversation_id, message)

    if conversation_id:
        try:
            conversation_id = uuid.UUID(conversation_id)  # Ensure it's a valid UUID
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid conversation_id format. Expected a UUID.")

        db_row = my_farmer_db.get_chat_conversation_by_id(id=conversation_id)
        
        if db_row is None:
            # If no conversation is found with the provided ID, create a new conversation.
            conversation = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ]
        else:
            # Extract the conversation list from the returned dictionary.
            conversation = db_row.get("conversation", [])
            conversation.append({"role": "user", "content": message})
    else:
        # No conversation_id provided; create a new conversation.
        conversation = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ]
        conversation_id = None

    if collection_name:
    # Add context and call OpenAI API.
        context = await query(message, collection_name=collection_name)
        conversation.append({"role": "system", "content": f'Use the following context: {context}'})
    else:
        context = None

    openai_response = await call_openai_api(conversation)
    conversation.append({"role": "assistant", "content": openai_response})
    
    # Update or insert the conversation into the DB.
    if conversation_id:
        my_farmer_db.update_chat_conversation(conversation_id, conversation)
    else:
        conversation_id = my_farmer_db.insert_chat_conversation(conversation)

    return {
        "message": "Response generated successfully",
        "answer": openai_response,
        "conversation_id": conversation_id,
        'context': context
    }


@app.post("/get_user_info")
async def get_user_info(person_id: str):
    user_info = my_farmer_db.get_user_by_id(person_id)
    return {"user_info": user_info}

@app.post("/add_to_community")
async def add_to_community(item: CommunityPost):
    title = item.title
    content = item.content
    image_data = item.image_data
    number_of_likes = item.number_of_likes
    number_of_comments = item.number_of_comments

    # Save the image to disk
    image_path = f"images/{title}.jpg"
    with open(image_path, "wb") as f:
        f.write(image_data)

    # Insert the post into the database
    my_farmer_db.insert_community(title, content, image_path, number_of_likes, number_of_comments)
    return {"message": "Post added successfully"}

@app.get("/get_community_posts")
async def get_community_posts():
    posts = my_farmer_db.get_all_community_posts()
    return {"posts": posts}

@app.get('/get_insights')
async def get_recommendations(id: uuid.UUID):
    # Optionally force an on-demand update:
    # fetch_all_data()
    insights = my_farmer_db.get_api_data_by_id(id)
    conversation = [{"role": "system", "content": "You are a helpful assistant."}]
    conversation.append({"role": "system", "content": f'Here are the insights: {insights}'})

    # TODO add json schema in this call

    insights = call_openai_api(conversation)
    return {"insights": insights}


@app.post("/add_data")
async def add_data(
    file: UploadFile = File(...),
    file_name: str = Form(...),
    collection_name: str = Form(...)
):
    try:
        file_data = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error reading file")

    # Adjust the extraction function to ignore errors in decoding.
    try:
        # Example: decode with errors ignored (modify extract_text_from_file accordingly)
        file_text = extract_text_from_file(file_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error extracting text from file")

    result = add_to_qdrant(text=file_text, source=file_name, collection_name=collection_name)
    return {"message": "Data added successfully"}

@app.post("/delete_data")
async def delete_data(item: FileItem):
    file_name = item.file_name
    result = delete_document_from_collection("text_collection", file_name)
    # result = farmer_db.
    return {"message": "Data deleted successfully"}

@app.post('/personalized_plan')
async def personalized_plan(answer: Optional[str] = None):
    """
    This endpoint receives an optional answer from the frontend.
    If no answer is provided, it defaults to an empty string.
    It iterates over all predefined questions, yielding each question back to the frontend.
    Once all questions are processed, it appends a summary prompt, calls the OpenAI API,
    parses the returned JSON, starts a background scheduler thread, and stores the data in the database.
    """
    # Default answer to empty string if not provided.
    if answer is None:
        answer = ""
    
    async def stream_response():
        conversation = []
        # Loop through all predefined questions.
        for current_question in predefined_questions:
            # Append the current question and the provided (or default) answer to the conversation.
            conversation.append({'role': 'system', 'content': current_question})
            conversation.append({'role': 'user', 'content': answer})
            # Yield the current question to the frontend (as a JSON string).
            yield json.dumps({"question": current_question}) + "\n"
            await asyncio.sleep(0)  # Yield control to the event loop

        # After processing all questions, append the summary prompt.
        conversation.append({'role': 'system', 'content': summary_prompt})
        
        # Call the OpenAI API to get the final structured answer.
        openai_response = await call_openai_api(conversation, json_schema=json_summary_plan_schema)
        try:
            parsed_response = json.loads(openai_response)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail="Invalid JSON response from OpenAI API")
        
        # Extract needed fields from the parsed response.
        location = parsed_response.get("location")
        longitude = parsed_response.get("longitude")
        latitude = parsed_response.get("latitude")
        crop = parsed_response.get("crop")
        crop_stage = parsed_response.get("crop_stage")
        planting_date_plan = parsed_response.get("planting_date_plan")
        planted_date = parsed_response.get("planted_date")
        harvest_date = parsed_response.get("harvest_date")
        planting_area = parsed_response.get("planting_area")
        previous_crop = parsed_response.get("previous_crop")
        irrigation_method = parsed_response.get("irrigation_method")
        fertilizers = parsed_response.get("fertilizers")
        water_availability = parsed_response.get("water_availability")
        pest_disease_issues = parsed_response.get("pest_disease_issues")
        pest_disease_control = parsed_response.get("pest_disease_control")
        biological_protection = parsed_response.get("biological_protection")
        soil_info = parsed_response.get("soil_info")
        
        # Start the background scheduler thread with the provided coordinates.
        scheduler_thread = threading.Thread(
            target=start_scheduler, args=(longitude, latitude), daemon=True
        )
        scheduler_thread.start()
        
        # Insert the structured data into the database.
        new_id = my_farmer_db.insert_users(
            longtitude=longitude,
            latitude=latitude,
            location=location,
            crops=crop,
            additional_info=json.dumps({
                "crop_stage": crop_stage,
                "planting_date_plan": planting_date_plan,
                "planted_date": planted_date,
                "harvest_date": harvest_date,
                "planting_area": planting_area,
                "previous_crop": previous_crop,
                "irrigation_method": irrigation_method,
                "fertilizers": fertilizers,
                "water_availability": water_availability,
                "pest_disease_issues": pest_disease_issues,
                "pest_disease_control": pest_disease_control,
                "biological_protection": biological_protection,
                "soil_info": soil_info
            })
        )
        
        # Yield the final response to the frontend.
        final_result = {"person_id": new_id, "data": parsed_response}
        yield json.dumps(final_result) + "\n"
    
    return StreamingResponse(stream_response(), media_type="application/json")

async def _send_session_update(openai_ws: WebSocketClientProtocol) -> None:
    """Send the session update to the OpenAI WebSocket."""
    session_update = {}
    print(f'Sending session update:', json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))

async def _receive_from_client(self, websocket: WebSocket, openai_ws: WebSocketClientProtocol) -> None:
        """Receive a message from the client."""
        try:
            async for message in websocket.iter_json():
                if message['event'] == 'media' and openai_ws.open:
                    audio_append = {
                        "type": "input_audio_buffer.append",
                        "audio": message['media']['payload']
                    }
                    await openai_ws.send(json.dumps(audio_append))
                # TODO: Handle other event types if needed
        except WebSocketDisconnect:
            print("Client disconnected.")
            if openai_ws.open:
                await openai_ws.close()



async def _send_to_client(openai_ws: WebSocketClientProtocol) -> None:
    """Send a message to the client."""
    try:
        async for openai_message in openai_ws:
            response = json.loads(openai_message)
            if response['type'] == 'response.audio.delta' and response.get('delta'):
                # decode the audio delta received from OpenAI
                audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                # decide what to do with it.
                ...
                print(f"Sending audio delta: {audio_payload}")

            if response['type'] == 'response.output_item.done':
                if "item" in response and response["item"]["type"] == "function_call":
                    item = response["item"]
                    function_args = json.loads(item["arguments"])
      
                    # add the function output to the convo
                    await openai_ws.send(json.dumps({
                        "type": "conversation.item.create",
                        "item": {
                            "type": "function_call_output",
                            "call_id": item["call_id"],
                        }
                    }))
                    # define a response_create object to 
                    # trigger the response
                    response_create = {}
                    await openai_ws.send(json.dumps(response_create))
    except Exception as e:
        print(f"Error in send_to_client: {e}")

# OpenAI Realtime API endpoint and your key (make sure to store keys securely)
OPENAI_REALTIME_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
async def setup_websocket():    
    headers = { "api-key": OPENAI_API }
    # define the OpenAI Realtime API websocket URL. This is for the Azure deployment
    async with websockets.connect(OPENAI_REALTIME_URL, extra_headers=headers) as openai_ws:
        # send the session update first before starting the conversation
        resp = await _send_session_update(openai_ws)
        # start listening and sending requests to the OpenAI ws
        await asyncio.gather(
            _receive_from_client(openai_ws),
            _send_to_client(openai_ws)
        )

if __name__ == "__main__":  
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)