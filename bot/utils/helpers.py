import os
from settings import config

def is_admin(nickname):
    return nickname in config.ADMIN_NICKNAMES.split()
