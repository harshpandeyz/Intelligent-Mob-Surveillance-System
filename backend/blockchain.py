import os
import json
import hashlib
from dotenv import load_dotenv
from web3 import Web3

# Load environment
load_dotenv()

WEB3_PROVIDER = os.getenv("WEB3_PROVIDER", "http://127.0.0.1:7545")
PRIVATE_KEY = os.getenv("GANACHE_PRIVATE_KEY")

CHAIN_DIR = os.path.join(os.path.dirname(__file__), "chain")
ABI_PATH = os.path.join(CHAIN_DIR, "evidence_abi.json")
ADDR_PATH = os.path.join(CHAIN_DIR, "evidence_address.txt")

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER))
acct = w3.eth.account.from_key(PRIVATE_KEY)

with open(ABI_PATH, 'r') as f:
    ABI = json.load(f)

CONTRACT_ADDRESS = open(ADDR_PATH).read().strip()
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)


def compute_sha256_file(path):
    """Compute SHA256 hash of a file and return hex string"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def log_event_on_chain(hash_hex: str, metadata: str, enc_file_path: str = None):
    """
    Store event hash + metadata on blockchain.
    If hash_hex is invalid, try regenerating from enc_file_path if provided.
    """
    if hash_hex.startswith("0x"):
        hash_hex = hash_hex[2:]

    try:
        hash_bytes = bytes.fromhex(hash_hex)
    except ValueError:
        if enc_file_path and os.path.exists(enc_file_path):
            # regenerate hash from encrypted file
            hash_hex = compute_sha256_file(enc_file_path)
            hash_bytes = bytes.fromhex(hash_hex)
        else:
            raise ValueError(f"Invalid hex hash received and no valid file to regenerate: {hash_hex}")

    # Build transaction
    nonce = w3.eth.get_transaction_count(acct.address)
    tx = contract.functions.logEvent(hash_bytes, metadata).build_transaction({
        'from': acct.address,
        'nonce': nonce,
        'gas': 500000,
        'gasPrice': w3.to_wei('20', 'gwei')
    })

    # Sign transaction
    signed = acct.sign_transaction(tx)

    # Send transaction (Web3.py v6 uses snake_case)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

    # Wait for receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return receipt.transactionHash.hex()
