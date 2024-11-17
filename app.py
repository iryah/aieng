# app.py
import streamlit as st
import requests
import sounddevice as sd
import wavio
import numpy as np
import tempfile
import os
from datetime import datetime

st.set_page_config(page_title="AI English Teacher", page_icon="🎓", layout="wide")

# Stil
st.markdown("""
    <style>
    .stApp {
        background-color: #1a1a1a;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #2ecc71;
        color: white;
        border-radius: 20px;
        padding: 10px 25px;
        font-size: 18px;
    }
    .example-box {
        background-color: #2c3e50;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

def record_audio(duration=5, sample_rate=44100):
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(duration):
            if i == 0:
                audio_data = sd.rec(int(duration * sample_rate),
                                  samplerate=sample_rate,
                                  channels=1,
                                  dtype='int16')
            progress_bar.progress((i + 1) / duration)
            status_text.text(f"Recording... {duration - i} seconds remaining")
            sd.sleep(1000)
        
        sd.wait()
        status_text.text("Recording complete!")
        progress_bar.empty()
        return audio_data, sample_rate
    except Exception as e:
        st.error(f"Recording error: {str(e)}")
        return None, None

def save_audio(audio_data, sample_rate):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"audio_{timestamp}.wav")
        wavio.write(temp_file, audio_data, sample_rate, sampwidth=2)
        return temp_file
    except Exception as e:
        st.error(f"Save error: {str(e)}")
        return None

# Ana başlık
st.title("🎓 AI English Teacher")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    duration = st.slider("Recording Duration (seconds)", 3, 15, 5)
    
    st.header("📚 Example Texts")
    categories = {
        "Self Introduction": [
            "Hi, my name is [Name]. I'm from [Country] and I love learning English.",
            "I'm a student studying computer science. In my free time, I enjoy playing sports.",
            "I've been learning English for two years, and I want to improve my speaking skills."
        ],
        "Daily Routines": [
            "Every morning, I wake up at 7 AM and have breakfast with my family.",
            "After work, I usually go to the gym and then cook dinner.",
            "On weekends, I like to meet friends and watch movies."
        ],
        "Job Interview": [
            "I have three years of experience in software development.",
            "My greatest strength is my ability to solve complex problems.",
            "I'm looking for opportunities to grow professionally in a dynamic company."
        ],
        "Travel": [
            "I'd like to book a room for two nights, please.",
            "Could you recommend some good local restaurants?",
            "What's the best way to get to the city center from here?"
        ]
    }
    
    selected_category = st.selectbox("Select Category", list(categories.keys()))
    
    st.write("### Example Sentences:")
    for text in categories[selected_category]:
        st.markdown(f"""
        <div class='example-box'>
        {text}
        </div>
        """, unsafe_allow_html=True)

    st.write("### Your Text:")
    custom_text = st.text_area("Write your own text to practice:", height=100)

# Ana içerik
st.markdown(f"""
### 🎤 Practice Speaking
Choose a sentence from the examples or write your own, then click 'Start Recording' to practice!
""")

if st.button("🎙️ Start Recording", use_container_width=True):
    try:
        audio_data, sample_rate = record_audio(duration=duration)
        
        if audio_data is not None:
            audio_file = save_audio(audio_data, sample_rate)
            
            if audio_file:
                with st.spinner('🤖 AI is analyzing your speech...'):
                    with open(audio_file, 'rb') as f:
                        files = {"audio_file": ("audio.wav", f, "audio/wav")}
                       response = requests.post("https://aieng-production.up.railway.app/speak", files=files, timeout=30)
                        )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    st.success("✨ Analysis complete!")
                    
                    st.markdown("### 🗣️ Your Speech:")
                    st.info(result["text"])
                    
                    st.markdown("### 📝 AI Feedback:")
                    st.info(result["feedback"])
                    
                    # Konuşma skoru ekleyelim
                    words = len(result["text"].split())
                    score = min(100, int((words / duration) * 20))  # Basit bir skor hesaplama
                    st.progress(score/100)
                    st.markdown(f"Speaking Score: {score}%")
                    
                else:
                    st.error("❌ Server error. Please try again.")
                
                try:
                    os.remove(audio_file)
                except:
                    pass
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    Made with ❤️ by AI English Team | v1.0
</div>
""", unsafe_allow_html=True)