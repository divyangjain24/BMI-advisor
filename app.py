import streamlit as st
import requests
import re

# 🔐 Use Streamlit secrets for OpenRouter API key
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# UI setup
st.set_page_config(page_title="BMI Health Advisor", layout="centered")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>BMI Health Advisor 💬</h1>", unsafe_allow_html=True)

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
    response = requests.post(OPENROUTER_ENDPOINT, json=data, headers=headers)

    try:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Unable to fetch advice. {str(e)}"

# BMI calculator logic
weight = st.number_input("Enter your weight (kg):", min_value=10.0, max_value=300.0, step=0.5)
height = st.number_input("Enter your height (cm):", min_value=50.0, max_value=250.0, step=0.5)

if st.button("🎙️ Speak Instead"):
    # This button is no longer needed and can be removed.
    st.write("🗣️ Voice input is disabled in this version.")

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
    else:
        st.warning("Please enter a valid height.")
