# Quick Start Guide

Get up and running with the Bitcoin implementation in 5 minutes!

## Installation

```bash
# Clone or download this repository
cd bitcoin-implementation

# No dependencies needed! Uses only Python standard library
python --version  # Should be Python 3.7+
```

## Your First Bitcoin Transaction

### Step 1: Run the Demo

```bash
python bitcoin_implementation.py
```

You'll see:
- ✅ Wallets created
- ⛏️ Blocks being mined
- 💸 Transactions being processed
- 🔍 Blockchain validation

### Step 2: Understand What Happened

The demo just:
1. Created 3 wallets (Alice, Bob, Charlie)
2. Mined a block giving Alice 50 BTC
3. Alice sent 10 BTC to Bob
4. Charlie mined that transaction (earning 50 BTC reward)
5. Validated the entire blockchain

### Step 3: Create Your Own Transaction

```python
from bitcoin_implementation import *

# Create blockchain and wallets
blockchain = Blockchain()
alice = Wallet()
bob = Wallet()

# Mine initial block to give Alice coins
blockchain.mine_pending_transactions(alice.address)

print(f"Alice has: {blockchain.get_balance(alice.address) / 100_000_000} BTC")

# Get Alice's UTXO
utxos = blockchain.utxo_set.get_utxos_for_address(alice.address)
tx_hash, output_idx, utxo = utxos[0]

# Create transaction: Alice sends 5 BTC to Bob
tx_input = TxInput(prev_tx_hash=tx_hash, prev_output_index=output_idx)
tx_outputs = [
    TxOutput(amount=5_00000000, recipient_address=bob.address),
    TxOutput(amount=45_00000000, recipient_address=alice.address)  # change
]

tx = Transaction(inputs=[tx_input], outputs=tx_outputs)
tx.sign_inputs(alice, blockchain.utxo_set)

# Add and mine
blockchain.add_transaction(tx)
blockchain.mine_pending_transactions(alice.address)

print(f"Alice now has: {blockchain.get_balance(alice.address) / 100_000_000} BTC")
print(f"Bob now has: {blockchain.get_balance(bob.address) / 100_000_000} BTC")
```

## Key Concepts in 60 Seconds

### 💰 UTXO (Unspent Transaction Output)
Think of UTXOs as physical bills in your wallet. Your balance is the sum of all your bills.

**Example:**
```
You have: [10 BTC, 20 BTC, 15 BTC]
Your balance: 45 BTC
```

### 💸 Transactions
To send money, you must spend entire UTXOs and create new ones.

**Example:**
```
I want to send 25 BTC but only have bills of [10, 20, 15]
I spend the 20 and 10 bills (30 BTC total)
Output 1: 25 BTC to recipient
Output 2: 5 BTC back to me (change)
```

### ⛏️ Mining
Finding a nonce that makes the block hash start with zeros.

**Example:**
```
Target: 0000...
Try nonce=0: hash=8a3f... ❌
Try nonce=1: hash=7b2e... ❌
Try nonce=12857: hash=0000a2b... ✅ Found it!
```

### 🔗 Blockchain
Chain of blocks where each block points to the previous one.

**Example:**
```
Block 1 → Block 2 → Block 3 → Block 4
(hash=abc) (prev=abc) (prev=def) (prev=ghi)
```

## Common Operations

### Create a Wallet
```python
wallet = Wallet()
print(f"Address: {wallet.address}")
```

### Check Balance
```python
balance = blockchain.get_balance(wallet.address)
print(f"Balance: {balance / 100_000_000} BTC")
```

### Mine a Block
```python
block = blockchain.mine_pending_transactions(miner_address)
print(f"Block #{block.index} mined!")
```

### View Blockchain
```python
blockchain.print_chain()
```

### Validate Blockchain
```python
is_valid = blockchain.is_chain_valid()
print(f"Valid: {is_valid}")
```

## Understanding Units

Bitcoin uses **satoshis** as the smallest unit:
```
1 BTC = 100,000,000 satoshis
0.5 BTC = 50,000,000 satoshis
0.00000001 BTC = 1 satoshi
```

In code:
```python
amount = 1_00000000  # 1 BTC
amount = 50_00000000  # 50 BTC
amount = 123456789  # 1.23456789 BTC
```

## Troubleshooting

### "Transaction invalid"
- Check that UTXOs exist and are unspent
- Verify signatures are correct
- Ensure input sum >= output sum

### "Mining taking forever"
- Lower the difficulty: `blockchain.difficulty = 2`
- Difficulty 4 ≈ few seconds
- Difficulty 5 ≈ tens of seconds
- Difficulty 6+ ≈ minutes

### "UTXO not found"
- Make sure you've mined at least one block
- Check that you're using the correct tx_hash and index
- Verify the UTXO hasn't been spent

## Next Steps

1. **Read the README.md** - Understand the architecture
2. **Try the EXERCISES.md** - Build new features
3. **Explore the code** - See how it all works
4. **Build something** - Create your own blockchain project

## Useful Code Snippets

### See All UTXOs
```python
for key, utxo in blockchain.utxo_set.utxos.items():
    print(f"{key}: {utxo.amount / 100_000_000} BTC → {utxo.recipient_address[:10]}...")
```

### See All Blocks
```python
for block in blockchain.chain:
    print(f"Block {block.index}: {len(block.transactions)} txs, hash={block.hash[:10]}...")
```

### Create Multiple Transactions
```python
transactions = []
for i in range(5):
    # Create transaction i
    tx = create_transaction(...)
    transactions.append(tx)
    blockchain.add_transaction(tx)

# Mine all at once
blockchain.mine_pending_transactions(miner_address)
```

### Simulate Network
```python
# Create nodes
node1 = Node("Node-1")
node2 = Node("Node-2")

# Connect them
node1.connect_to_peer(node2)

# Node1 mines
node1.mine()

# Automatically broadcasts to node2
```

## FAQ

**Q: Is this production-ready?**
A: No! This is educational. Real Bitcoin is much more complex.

**Q: Can I use this for real money?**
A: Absolutely not. This is a learning tool only.

**Q: What's missing compared to real Bitcoin?**
A: Bitcoin Script, Merkle trees, proper P2P, SegWit, Taproot, and much more.

**Q: Should I learn this before Summer of Bitcoin?**
A: Yes! Understanding these concepts will help you tremendously.

**Q: How do I modify the code?**
A: Fork it, experiment, break things, learn! That's the point.

## Need Help?

- Check the README.md for detailed explanations
- Look at the code comments
- Try the EXERCISES.md for practice problems
- Read Bitcoin documentation: https://developer.bitcoin.org/

Happy learning! 🎓
