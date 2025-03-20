from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from models import my_farmer_db
from pydantic import BaseModel
from tools import logger, call_openai_api, OPENAI_API, predefined_questions, json_summary_plan_schema, summary_prompt
from handle_file import add_to_qdrant, query, delete_document_from_collection, extract_text_from_file
from typing import Optional
import json
import soundfile as sf
from fastapi.responses import JSONResponse
import uuid
from api_calls import start_scheduler
import threading
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import json
import logging
import numpy as np
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import tempfile
import wave
import webrtcvad
import numpy as np
import struct

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

class VoiceDetector:
    def __init__(self, sample_rate=16000, frame_duration=30):
        self.vad = webrtcvad.Vad(2)  # Reduced aggressiveness for better continuous speech detection
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.frame_size = int(sample_rate * frame_duration / 1000)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.silence_frames = 0
        self.max_silence_frames = 15  # Allow more silence between words
        self.min_speech_frames = 3  # Require minimum speech frames to avoid spurious detections
        self.speech_frames = 0
        self.is_speaking = False
        
    def _frame_generator(self, audio_data):
        """Generate audio frames from raw audio data."""
        if len(audio_data) < self.frame_size:
            self.logger.warning(f"Audio data too short: {len(audio_data)} bytes")
            return []
        
        n = len(audio_data)
        offset = 0
        frames = []
        while offset + self.frame_size <= n:
            frames.append(audio_data[offset:offset + self.frame_size])
            offset += self.frame_size
        return frames

    def _convert_audio_data(self, audio_data):
        """Convert audio data to the correct format."""
        try:
            # First try to interpret as float32
            float_array = np.frombuffer(audio_data, dtype=np.float32)
            # Convert float32 [-1.0, 1.0] to int16 [-32768, 32767]
            int16_array = (float_array * 32767).astype(np.int16)
            return int16_array
        except ValueError:
            try:
                # If that fails, try direct int16 interpretation
                return np.frombuffer(audio_data, dtype=np.int16)
            except ValueError as e:
                # If both fail, try to pad the data to make it aligned
                padding_size = (2 - (len(audio_data) % 2)) % 2
                if padding_size > 0:
                    padded_data = audio_data + b'\x00' * padding_size
                    return np.frombuffer(padded_data, dtype=np.int16)
                raise e

    def detect_voice(self, audio_data):
        """
        Detect voice activity in audio data.
        
        Args:
            audio_data (bytes): Raw audio data
            
        Returns:
            bool: True if voice activity is detected, False otherwise
        """
        try:
            if audio_data is None or len(audio_data) == 0:
                self.logger.warning("Audio data is empty or None")
                return False
                
            # Convert audio data to the correct format
            try:
                audio_array = self._convert_audio_data(audio_data)
                if len(audio_array) == 0:
                    self.logger.warning("No valid audio data after conversion")
                    return False
            except ValueError as e:
                self.logger.error(f"Error converting audio data: {str(e)}")
                return False
            
            # Process frames
            frames = self._frame_generator(audio_array)
            if not frames:
                self.logger.warning("No frames generated from audio data")
                return False
                
            # Count speech frames in this chunk
            current_speech_frames = 0
            for frame in frames:
                try:
                    # Pack the frame into bytes
                    frame_bytes = struct.pack("%dh" % len(frame), *frame)
                    
                    # Check for voice activity
                    if self.vad.is_speech(frame_bytes, self.sample_rate):
                        current_speech_frames += 1
                        self.speech_frames += 1
                        self.silence_frames = 0
                    else:
                        self.silence_frames += 1
                        
                except struct.error as se:
                    self.logger.error(f"Error packing frame data: {str(se)}")
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing frame: {str(e)}")
                    continue
            
            # Update speaking state
            if current_speech_frames > 0:
                if not self.is_speaking and self.speech_frames >= self.min_speech_frames:
                    self.is_speaking = True
                return True
            elif self.silence_frames > self.max_silence_frames:
                if self.is_speaking:
                    self.is_speaking = False
                    self.speech_frames = 0
                return False
            
            # Keep current state if in transition
            return self.is_speaking
            
        except Exception as e:
            self.logger.error(f"Error in voice detection: {str(e)}")
            return False 

