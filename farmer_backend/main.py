from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from models import my_farmer_db
from pydantic import BaseModel
import httpx
from tools import logger, call_openai_api, OPENAI_API, predefined_questions, json_summary_plan_schema, summary_prompt
from handle_file import add_to_qdrant, query, delete_document_from_collection, extract_text_from_file
from typing import Optional
import json
import soundfile as sf
from fastapi.responses import JSONResponse
import uuid
from api_calls import start_scheduler
import threading
import uvicorn
import json
import numpy as np
import os

import numpy as np

app = FastAPI()

class Conversation(BaseModel):
    person_id: Optional[str] = None
    conversation_id: Optional[str] = None
    message: str
    context: Optional[str] = None
 

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
        try:
            api_data = my_farmer_db.get_api_data_by_id(collection_name)

            if api_data:
                # Extract the conversation list from the returned dictionary.
                conversation = db_row.get("conversation", [])
                conversation.append({"role": "user", "content": message})
                conversation.append({"role": "system", "content": f'Here are the insights: {api_data}'})
            else:
                conversation = db_row.get("conversation", [])
                conversation.append({"role": "user", "content": message})
        except Exception as e:
            raise HTTPException(status_code=400, detail="Error fetching data from the database.")
        try:
            context = await query(message, collection_name=collection_name)
            conversation.append({"role": "system", "content": f'Use the following context: {context}'})
        except Exception as e:
            raise HTTPException(status_code=400, detail="Error fetching data from the database.")    
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
async def get_recommendations(id: str):
    # Optionally force an on-demand update:
    # fetch_all_data()
    insights = my_farmer_db.get_api_data_by_id(id)
    logger.info("Retrieved insights: %s", insights)
    conversation = [{"role": "system", "content": "You are a helpful assistant."}]
    conversation.append({"role": "system", "content": f'Here are the insights: {insights}'})

    # TODO add json schema in this call

    insights = await call_openai_api(conversation)
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


conversation_state = {}  # { conversation_id: { "conversation": [...], "current_index": int } }


@app.post('/personalized_plan')
async def personalized_plan(
    answer: Optional[str] = None,
    conversation_id: Optional[str] = None,
):
    """
    Interactive conversation endpoint.
    
    - If no conversation_id is provided, a new conversation is started.
    - Each call supplies an optional answer for the current question.
    - The endpoint returns the next question (with conversation_id and q_index).
    - The endpoint returns the next question (with conversation_id).
      the conversation is sent to OpenAI, the structured response is parsed,
      a background scheduler is started, and the result is stored in the DB.
    """
    # If no conversation_id, start a new conversation.
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
        conversation_state[conversation_id] = {
            "conversation": [],
            "current_index": 0
        }
    
    # Retrieve state for this conversation.
    state = conversation_state.get(conversation_id)
    if state is None:
        raise HTTPException(status_code=400, detail="Invalid conversation_id")
    
    # If an answer is provided, store it for the current question.
    # We expect that q_index == state["current_index"].
    if answer is not None:
        # Append the current question and the user's answer.
        current_index = state["current_index"]
        # Safety check: ensure the index is within range.
        if current_index < len(predefined_questions):
            state["conversation"].append({
                'role': 'system',
                'content': predefined_questions[current_index]
            })
            state["conversation"].append({
                'role': 'user',
                'content': answer
            })
            state["current_index"] += 1
        else:
            # All questions have been answered.
            pass

    # If there are still unanswered questions, return the next question.
    if state["current_index"] < len(predefined_questions):
        next_question = predefined_questions[state["current_index"]]
        return JSONResponse({
            "conversation_id": conversation_id,
            "question": next_question,
            "q_index": state["current_index"]
        })
    else:
        # All questions answered; complete the conversation.
        state["conversation"].append({'role': 'system', 'content': summary_prompt})
        # Call OpenAI API with the full conversation.
        logger.info("Calling OpenAI API with conversation: %s", state["conversation"])
        openai_response = await call_openai_api(state["conversation"], json_schema=json_summary_plan_schema)
        try:
            parsed_response = json.loads(openai_response)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON response from OpenAI API")
        
        # Extract fields from the parsed response.
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
        
        
        # Insert the structured data into your database.
        result = my_farmer_db.insert_users(
            id=conversation_id,
            longitude=longitude,
            latitude=latitude,
            location=location,
            crops=[crop],
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

        # Start a background scheduler thread (if your scheduler needs updated coordinates).
        scheduler_thread = threading.Thread(
            target=start_scheduler, args=(conversation_id, longitude, latitude), daemon=True
        )
        scheduler_thread.start()
        
        # Once completed, remove the conversation state.
        del conversation_state[conversation_id]
        
        # Return the final structured result.
        return JSONResponse({"person_id": conversation_id, "data": parsed_response})
    
@app.get("/session")
async def get_session():
    url = "https://api.openai.com/v1/realtime/sessions"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-realtime-preview-2024-12-17",
        "voice": "verse"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    data = response.json()
    return data

if __name__ == "__main__":  
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)