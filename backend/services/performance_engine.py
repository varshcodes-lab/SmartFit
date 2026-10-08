def calculate_performance(correct_reps, total_reps, duration_minutes):
    if total_reps == 0 or duration_minutes == 0:
        return 0

    accuracy = correct_reps / total_reps
    speed = total_reps / duration_minutes

    score = (accuracy * 70) + (speed * 4)
    return round(score, 2)
