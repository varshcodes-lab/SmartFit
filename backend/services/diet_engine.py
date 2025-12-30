def calculate_bmi(weight, height):
    return weight / (height ** 2)

def recommend_diet(bmi):
    if bmi < 18.5:
        return "High Protein Muscle Gain Diet"
    elif bmi <= 24.9:
        return "Balanced Fitness Diet"
    else:
        return "Low Carb Weight Loss Diet"
