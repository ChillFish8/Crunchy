import base64
import random
from string import ascii_letters, punctuation

characters = list(ascii_letters) + list(punctuation)


def get_id():
    random.shuffle(characters)
    file_name = "".join(characters[:16])
    new = str(base64.urlsafe_b64encode(file_name.encode("utf-8")), "utf-8").replace("=", "")
    return new
