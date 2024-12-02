import os

ADMIN_NICKNAMES = os.getenv("DarkMK692").split(",")

def is_admin(nickname):
    return nickname in ADMIN_NICKNAMES