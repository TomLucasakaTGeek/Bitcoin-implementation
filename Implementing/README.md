# Educational Bitcoin Implementation

A comprehensive, educational implementation of Bitcoin's core concepts in Python. This implementation demonstrates how Bitcoin works under the hood, covering all fundamental concepts you'll need for Summer of Bitcoin.

## 🎯 What This Implementation Covers

### ✅ Implemented Features

1. **Cryptographic Primitives**
   - SHA-256 hashing
   - Double SHA-256 (hash256) - Bitcoin's standard
   - RIPEMD-160 hashing
   - Hash160 (SHA-256 + RIPEMD-160 for addresses)

2. **Wallets & Key Management**
   - ECDSA key pair generation (secp256k1 curve)
   - Bitcoin address generation
   - Digital signatures (signing & verification)
   - Public key cryptography

3. **UTXO Model (Unspent Transaction Output)**
   - UTXO creation and tracking
   - Balance calculation as sum of UTXOs
   - UTXO spending and removal
   - UTXO set management

4. **Transactions**
   - Transaction inputs (spending UTXOs)
   - Transaction outputs (creating new UTXOs)
   - Transaction signing with ECDSA
   - Signature verification
   - Transaction hash calculation
   - Coinbase transactions (mining rewards)

5. **Blocks & Blockchain**
   - Block structure (index, timestamp, transactions, previous hash, nonce)
   - Block hash calculation
   - Blockchain validation
   - Genesis block creation

6. **Mining (Proof of Work)**
   - Nonce discovery
   - Difficulty adjustment
   - Mining reward (coinbase transaction)
   - Hash target validation

7. **Peer-to-Peer Network (Simplified)**
   - Node creation
   - Peer connections
   - Transaction broadcasting
   - Block broadcasting

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Bitcoin Network Layer                    │
│  (Nodes, Peers, Transaction/Block Broadcasting)             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Blockchain Layer                        │
│  (Chain of Blocks, Consensus, Validation)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Transaction Layer                       │
│  (Inputs, Outputs, Signatures, UTXO Management)             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Cryptography Layer                       │
│  (Hashing, Digital Signatures, Key Management)              │
└─────────────────────────────────────────────────────────────┘
```

## 📚 Key Concepts Explained

### 1. UTXO Model

**What is it?**
Bitcoin doesn't track account balances directly. Instead, it tracks "Unspent Transaction Outputs" (UTXOs). Think of UTXOs as individual bills/coins in your physical wallet.

**How it works:**
- When you receive Bitcoin, you get a UTXO
- Your balance = sum of all your UTXOs
- When you spend, you consume entire UTXOs and create new ones
- Change goes back to you as a new UTXO

**Example:**
```
Alice has UTXO: 50 BTC
Alice wants to send 10 BTC to Bob

Transaction:
  Input:  50 BTC UTXO (fully consumed)
  Outputs:
    - 10 BTC to Bob (new UTXO)
    - 40 BTC to Alice (change, new UTXO)
```

### 2. Transactions

**Structure:**
```
Transaction {
  inputs: [
    {
      previous_tx: "hash of transaction containing the UTXO"
      output_index: "which output in that transaction"
      signature: "proves you own this UTXO"
      public_key: "your public key"
    }
  ]
  outputs: [
    {
      amount: "satoshis to send"
      recipient: "recipient's address"
    }
  ]
}
```

**Lifecycle:**
1. Create transaction with inputs (UTXOs to spend) and outputs (new UTXOs)
2. Sign inputs with your private key
3. Broadcast to network
4. Miners include in block
5. UTXO set updated: old UTXOs removed, new ones added

### 3. Digital Signatures

**Why?**
Prove you own a UTXO without revealing your private key.

**How?**
1. Hash the transaction data
2. Sign the hash with your private key → signature
3. Anyone can verify signature using your public key
4. If signature is valid, you must own the private key

**Security:**
- Private key: Keep secret, used for signing
- Public key: Share freely, used for verification
- Address: Derived from public key, identifies you

### 4. Mining & Proof of Work

**What is mining?**
Process of adding new blocks to the blockchain by solving a cryptographic puzzle.

**The Puzzle:**
Find a nonce such that:
```
hash(block_data + nonce) < target
```

Where target = number starting with N zeros (difficulty)

**Example:**
```
Difficulty = 4
Target = 0000ffffffffffffffffffff...

