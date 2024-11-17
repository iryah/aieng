# streamlit_app.py
import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder
import os

st.title("SpeakMate AI - English Learning")

def main():
    st.write("Practice your English pronunciation!")
    
    # Ses kaydı
    audio_bytes = audio_recorder()
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
        # Backend'e gönder
        files = {"audio_file": ("audio.wav", audio_bytes, "audio/wav")}
        response = requests.post(
            "http://localhost:8000/check-pronunciation",
            files=files
        )
        
        if response.status_code == 200:
            result = response.json()
            
            st.write("### Your Speech:")
            st.write(result["transcription"])
            
            st.write("### Feedback:")
            st.write(result["feedback"])

if __name__ == "__main__":
    main()