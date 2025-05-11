import streamlit as st
import requests

# 🔐 Use Streamlit secrets for OpenRouter API key
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# UI setup
st.set_page_config(page_title="BMI Health Advisor", layout="centered")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>BMI Health Advisor 💬</h1>", unsafe_allow_html=True)

# Function to get advice from OpenRouter API with bullet formatting
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
        response.raise_for_status()
        result = response.json()

        if "choices" in result:
            advice = result["choices"][0]["message"]["content"]

            # Handle both '|' and newline as separators
            if "|" in advice:
                segments = [segment.strip() for segment in advice.split("|") if segment.strip()]
            else:
                segments = [line.strip() for line in advice.split("\n") if line.strip()]

            # Return as markdown bullet points
            return "\n".join([f"- {line}" for line in segments])
        else:
            return "⚠️ Unable to fetch valid advice from the response."

    except requests.exceptions.RequestException as e:
        return f"⚠️ API request failed: {str(e)}"
    except Exception as e:
        return f"⚠️ An error occurred: {str(e)}"

# BMI calculator inputs
weight = st.number_input("Enter your weight (kg):", min_value=10.0, max_value=300.0, step=0.5)
height = st.number_input("Enter your height (cm):", min_value=50.0, max_value=250.0, step=0.5)

if st.button("Calculate BMI"):
    if height > 0:
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        st.success(f"Your BMI is: {bmi:.2f}")

        # Determine status and get appropriate query
        if bmi < 18.5:
            status = "Underweight"
            query = "Act as a certified BMI doctor and nutritionist. My BMI is below 18.5, which classifies me as underweight. Please provide a medically accurate and structured treatment plan to help me gain weight in a healthy and sustainable way. Include dietary recommendations, safe exercise routines, and lifestyle changes. Use bullet points for clarity. Also, mention potential risks of being underweight and when I should seek medical attention."
        elif 18.5 <= bmi <= 24.9:
            status = "Normal"
            query = "You are an expert BMI doctor and fitness consultant. My BMI is in the normal range (18.5 to 24.9). Please advise me on how to maintain this healthy BMI through a balanced diet, fitness habits, and lifestyle choices. Provide practical tips for long-term weight management, stress reduction, and early signs that may indicate a shift away from this healthy range. Use bullet points and simple explanations."
        else:
            status = "Overweight"
            query = "Act as a professional BMI doctor and health coach. My BMI is above 25, putting me in the overweight category. I want a detailed, medically sound plan to reduce my BMI safely. Suggest a diet strategy, workout routine, and lifestyle habits for healthy weight loss. Keep your response structured using bullet points, and include cautionary notes on crash diets or unhealthy practices. Also mention when it’s important to consult a physician."

        st.markdown(f"### Status: `{status}`")
        st.markdown("### 💡 Experts Advice:")
        advice = get_openrouter_advice(query)
        st.markdown(advice)
    else:
        st.warning("Please enter a valid height.")
