
import json
from dotenv import load_dotenv
import os

load_dotenv()

AGENTS = r"X:/projects/fetch-pay/data/address.json"
USERS = r"X:/projects/fetch-pay/data/users.json"

def add_address(name: str, address: str) -> None:
    with open(AGENTS, 'r+') as file:
        data = json.load(file)
        data[name] = address
        file.seek(0)
        json.dump(data, file)
        file.truncate()

def remove_address(name: str) -> None:
    with open(AGENTS, 'r+') as file:
        data = json.load(file)
        del data[name]
        file.seek(0)
        json.dump(data, file)
        file.truncate()

def get_address(name: str | None) -> str:
    with open(AGENTS, 'r') as file:
        data = json.load(file)
        if name in data.keys():
            return data[name]
    raise ValueError(f"No agent named {name}")

def add_user(id: str, port: int) -> None:
    with open(USERS, 'r+') as file:
        data = json.load(file)
        data[id] = port
        file.seek(0)
        json.dump(data, file)
        file.truncate()

def remove_user(id: str) -> None:
    with open(USERS, 'r+') as file:
        data = json.load(file)
        del data[id]
        file.seek(0)
        json.dump(data, file)
        file.truncate()

def get_port() -> int:
    port = int(os.getenv('SENDER_PORT', '0'))
    if port == 0:
        raise ValueError("SENDER_PORT not set in .env")
    
    with open(USERS, 'r+') as file:
        data = json.load(file)
        while True:
            if port in data.values():
                port += 1
            else:
                break
    
    return port