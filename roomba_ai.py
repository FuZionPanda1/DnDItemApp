import random

detect_hit = False
phrases = ["You bitch!", "Kill yourself."]
angry_mode = False
random_element = random.choice(phrases)
isHit = True
num_hits = 0
isOn = True

while isOn == True:
    if isHit == True:
        angry_mode = True
        random_element = random.choice(phrases)
        num_hits = num_hits + 1
    if angry_mode == True:
        {
            print(f"{random_element}")
        }