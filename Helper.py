from Config import DEBUG_MODE

def debug(message, level=0, ending="\n"):
    if level <= DEBUG_MODE:
        print(message, end=ending)