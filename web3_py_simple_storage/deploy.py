import json

from solcx import compile_standard
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    },
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol['contracts']['SimpleStorage.sol']['SimpleStorage']['evm']['bytecode']['object']
abi = compiled_sol['contracts']['SimpleStorage.sol']['SimpleStorage']['abi']

w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/438e116d108d415ca0bceddb87b2f831"))
chain_id = 4
my_address = "0x0876dC9150dB8672B45502262A6173296d68e2a7"
private_key = os.getenv("PRIVATE_KEY")

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

nonce = w3.eth.getTransactionCount(my_address)

transaction = SimpleStorage.constructor().buildTransaction(
    {"gasPrice": w3.eth.gas_price, "chainId": chain_id, "from": my_address, "nonce": nonce}
)

signed_tx = w3.eth.account.sign_transaction(transaction, private_key)

tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(simple_storage.functions.retrieve().call())

store_transaction = simple_storage.functions.store(15).buildTransaction(
    {"gasPrice": w3.eth.gas_price, "chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)
signed_store_tx = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)
send_store_tx = w3.eth.sendRawTransaction(signed_store_tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)

print(simple_storage.functions.retrieve().call())
