# Base Contract Analyzer

This project analyzes smart contracts on the BASE blockchain, identifying non-token contracts (not ERC-20 or ERC-721) with non-zero ETH or USDC balances. It uses a Dune Analytics SQL query to fetch recently created contracts and a Python script to process the data, check balances, verify non-token status, and retrieve contract code.

## Overview

- **Dune Query**: Fetches contract creation data from the BASE blockchain (contracts created between 48 and 24 hours ago).
- **Python Script**: Processes the query results, checks ETH and USDC balances, filters for non-token contracts, and retrieves contract code (source or bytecode).
- **Output**: A CSV file (`contract_analysis.csv`) containing contracts with non-zero balances, their non-token status, and contract code.

## Prerequisites

- **Python 3.10+**: Ensure Python is installed. Check with `python3 --version`.
- **Dune Analytics Account**: Required to run the SQL query. Sign up at [dune.com](https://dune.com).
- **API Keys**:
  - **BASE RPC URL**: Get a free RPC URL from [Alchemy](https://www.alchemy.com) or [Infura](https://infura.io) for BASE mainnet.
  - **Basescan API Key**: Sign up at [basescan.org](https://basescan.org/register) and get an API key under "My API Keys".
- **Dependencies**: Listed in `requirements.txt`.

## Setup

1. **Clone the Repository**:

```
git clone https://github.com/yourusername/base-contract-analyzer.git
cd base-contract-analyzer
```

2. **Set Up a Virtual Environment**:

```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**:

```
pip install -r requirements.txt
```

This installs `pandas`, `web3`, `requests`, and `python-dotenv`.

4. **Configure Environment Variables**:
   - Create a `.env` file in the root directory:

```
touch .env
```

   - Add your API keys:

```
RPC_URL=https://base-mainnet.g.alchemy.com/v2/your-alchemy-api-key
BASESCAN_API_KEY=your-basescan-api-key
```

   - Replace placeholders with your actual keys. Do not commit `.env` to Git (it’s in `.gitignore`).

## Usage

### Step 1: Run the Dune Query

1. **Open Dune Analytics**:
   - Go to [dune.com](https://dune.com) and sign in.
   - Click "New Query".

2. **Paste the Query**:
   - Copy the SQL query from `baseRecentContractCreations.sql`:

```
SELECT
  t.address AS contract_address,
  t.block_time,
  t.tx_hash,
  t."from" AS creator_address
FROM base.creation_traces AS t
WHERE
  t.block_time >= CURRENT_TIMESTAMP - INTERVAL '48' hour
  AND t.block_time < CURRENT_TIMESTAMP - INTERVAL '24' hour
ORDER BY
  t.block_time DESC
LIMIT 25
```

   - Paste it into the Dune SQL editor.
   - Set the dataset to "Base" via the dropdown.

3. **Run and Export**:
   - Click "Run" to execute the query.
   - Export the results as `contracts.csv` and save it in the repository root directory.
   - Note: If your Dune plan doesn’t allow CSV exports, manually copy the results into a CSV file (columns: `contract_address`, `block_time`, `tx_hash`, `creator_address`).

### Step 2: Run the Python Script

1. **Ensure Virtual Environment is Active**:

```
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Run the Script**:

```
python check_contracts.py
```

   - The script reads `contracts.csv`, checks ETH and USDC balances, verifies non-token status, and retrieves contract code.
   - It outputs `contract_analysis.csv` with contracts that have non-zero balances.

3. **Check the Output**:
   - Open `contract_analysis.csv`. It contains:
     - `contract_address`, `block_time`, `tx_hash`, `creator_address`
     - `eth_balance`: ETH balance in ETH.
     - `usdc_balance`: USDC balance in USDC.
     - `is_non_token`: `True` if the contract doesn’t emit `Transfer`/`Approval` events.
     - `code_type`: `source` (verified) or `bytecode` (unverified).
     - `code`: Truncated contract code.

## File Structure

- base-contract-analyzer/
  - check_contracts.py          # Python script to analyze contracts
  - baseRecentContractCreations.sql  # Dune SQL query
  - contracts.csv               # Input CSV from Dune query (not tracked)
  - contract_analysis.csv       # Output CSV with results (not tracked)
  - .env                        # Environment variables (not tracked)
  - .env.example                # Example .env file
  - .gitignore                  # Git ignore file
  - requirements.txt            # Python dependencies
  - README.md                   # This file

## Notes

- **Rate Limits**: Basescan API has a 5 requests/second limit for free keys. If rate-limited, add a delay in the script:

```
import time
# Before get_contract_events(address):
time.sleep(0.2)
```

- **Dynamic Balances**: Balances may change over time. Re-run the script periodically to update results.
- **Proxy Contracts**: Some contracts may be proxies, which often don’t hold funds directly. Check the implementation contract on Basescan if needed.

## Ethical Usage

- **Public Data**: This project uses public blockchain data via RPC providers and Basescan API, complying with BASE’s terms as of May 22, 2025.
- **No Interaction**: The script only reads balances and code, making no state-modifying calls, ensuring no disruption to the blockchain.
- **Research Purpose**: Intended for auditing and analysis, not malicious purposes.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with any improvements or bug fixes.