Try nonce = 0: hash = 8a3f2c... ❌
Try nonce = 1: hash = 7b2e1d... ❌
Try nonce = 2: hash = 6c4d3f... ❌
...
Try nonce = 142857: hash = 0000abc... ✅ Found it!
```

**Why?**
- Makes it expensive to add blocks (requires computation)
- Prevents spam and double-spending
- Secures the network through economic incentives

### 5. Blockchain Structure

```
Block N-1              Block N                Block N+1
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ Index: 99    │      │ Index: 100   │      │ Index: 101   │
│ Prev: ...abc │◄─────│ Prev: ...xyz │◄─────│ Prev: ...def │
│ Hash: ...xyz │      │ Hash: ...def │      │ Hash: ...ghi │
│ Nonce: 12345 │      │ Nonce: 67890 │      │ Nonce: 24680 │
│ Txs: [...]   │      │ Txs: [...]   │      │ Txs: [...]   │
└──────────────┘      └──────────────┘      └──────────────┘
```

**Immutability:**
If you change block N:
- Its hash changes
- Block N+1's "previous hash" is now invalid
- Must re-mine block N+1
- But that changes N+1's hash
- Must re-mine N+2, N+3, ... all the way to the tip
- Nearly impossible if the chain is long

## 🚀 Running the Code

### Prerequisites

```bash
pip install ecdsa --break-system-packages
```

### Run the demonstration

```bash
python bitcoin_implementation.py
```

### Expected Output

You'll see:
1. Wallet creation with addresses
2. Blockchain initialization
3. Mining demonstration with Proof of Work
4. Transaction creation and signing
5. UTXO updates
6. Balance calculations
7. Blockchain validation
8. P2P network simulation

## 📖 Learning Path

### Beginner Level
1. Start by reading the `Wallet` class - understand key generation
2. Look at `Transaction` and `TxOutput` - understand UTXO model
3. Trace through the main() function to see everything in action

### Intermediate Level
1. Study the `mine_block()` function - understand Proof of Work
2. Examine `UTXOSet` - understand how balances are calculated
3. Look at transaction validation logic

### Advanced Level
1. Modify difficulty and observe mining time changes
2. Implement transaction fees (fee = input_sum - output_sum)
3. Add merkle tree implementation for transactions
4. Implement SPV (Simplified Payment Verification)

## 🔍 Code Walkthrough

### Creating a Transaction

```python
# 1. Get sender's UTXOs
utxos = blockchain.utxo_set.get_utxos_for_address(alice.address)
tx_hash, output_idx, utxo = utxos[0]

# 2. Create input (spending the UTXO)
tx_input = TxInput(
    prev_tx_hash=tx_hash,
    prev_output_index=output_idx
)

# 3. Create outputs (who gets the money)
tx_outputs = [
    TxOutput(amount=10_00000000, recipient_address=bob.address),
    TxOutput(amount=40_00000000, recipient_address=alice.address)  # change
]

# 4. Create and sign transaction
tx = Transaction(inputs=[tx_input], outputs=tx_outputs)
tx.sign_inputs(alice_wallet, blockchain.utxo_set)

# 5. Add to blockchain
blockchain.add_transaction(tx)
```

### Mining a Block

```python
# 1. Miner creates coinbase transaction (reward)
coinbase_tx = create_coinbase_transaction(miner_address, block_height)

# 2. Include pending transactions
transactions = [coinbase_tx] + pending_transactions

# 3. Create block
block = Block(
    index=len(chain),
    timestamp=time.time(),
    transactions=transactions,
    previous_hash=previous_block.hash
)

