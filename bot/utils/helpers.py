import os
from bot.settings import config

def is_admin(nickname):
    return nickname in config.ADMIN_NICKNAMES.split()
