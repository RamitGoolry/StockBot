import os
DEBUG = True if os.environ.get('DEBUG') == '1' else False

RESET = '\033[0m'
RED = '\033[31m'

def log(x, color = RED):
    if DEBUG:
        print(color + x + RESET)