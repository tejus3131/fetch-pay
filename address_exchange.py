from uagents import Agent, Context, Protocol  # type: ignore
from uagents.setup import fund_agent_if_low #type: ignore
import os
from dotenv import load_dotenv  # type: ignore
from random import randint
from utils import add_address, remove_address, get_address
from models import RegisterRequest, RegisterResponse, AuthRequest, AuthResponse, AddressRequest, AddressResponse, Error

load_dotenv()

address_exchange_agent: Agent = Agent(
    name=os.getenv('ADDRESS_EXCHANGE_NAME'),
    seed=os.getenv('ADDRESS_EXCHANGE_SECRET'),
    port=os.getenv('ADDRESS_EXCHANGE_PORT'),
    endpoint=[f"http://127.0.0.1:{os.getenv('ADDRESS_EXCHANGE_PORT')}/submit"]
)

fund_agent_if_low(address_exchange_agent.wallet.address())

@address_exchange_agent.on_event("startup")
async def introduce_address_exchange_agent(ctx: Context) -> None:

    add_address(address_exchange_agent.name, address_exchange_agent.address)

    if not ctx.storage.get("users"):
        ctx.storage.set("users", {})


@address_exchange_agent.on_event("shutdown")
async def good_bye(ctx: Context) -> None:
    remove_address(address_exchange_agent.name)


exchange_protocol = Protocol(
    name="authenticator_protocol", version="1.0")


@exchange_protocol.on_message(model=RegisterRequest, replies={RegisterResponse, Error})
async def handle_request(ctx: Context, sender: str, _msg: RegisterRequest) -> None:
    ctx.logger.info(f"Received message from {sender} with id {_msg.address}")

    users = ctx.storage.get("users")
    if _msg.address in users.keys():
        await ctx.send(sender, Error(message="Address already registered"))
    else:
        id = None
        while not id:
            id = randint(1000000000, 9999999999)
            if id in users.keys():
                id = None

        id = str(id)
        users[id] = [_msg.name, sender, _msg.address]
        ctx.storage.set("users", users)
        await ctx.send(sender, RegisterResponse(id=id))


@exchange_protocol.on_query(model=AuthRequest, replies={AuthResponse, Error})
async def query_handler(ctx: Context, sender: str, _query: AuthRequest) -> None:
    ctx.logger.info(f"Received query from {sender} with id {_query.id}")
    users = ctx.storage.get("users")
    if _query.id in users.keys():
        await ctx.send(sender, AuthResponse(name=users[_query.id][0]))
    else:
        await ctx.send(sender, Error(message="User not found"))

@exchange_protocol.on_query(model=AddressRequest, replies={AddressResponse, Error})
async def handle_address_request(ctx: Context, sender: str, _msg: AddressRequest) -> None:
    ctx.logger.info(f"Received message from {sender} with id {_msg.id}")
    users = ctx.storage.get("users")
    if _msg.id in users.keys():
        await ctx.send(sender, AddressResponse(address=users[_msg.id][1], wallet=users[_msg.id][2]))
    else:
        await ctx.send(sender, Error(message="User not found"))


address_exchange_agent.include(exchange_protocol)

if __name__ == "__main__":
    address_exchange_agent.run()