# 4. Mine (find valid nonce)
block.mine_block(difficulty=4)

# 5. Add to chain and update UTXO set
chain.append(block)
for tx in transactions:
    utxo_set.update_with_transaction(tx)
```

## 🎓 Bitcoin Concepts Quiz

Test your understanding:

1. **What is a UTXO?**
   - An unspent output from a previous transaction that can be used as input

2. **How is your balance calculated?**
   - Sum of all UTXOs belonging to your address

3. **What does signing a transaction prove?**
   - You own the private key corresponding to the address that owns the UTXO

4. **What is the purpose of mining?**
   - Secure the network, prevent double-spending, add new blocks

5. **Why is the blockchain immutable?**
   - Each block references the previous block's hash; changing history requires re-mining all subsequent blocks

## 🔧 Extending This Implementation

### Easy Extensions
- [ ] Transaction fees (difference between inputs and outputs goes to miner)
- [ ] Transaction mempool with priority queue
- [ ] Block size limits
- [ ] Multiple signatures (multisig)

### Medium Extensions
- [ ] Merkle trees for transaction verification
- [ ] Simplified Payment Verification (SPV)
- [ ] Network difficulty adjustment algorithm
- [ ] Segregated Witness (SegWit) structure

### Hard Extensions
- [ ] Script execution engine (Bitcoin Script)
- [ ] P2PKH, P2SH address types
- [ ] Lightning Network payment channels
- [ ] Full P2P networking with socket connections

## 📚 Recommended Resources

### Books
- "Mastering Bitcoin" by Andreas Antonopoulos
- "Grokking Bitcoin" by Kalle Rosenbaum
- "Programming Bitcoin" by Jimmy Song

### Online
- Bitcoin Developer Documentation: https://developer.bitcoin.org/
- Bitcoin Improvement Proposals (BIPs): https://github.com/bitcoin/bips
- Bitcoin Wiki: https://en.bitcoin.it/

### Videos
- Chaincode Labs Seminars
- MIT Bitcoin Course
- Andreas Antonopoulos YouTube channel

## ⚠️ Important Notes

This is an **educational implementation** for learning purposes. It simplifies many aspects:

**Simplifications:**
- No real P2P networking (uses simulated nodes)
- Simplified scripting (real Bitcoin uses Script language)
- No Merkle trees (important for SPV)
- Simplified address format (real Bitcoin uses Base58Check)
- No network protocol messages (version, verack, etc.)
- No transaction relay or block propagation logic
- Single difficulty (real Bitcoin adjusts every 2016 blocks)

**DO NOT use this for:**
- Production systems
- Real money
- Security-critical applications

**DO use this for:**
- Learning Bitcoin internals
- Understanding UTXO model
- Preparing for Summer of Bitcoin
- Building your own cryptocurrency projects
- Teaching blockchain concepts

## 💡 Summer of Bitcoin Preparation

This implementation covers key concepts you'll encounter:

✅ UTXO model and management
✅ Transaction structure and validation
✅ Digital signatures with ECDSA
✅ Proof of Work mining
✅ Blockchain validation
✅ P2P network basics (simplified)

**Additional Topics to Study:**
- Bitcoin Script and opcodes
- Merkle trees and SPV
- SegWit and Taproot
- Lightning Network
- Bitcoin Core codebase
- BIP proposals

## 🤝 Contributing

This is an educational project. Feel free to:
- Add more features
- Improve documentation
- Fix bugs
- Add tests
- Create tutorials

## 📄 License

MIT License - Free to use for learning and education

## 🎉 Acknowledgments

Inspired by:
- Bitcoin Whitepaper by Satoshi Nakamoto
- "Mastering Bitcoin" by Andreas Antonopoulos
- Bitcoin Core implementation
- Summer of Bitcoin program

---

**Happy Learning! 🚀**

Remember: The best way to learn is by doing. Modify this code, break things, fix them, and build on top of it!
