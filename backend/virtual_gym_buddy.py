def chat_response(message: str):
    """
    Simple virtual gym buddy chatbot response
    """
    message = message.lower()

    if "diet" in message:
        return "Maintaining a balanced diet is key to achieving your fitness goals."
    elif "workout" in message:
        return "Consistency in workouts is more important than intensity."
    elif "motivation" in message:
        return "Stay consistent and trust the process. Progress takes time."
    else:
        return "I'm your virtual gym buddy. Ask me about workouts, diet, or motivation."
