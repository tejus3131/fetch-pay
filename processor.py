from uagents import Agent, Context, Protocol #type: ignore
from uagents.setup import fund_agent_if_low #type: ignore
from uagents.query import query #type: ignore
from uagents.envelope import Envelope #type: ignore
import os
from uagents.network import wait_for_tx_to_complete #type: ignore
from random import randint
from time import sleep

from dotenv import load_dotenv #type: ignore

from models import TransactionRequest, PaymentRequest, PaymentResponse, TransactionResponse, Error
from utils import add_address, remove_address, get_address


load_dotenv()

processor_agent: Agent = Agent(
    name=os.getenv('PROCESSOR_NAME'), 
    seed=os.getenv('PROCESSOR_SECRET'),
    port=os.getenv('PROCESSOR_PORT'),
    endpoint=[f"http://127.0.0.1:{os.getenv('PROCESSOR_PORT')}/submit"]
)

fund_agent_if_low(processor_agent.wallet.address())

@processor_agent.on_event("startup")
async def introduce_agent(ctx: Context) -> None:
    add_address(processor_agent.name, processor_agent.address)

@processor_agent.on_event("shutdown")
async def good_bye(ctx: Context) -> None:
    remove_address(processor_agent.name)

processor = Protocol(name="processor_protocol", version="1.0")

@processor.on_query(model=PaymentRequest, replies={PaymentResponse})
async def query_handler(ctx: Context, sender: str, _query: PaymentRequest) -> None:
    ctx.logger.info(f"Received query from {sender}: {_query}")

    id = None
    while not id:
        id = randint(100000, 999999)
        if ctx.storage.get(id):
            id = None
        else:
            ctx.storage.set(id, None)
            
    await ctx.send(destination=_query.address, message=TransactionRequest(transaction_id=id, wallet=_query.wallet, amount=_query.amount, code=_query.code), timeout=240.0)

    while not ctx.storage.get(id):
        sleep(1)

    if ctx.storage.get(id) == "error":
        await ctx.send(sender, PaymentResponse(success=False, message="Transaction failed"))
        return
    
    print(f"Transaction hash: {ctx.storage.get(id)}")


@processor.on_message(model=TransactionResponse)
async def handle_response(ctx: Context, sender: str, _msg: TransactionResponse) -> None:
    ctx.storage.set(_msg.transaction_id, _msg.hash)


@processor.on_message(model=Error)
async def handle_error(ctx: Context, sender: str, _msg: Error) -> None:
    ctx.storage.set(_msg.transaction_id, "error")

    
processor_agent.include(processor)
 
if __name__ == "__main__":
    processor_agent.run()