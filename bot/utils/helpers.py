import os

ADMIN_NICKNAMES = os.getenv("ADMIN_NICKNAMES").split(",")

def is_admin(nickname):
    return nickname in ADMIN_NICKNAMES