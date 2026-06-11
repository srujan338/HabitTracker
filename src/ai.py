import requests
import json
import streamlit as st

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3" # Defaulting to llama3, can be changed

def call_ollama(prompt, system_prompt=""):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            return f"Error: Ollama returned status {response.status_code}"
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"

def get_habit_recommendations(user_answers):
    system_prompt = (
        "You are an expert habit coach. Based on the user's survey answers, "
        "suggest 3-5 specific habits they should adopt or kill. "
        "Keep the suggestions concise and actionable. "
        "Format the output as a clean list with emojis."
    )
    prompt = f"User Survey Answers: {json.dumps(user_answers)}"
    return call_ollama(prompt, system_prompt)

def get_companion_chat(user_data, message):
    system_prompt = (
        "You are 'Draco', a baby dragon pet. "
        "Your mission is to grow by being fed with the user's completed habit 'missions'. "
        "Be playful, protective, and sometimes hungry for more XP. "
        "Use dragon-themed language (e.g., 'roar', 'spark', 'treasure'), "
        "and react to habit completion. You speak English and Hindi."
    )
    prompt = f"User Stats: {user_data}\nUser Message: {message}"
    return call_ollama(prompt, system_prompt)
