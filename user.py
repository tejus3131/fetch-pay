from uagents import Agent, Context, Protocol #type: ignore
from uagents.setup import fund_agent_if_low #type: ignore
import os
from dotenv import load_dotenv

from models import TransactionRequest, TransactionResponse, RegisterRequest, RegisterResponse, Error #type: ignore
from utils import get_address, add_user, remove_user, get_port, add_address, remove_address #type: ignore
from uagents.network import wait_for_tx_to_complete #type: ignore


load_dotenv()

class SenderAgent:
    def __init__(self, name, code) -> None:
        self.port = get_port()
        self.agent: Agent = Agent(
            name=name,
            seed=name,
            port=self.port,
            endpoint=[f"http://127.0.0.1:{self.port}/submit"]
        )

        self.agent.storage.set("code", code)

        fund_agent_if_low(self.agent.wallet.address())

        @self.agent.on_event("startup")
        async def introduce_agent(ctx: Context) -> None:
            add_address(name, str(self.agent.address))
            await ctx.send(get_address(os.getenv('ADDRESS_EXCHANGE_NAME')), RegisterRequest(name=name, address=str(self.agent.wallet.address())))

        @self.agent.on_event("shutdown")
        async def good_bye(ctx: Context) -> None:
            remove_address(name)
            remove_user(ctx.storage.get("id"))

        self.protocol = Protocol(name=f"{name}.protocol", version="1.0")

        @self.protocol.on_message(model=Error)
        async def handle_error(ctx: Context, sender: str, _msg: Error) -> None:
            ctx.logger.error(_msg.message)
            exit(1)

        @self.protocol.on_message(model=RegisterResponse)
        async def handle_response(ctx: Context, sender: str, _msg: RegisterResponse) -> None:
            ctx.logger.info(f"USER ID: {_msg.id}")
            add_user(_msg.id, self.port)
            ctx.storage.set("id", _msg.id)

        @self.protocol.on_query(model=TransactionRequest, replies={TransactionResponse})
        async def query_handler(ctx: Context, sender: str, _query: TransactionRequest) -> None:
            ctx.logger.info(f"Received query from {sender}: {_query}")

            if _query.code != ctx.storage.get("code"):
                await ctx.send(sender, TransactionResponse(status=False, message="Invalid code"))
                return

            print(f"Sending {_query.amount} to {_query.wallet}")

            hash = ctx.ledger.send_tokens(
                _query.wallet, _query.amount, os.getenv('DENOM'), self.agent.wallet
            )

            print(f"Transaction hash: {hash.tx_hash}")

            tx_resp = await wait_for_tx_to_complete(hash.tx_hash, ctx.ledger)

            coin_received = tx_resp.events["coin_received"]

            if (
                coin_received["receiver"] == _query.wallet
                and coin_received["amount"] == f"{_query.amount}{os.getenv('DENOM')}"
            ):
                await ctx.send(sender, TransactionResponse(status=True, message="Transaction successful"))
                print("Transaction successful")
            else:
                await ctx.send(sender, TransactionResponse(status=False, message="Transaction failed"))
                print("Transaction failed")

        self.agent.include(self.protocol)

    def run(self) -> None:
        self.agent.run()

if __name__ == "__main__":
    sender = SenderAgent(input("Enter your username: "), input("Enter the security code: "))
    sender.run()
