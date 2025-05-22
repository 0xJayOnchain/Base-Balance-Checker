import pandas as pd
from web3 import Web3
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Configuration
RPC_URL = os.getenv("RPC_URL")  # Loaded from .env
BASESCAN_API_KEY = os.getenv("BASESCAN_API_KEY")  # Loaded from .env
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # USDC contract on BASE
USDC_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    }
]
CSV_INPUT = "contracts.csv"  # Input CSV from Dune query
CSV_OUTPUT = "contract_analysis.csv"  # Output CSV

# Validate environment variables
if not RPC_URL or not BASESCAN_API_KEY:
    raise ValueError("RPC_URL or BASESCAN_API_KEY not set in .env file")

# Connect to BASE blockchain
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise Exception("Failed to connect to BASE RPC")

# Initialize USDC contract
usdc_contract = w3.eth.contract(address=USDC_ADDRESS, abi=USDC_ABI)

# Read CSV
df = pd.read_csv(CSV_INPUT)
results = []

# Basescan API functions
def get_contract_code(address):
    url = f"https://api.basescan.org/api?module=contract&action=getsourcecode&address={address}&apikey={BASESCAN_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "1" and data["result"][0]["SourceCode"]:
        return {"type": "source", "code": data["result"][0]["SourceCode"]}
    return {"type": "bytecode", "code": w3.eth.get_code(address).hex()}

def get_contract_events(address):
    url = f"https://api.basescan.org/api?module=logs&action=getLogs&address={address}&topic0=0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef&apikey={BASESCAN_API_KEY}"
    response = requests.get(url)
    data = response.json()
    transfer_events = len(data["result"]) if data["status"] == "1" else 0
    url = f"https://api.basescan.org/api?module=logs&action=getLogs&address={address}&topic0=0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925&apikey={BASESCAN_API_KEY}"
    response = requests.get(url)
    data = response.json()
    approval_events = len(data["result"]) if data["status"] == "1" else 0
    return transfer_events + approval_events == 0

# Process each contract
for index, row in df.iterrows():
    address = row["contract_address"]
    if not w3.is_address(address):
        continue
    address = w3.to_checksum_address(address)
    
    # Check ETH balance
    eth_balance = w3.eth.get_balance(address) / 1e18  # Convert wei to ETH
    
    # Check USDC balance
    usdc_balance = usdc_contract.functions.balanceOf(address).call() / 1e6  # Convert to USDC (6 decimals)
    
    # Only proceed if the contract has non-zero ETH or USDC balance
    if eth_balance > 0 or usdc_balance > 0:
        # Verify non-token status (no Transfer/Approval events)
        is_non_token = get_contract_events(address)
        
        # Get contract code
        code_info = get_contract_code(address)
        
        # Store results
        results.append({
            "contract_address": address,
            "block_time": row["block_time"],
            "tx_hash": row["tx_hash"],
            "creator_address": row["creator_address"],
            "eth_balance": eth_balance,
            "usdc_balance": usdc_balance,
            "is_non_token": is_non_token,
            "code_type": code_info["type"],
            "code": code_info["code"][:100] + "..." if len(code_info["code"]) > 100 else code_info["code"]  # Truncate for CSV
        })

# Save results to CSV
results_df = pd.DataFrame(results)
results_df.to_csv(CSV_OUTPUT, index=False)
print(f"Results saved to {CSV_OUTPUT}")