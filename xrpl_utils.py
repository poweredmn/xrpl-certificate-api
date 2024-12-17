import hashlib
import os

from dotenv import load_dotenv
from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.asyncio.transaction import sign_and_submit
from xrpl.models import Memo
from xrpl.models.requests import AccountTx
from xrpl.models.transactions import AccountSet
from xrpl.wallet import Wallet

load_dotenv()

SOURCE_SECRET = os.getenv("SOURCE_SECRET")
JSON_RPC_ENDPOINT = os.getenv("JSON_RPC_ENDPOINT")

wallet = Wallet.from_secret(SOURCE_SECRET)
async_json_rpc_client = AsyncJsonRpcClient(JSON_RPC_ENDPOINT)


def calculate_hash(file_content: bytes) -> str:
    """Calculates SHA-256 hash for the given file content."""
    return hashlib.sha256(file_content).hexdigest().upper()


async def submit_payment_transaction(hash_hex: str):
    payment = AccountSet(
        account=wallet.address,
        fee="10000",
        memos=[Memo(
            memo_type="48617368",
            memo_data=hash_hex.encode('utf-8').hex()
        )]
    )

    response = await sign_and_submit(payment, async_json_rpc_client, wallet, check_fee=False)

    return {
        "transactionResult": response.result.get("engine_result"),
        "resultMessage": response.result.get("engine_result_message")
    }


async def check_hash_in_state(hash_hex: str):
    response = await async_json_rpc_client.request(AccountTx(
        account=wallet.address,
        ledger_index_max=-1,
    ))

    result_values = response.result.values()
    transactions = list(result_values)[4]

    matching_tx = next(
        (tx for tx in transactions
         if 'Memos' in tx['tx']
         and tx['tx']['Memos'][0]['Memo']['MemoData'] == hash_hex.encode('utf-8').hex()),
        None
    )

    if matching_tx:
        return {
            "status": "success",
            "message": "Hash found in transaction memos.",
            "timestamp": matching_tx['tx'].get('date'),
        }
    else:
        return {
            "status": "not_found",
            "message": "Hash not found in transaction memos."
        }
