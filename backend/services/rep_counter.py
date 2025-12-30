

def count_reps(exercise: str, angles: list):
    """
    Generic rep counter dispatcher
    angles = list of angle values over frames
    """
    if exercise == "squat":
        return count_squat_reps(angles)

    elif exercise == "pushup":
        return count_pushup_reps(angles)

    elif exercise == "pullup":
        return count_pullup_reps(angles)

    return 0




def count_squat_reps(knee_angles):
    reps = 0
    state = "up"

    for angle in knee_angles:
        if angle < 90 and state == "up":
            state = "down"
        elif angle > 160 and state == "down":
            reps += 1
            state = "up"

    return reps




def count_pushup_reps(elbow_angles):
    reps = 0
    state = "up"

    for angle in elbow_angles:
        if angle < 90 and state == "up":
            state = "down"
        elif angle > 160 and state == "down":
            reps += 1
            state = "up"

    return reps




def count_pullup_reps(elbow_angles):
    reps = 0
    state = "down"

    for angle in elbow_angles:
        if angle < 80 and state == "down":
            state = "up"
        elif angle > 150 and state == "up":
            reps += 1
            state = "down"

    return reps
