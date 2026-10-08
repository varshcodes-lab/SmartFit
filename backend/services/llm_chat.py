import os
from openai import OpenAI

def llm_chat(message: str):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {
            "reply": "❌ OPENAI_API_KEY not set. Please configure environment variable."
        }

    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=message
        )

        return {
            "reply": response.output_text
        }

    except Exception as e:
        return {
            "reply": f"⚠️ AI service error: {str(e)}"
        }
