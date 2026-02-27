import os, json
from dotenv import load_dotenv
from solcx import compile_source, install_solc
from web3 import Web3

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

WEB3_PROVIDER = os.getenv("WEB3_PROVIDER", "http://127.0.0.1:7545")
PRIVATE_KEY = os.getenv("GANACHE_PRIVATE_KEY")

if not PRIVATE_KEY:
    raise Exception("❌ GANACHE_PRIVATE_KEY missing in .env")

# Load contract source
file_path = os.path.join(os.path.dirname(__file__), "EvidenceLog.sol")
source = open(file_path).read()

# Compile
install_solc('0.8.17')
compiled_sol = compile_source(source, output_values=['abi', 'bin'], solc_version='0.8.17')
contract_id, contract_interface = compiled_sol.popitem()
abi = contract_interface['abi']
bytecode = contract_interface['bin']

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))
if not w3.is_connected():
    raise Exception("❌ Cannot connect to Ganache. Is it running?")

acct = w3.eth.account.from_key(PRIVATE_KEY)
nonce = w3.eth.get_transaction_count(acct.address)
chain_id = w3.eth.chain_id

# Build deployment tx
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
tx = Contract.constructor().build_transaction({
    'from': acct.address,
    'nonce': nonce,
    'gas': 3000000,
    'gasPrice': w3.to_wei('20', 'gwei'),
    'chainId': chain_id
})

# Sign and send
signed_tx = acct.sign_transaction(tx)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print("🚀 Deploying... Transaction Hash:", tx_hash.hex())

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("✅ Contract deployed at:", receipt.contractAddress)

# Save ABI + address
out_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "chain")
os.makedirs(out_dir, exist_ok=True)
open(os.path.join(out_dir, "evidence_abi.json"), "w").write(json.dumps(abi))
open(os.path.join(out_dir, "evidence_address.txt"), "w").write(receipt.contractAddress)

print("📦 Saved ABI and contract address to backend/chain/")
