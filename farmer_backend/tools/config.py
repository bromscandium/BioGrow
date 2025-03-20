from dotenv import load_dotenv
import os


load_dotenv()

OPENAI_API = os.getenv("OPENAI_API_KEY")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

QDRANT_CLIENT_HOST = os.getenv("QDRANT_CLIENT_HOST")


GEMINI_PROMPT : str = """
Your tasks are:

1. Perform thorough OCR on all pages of the provided document or image.

2. Extract ALL written text, ensuring no information is missed.

3. Double-check and verify the following elements for consistency across the entire document:
   a. Names
   b. Numbers
   c. Dates
   d. People mentioned
   e. Checkboxes (checked or unchecked)
   f. Phone numbers

4. Ensure logical consistency of dates and names throughout the document.

5. Verify that all extracted information is coherent and makes sense in context.

6. Provide a comprehensive and accurate transcription of the entire document without page separation.

7. Return the transcription in a clean, readable format. If there are several languages present in the document, separate the text by language.

Remember: Accuracy, completeness, and consistency are your top priorities. Do not omit any text, no matter how insignificant it may seem.
Return only the text without explanations or comments. If there is no text, no images, or the document is blank, return an empty string.
""".strip()


async def build_chat_conversation(SYSTEM_PROMPT: str, user_query: str = "") -> str:
    conversation = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]
    return conversation

async def update_chat_conversation(conversation: list, user_query: str = "", ai_answer: str = "") -> list:
    if ai_answer:
        conversation.append({"role": "assistant", "content": ai_answer})
    if user_query:
        conversation.append({"role": "user", "content": user_query})
    return conversation

async def build_conversation(prompt: str, summary_text: str) -> list[dict]:
    # Format the prompt so that only the {cv_text} placeholder is replaced
    formatted_prompt = prompt.format(text=summary_text)
    return [
        {"role": "system", "content": formatted_prompt},
    ]

json_schema = {
  "type": "json_schema",
  "json_schema": {
    "name": "OpenAIOutput",
    "schema": {
      "title": "OpenAIOutput",
      "type": "object",
      "properties": {
          "name": {
          "type": "string",
          "description": "The name of the person."
        },
            'age': {
            'type': 'string',  
            'description': 'The age of the person.'
        },
        'occupation': {
            'type': 'string',  
            'description': 'The current occupation of the person.'
        },
        'education': {
            'type': 'string',  
            'description': 'The educational qualifications of the person.'
        },
        'experience': {
            'type': 'string',  
            'description': 'The work experience of the person.'
        },
        'skills': {
            'type': 'string',  
            'description': 'The skills of the person.'
        },
        'aspirations': {
            'type': 'string',  
            'description': 'The future aspirations of the person.'
        }
      }
    }
    }
}

json_summary_plan_schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "FarmingCropPlan",
        "schema": {
            "title": "Farming Crop Plan",
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Which city or village is your farm closest to? (e.g., 'Punjab, India')"
                },
                "longitude": {
                    "type": "string",
                    "description": "What's the longitude of your farm? (e.g., '75.3412')"
                },
                "latitude": {
                    "type": "string",
                    "description": "What's the latitude of your farm? (e.g., '31.5497')"
                },
                "crop": {
                    "type": "string",
                    "description": "Which crop are you planning to plant? (Rice, Wheat, Cotton, Other (specify))"
                },
                "crop_stage": {
                    "type": "string",
                    "description": "At what stage are you currently with your crop? (Planning, Just Planted, Growing Stage, Approaching Harvest)"
                },
                "planting_date_plan": {
                    "type": "string",
                    "description": "When do you plan to plant? (Specific date like 'June 15th' or Approximate period like 'Mid-June') [Only if 'Planning']"
                },
                "planted_date": {
                    "type": "string",
                    "description": "When did you plant your crop? (Exact date preferred, e.g., 'June 15th') [Only if 'Just Planted' or 'Growing Stage']"
                },
                "harvest_date": {
                    "type": "string",
                    "description": "When do you expect to harvest your crop? (Specific date like 'November 25th' or Approximate period like 'Late November') [Only if 'Approaching Harvest']"
                },
                "planting_area": {
                    "type": "string",
                    "description": "What's the approximate size of your planting area? (Numeric input, e.g., '5 acres')"
                },
                "previous_crop": {
                    "type": "string",
                    "description": "Which crop did you plant previously on this land? (Rice, Wheat, Cotton, Other (specify), None (fallow land))"
                },
                "irrigation_method": {
                    "type": "string",
                    "description": "Which irrigation method are you currently using? (Rain-fed, Canal, Tube wells, Drip irrigation, Sprinkler irrigation, Other (specify))"
                },
                "fertilizers": {
                    "type": "string",
                    "description": "Are you currently using any fertilizers? (Chemical fertilizers, Organic fertilizers, Both, None)"
                },
                "water_availability": {
                    "type": "string",
                    "description": "Do you typically experience water availability challenges? (Yes, No)"
                },
                "pest_disease_issues": {
                    "type": "string",
                    "description": "Have you experienced pest or disease issues in past seasons? (Yes, No)"
                },
                "pest_disease_control": {
                    "type": "string",
                    "description": "What pest/disease control methods are you using now? (Chemical pesticides, Biological products, Integrated Pest Management (IPM), None, Other (specify))"
                },
                "biological_protection": {
                    "type": "string",
                    "description": "Are you familiar with biological protection products? (Yes, No)"
                },
                "soil_info": {
                    "type": "string",
                    "description": "What kind of soil do you have on your farm (sandy, clay, black soil, or something else)? And is your land flat or hilly?"
                }
            }
        }
    }
}

summary_prompt = '''
Based on our conversation and the provided format, 
summarize all the information into a single JSON response. 
Your JSON output must conform exactly to the following schema: 
keys include 'location', 'longitude', 'latitude', 'crop', 'crop_stage', 'planting_date_plan', 
'planted_date', 'harvest_date', 'planting_area', 'previous_crop', 
'irrigation_method', 'fertilizers', 'water_availability', 
'pest_disease_issues', 'pest_disease_control', 'biological_protection', and 'soil_info'. 
Ensure the JSON is valid and follows the structure defined in the JSON schema.
Put some dummy data if nothing provided
'''
# The following questions will be asked from the user:
predefined_questions = [

    "Hello! I'm your personal farming companion. Let's build your personalized crop growth plan. Which city or village is your farm closest to?",
    "Great! Based on your location, which crop are you planning to plant?",
    # "At what stage are you currently with your crop?",
    # "When do you plan to plant? (Approximate or specific date)",
    # "When did you plant your crop? (Exact date preferred)",
    # "When do you expect to harvest your crop? (Approximate or specific date)",
    # "What's the approximate size of your planting area? (in acres)",
    # "Which crop did you plant previously on this land?",
    # "Which irrigation method are you currently using?",
    # "Are you currently using any fertilizers?",
    # "Do you typically experience water availability challenges?",
    # "Have you experienced pest or disease issues in past seasons?",
    # "What pest/disease control methods are you using now?",
    # "Are you familiar with biological protection products?",
    # "What kind of soil do you have on your farm (sandy, clay, black soil, or something else)? And is your land flat or hilly?"
]




# The JSON schema above defines the expected structure for the final output based on the user's responses.

# async def build_conversation(user_query:str, collection_name:str = "documents") -> dict:
#     documents_text = query()
#     conversation = [
#         {"role": "system", "content": f"You are a helpful assistant. Use the following information to help you. {results}"},
#         {"role": "user", "content": user_query}
#     ]
#     return conversation