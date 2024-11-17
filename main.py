# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from openai import OpenAI
import os
from dotenv import load_dotenv
import tempfile
import shutil
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="AI English Teacher")
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to AI English Teacher"}

@app.post("/speak")
async def check_speech(audio_file: UploadFile):
    try:
        logger.info("Received audio file")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            shutil.copyfileobj(audio_file.file, temp_file)
            temp_path = temp_file.name

        with open(temp_path, 'rb') as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                language="en",
                prompt="This is an English speech practice session."
            )

        os.unlink(temp_path)

        if not transcript.text:
            return {
                "text": "No speech detected", 
                "feedback": "Please try speaking again."
            }

        logger.info(f"Transcribed text: {transcript.text}")

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """You are an experienced and encouraging English teacher.
                Your task is to:
                1. Listen to the student's English speech
                2. Provide constructive feedback on:
                   - Pronunciation
                   - Grammar
                   - Vocabulary usage
                   - Sentence structure
                3. Always be encouraging and positive
                4. Give specific examples of improvements if needed
                5. Keep feedback concise but helpful"""},
                {"role": "user", "content": f"Student's speech: {transcript.text}"}
            ]
        )

        feedback = response.choices[0].message.content
        logger.info(f"Generated feedback: {feedback}")

        return {
            "text": transcript.text,
            "feedback": feedback
        }

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)