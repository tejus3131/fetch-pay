
from uagents import Model #type: ignore
from typing import Optional

class RegisterRequest(Model):
    name: str
    address: str

class RegisterResponse(Model):  
    id: str

class AuthRequest(Model):
    id: str

class AuthResponse(Model):
    name: str

class AddressRequest(Model):
    id: str

class AddressResponse(Model):
    address: str
    wallet: str

class Error(Model):
    message: str

class TransactionRequest(Model):
    wallet: str
    amount: int
    code: str

class TransactionResponse(Model):
    status: bool
    message: str