import os
import json
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ GROQ_API_KEY not found. Add it to .env file")
    st.stop()

client = Groq(api_key=api_key)

MEMORY_FILE = "gym_memory.json"
PROFILE_FILE = "user_profile.json"
WEIGHT_FILE = "weight.json"

# ------------------ FILE HANDLING ------------------

def load_json(file, default):
    if not os.path.exists(file):
        return default
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

memory = load_json(MEMORY_FILE, {"logs": []})
profile = load_json(PROFILE_FILE, {"name": "", "age": "", "weight": "", "goal": ""})
weights = load_json(WEIGHT_FILE, [])

# ------------------ AI ------------------

def ask_ai(user_input):
    system_prompt = f"""
    You are a professional gym trainer AI.

    User Profile:
    {profile}

    Workout History:
    {memory["logs"]}

    Rules:
    - Give short, powerful answers
    - Suggest sets, reps, rest
    - Motivate like a real coach
    """

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return chat.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# ------------------ UI ------------------

st.set_page_config(page_title="AI Gym Trainer Pro", layout="wide")

st.title("🏋️ AI Gym Trainer PRO")

# Sidebar
st.sidebar.header("👤 Profile")

profile["name"] = st.sidebar.text_input("Name", profile["name"])
profile["age"] = st.sidebar.text_input("Age", profile["age"])
profile["weight"] = st.sidebar.text_input("Weight", profile["weight"])
profile["goal"] = st.sidebar.selectbox(
    "Goal",
    ["Muscle Gain", "Fat Loss", "Fitness"],
    index=0
)

if st.sidebar.button("Save Profile"):
    save_json(PROFILE_FILE, profile)
    st.sidebar.success("Saved!")

# ------------------ WEIGHT TRACKER ------------------

st.sidebar.subheader("⚖️ Track Weight")

new_weight = st.sidebar.number_input("Enter weight", min_value=0.0)

if st.sidebar.button("Add Weight"):
    weights.append({"date": str(datetime.now()), "weight": new_weight})
    save_json(WEIGHT_FILE, weights)
    st.sidebar.success("Weight added!")

# ------------------ DASHBOARD ------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Workout Logs")
    for log in memory["logs"][-10:]:
        st.write("•", log)

with col2:
    st.subheader("📈 Weight Progress")
    if weights:
        chart_data = {
            "Weight": [w["weight"] for w in weights]
        }
        st.line_chart(chart_data)
    else:
        st.write("No data yet")

# ------------------ CHAT ------------------

st.subheader("💬 AI Coach")

if "chat" not in st.session_state:
    st.session_state.chat = []

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask your trainer...")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})

    # smart logging
    if any(word in user_input.lower() for word in ["did", "kg", "reps"]):
        memory["logs"].append(user_input)
        save_json(MEMORY_FILE, memory)

    reply = ask_ai(user_input)

    st.session_state.chat.append({"role": "assistant", "content": reply})
    st.rerun()