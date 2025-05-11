import streamlit as st
import speech_recognition as sr
import requests
import pygame
import uuid
from gtts import gTTS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# UI setup
st.set_page_config(page_title="BMI Health Advisor", layout="centered")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>BMI Health Advisor 💬</h1>", unsafe_allow_html=True)

# Get voice input
def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"API error: {e}"

# Speak output
def speak(text):
    tts = gTTS(text=text)
    filename = f"temp_{uuid.uuid4().hex}.mp3"
    tts.save(filename)
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.quit()
    os.remove(filename)

# OpenRouter chatbot advice
def get_openrouter_advice(query):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a health advisor."},
            {"role": "user", "content": query},
        ],
    }

    try:
        response = requests.post(OPENROUTER_ENDPOINT, json=data, headers=headers)
        result = response.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            error_message = result.get("error", {}).get("message", "Unknown error.")
            st.error(f"OpenRouter Error: {error_message}")
            return f"⚠️ Unable to fetch advice. {error_message}"

    except Exception as e:
        st.error(f"Request failed: {e}")
        return f"⚠️ Exception occurred: {e}"

# BMI calculator logic
weight = st.number_input("Enter your weight (kg):", min_value=10.0, max_value=300.0, step=0.5)
height = st.number_input("Enter your height (cm):", min_value=50.0, max_value=250.0, step=0.5)

if st.button("🎙️ Speak Instead"):
    text = get_voice_input()
    st.write("🗣️ You said:", text)

    import re
    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", text)]
    if len(nums) >= 2:
        weight = nums[0]
        height = nums[1]
        st.success(f"Using: Weight = {weight} kg, Height = {height} cm")
    else:
        st.warning("Couldn't detect weight and height properly.")

if st.button("Calculate BMI"):
    if height > 0:
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        st.success(f"Your BMI is: {bmi:.2f}")

        if bmi < 18.5:
            status = "Underweight"
            query = "Suggest a healthy way to gain weight for an underweight person using diet and exercise."
        elif 18.5 <= bmi <= 24.9:
            status = "Normal"
            query = "Suggest how to maintain current healthy weight through lifestyle and diet."
        else:
            status = "Overweight"
            query = "Suggest a healthy way to lose weight for an overweight person using diet and exercise."

        st.markdown(f"### Status: `{status}`")
        st.markdown("### 💡 Chatbot Advice:")
        advice = get_openrouter_advice(query)
        st.write(advice)

        speak(f"Your BMI is {bmi:.2f}. Status: {status}. Here's some advice: {advice}")
    else:
        st.warning("Please enter a valid height.")
