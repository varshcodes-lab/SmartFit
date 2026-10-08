import random

def get_iot_data():
    """
    Simulates smart gym IoT sensor data
    """
    return {
        "heart_rate": random.randint(70, 150),
        "calories_burned": random.randint(100, 600),
        "steps": random.randint(1000, 8000)
    }
