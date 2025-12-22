import os

from dotenv import load_dotenv


class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            load_dotenv()
            cls._instance = super().__new__(cls)
            cls._instance.proxy = os.getenv("PROXY_URL")
            cls._instance.token = os.getenv("TOKEN")
            cls._instance.group_id = os.getenv("GROUP_ID")
        return cls._instance

    def __init__(self):
        pass
