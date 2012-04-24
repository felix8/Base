def enough_confidence(confidence, threshold):
    actual = 0
    for val in confidence:
        actual = actual + val
    
    if actual > 2:
        return 1
    else:
        return 0