# Initialize OpenAI and Groq clients
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#
groq_client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)


async def transcribe_audio(audio_data: bytes):
    """Transcribe audio using Groq's Whisper model"""
    temp_wav = None
    try:
        # Create a unique temporary file
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        wav_path = temp_wav.name
        temp_wav.close()  # Close the file handle immediately
        
        # Write the WAV file
        with wave.open(wav_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
            wav_file.setframerate(16000)  # 16kHz
            wav_file.writeframes(audio_data)
        
        # Transcribe using Groq
        with open(wav_path, 'rb') as audio_file:
            response = await groq_client.audio.transcriptions.create(
                model="whisper-large-v3-turbo",
                file=audio_file,
                response_format="text"
            )
        
        return response
            
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        return None
    finally:
        # Clean up the temporary file
        if temp_wav is not None:
            try:
                os.unlink(temp_wav.name)
            except Exception as e:
                logger.error(f"Error deleting temporary file: {str(e)}")

async def get_chat_response(text: str):
    """Get chat response from Groq"""
    try:
        response = await groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Please provide a clear, concise, and accurate response."},
                {"role": "user", "content": text}
            ],
            temperature=0,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Chat response error: {str(e)}")
        return None

async def generate_speech(text: str):
    """Generate speech using OpenAI TTS"""
    try:
        response = await openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        # Get the speech data directly from the response
        # No need to await response.read() as the response is already the audio data
        return response.content
    except Exception as e:
        logger.error(f"Speech generation error: {str(e)}")
        return None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    voice_detector = VoiceDetector()
    audio_buffer = bytearray()
    silence_duration = 0
    max_silence_duration = 1.5  # seconds
    frames_per_second = 1000 / voice_detector.frame_duration  # frames per second
    max_silence_frames = int(max_silence_duration * frames_per_second)
    
    try:
        while True:
            try:
                data = await websocket.receive_bytes()
                
                if not data:
                    logger.warning("Received empty data frame")
                    continue
                
                # Check for voice activity
                voice_detected = voice_detector.detect_voice(data)
                
                if voice_detected:
                    # Reset silence counter and add to buffer
                    silence_duration = 0
                    audio_buffer.extend(data)
                    await websocket.send_json({"type": "vad", "status": "active"})
                else:
                    # Increment silence counter
                    silence_duration += 1
                    
                    # If we were collecting speech and hit max silence, process the buffer
                    if len(audio_buffer) > 0 and silence_duration >= max_silence_frames:
                        logger.info(f"Processing audio buffer of size: {len(audio_buffer)} bytes")
                        
                        # Process the complete utterance
                        transcription = await transcribe_audio(bytes(audio_buffer))
                        if transcription:
                            logger.info(f"Transcription: {transcription}")
                            await websocket.send_json({
                                "type": "transcription",
                                "text": transcription
                            })
                            
                            # Get chat response
                            chat_response = await get_chat_response(transcription)
                            if chat_response:
                                logger.info(f"Chat response: {chat_response}")
                                await websocket.send_json({
                                    "type": "chat_response",
                                    "text": chat_response
                                })
                                
                                # Generate and send voice response
                                voice_response = await generate_speech(chat_response)
                                if voice_response:
                                    logger.info("Generated voice response")
                                    await websocket.send_bytes(voice_response)
                        
                        # Clear the buffer after processing
                        audio_buffer = bytearray()
                        await websocket.send_json({"type": "vad", "status": "inactive"})
                    elif len(audio_buffer) > 0:
                        # Still collecting silence, add to buffer
                        audio_buffer.extend(data)
            
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
                break
            except Exception as e:
                logger.error(f"Error processing websocket frame: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
    finally:
        logger.info("Closing WebSocket connection")
        await websocket.close()

if __name__ == "__main__":  
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)