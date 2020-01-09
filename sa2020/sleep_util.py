import time
from random import randrange


def animated_sleep(seconds: int):
    animation = "|/-\\"
    for i in range(seconds * 2):
        time.sleep(0.5)
        print(animation[i % len(animation)], end="\r")


def animated_random_sleep(min: int, max: int):
    animated_sleep(randrange(min, max + 1))
