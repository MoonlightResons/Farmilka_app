import random
import string


def generate_code(length=16):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    code = ''.join(random.choice(characters) for _ in range(length))
    return code