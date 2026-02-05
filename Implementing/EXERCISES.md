# Bitcoin Implementation Exercises

Practice these exercises to deepen your understanding. Solutions are provided at the bottom.

## Exercise 1: Transaction Fees

Currently, miners only receive block rewards. Implement transaction fees.

**Task:**
- Calculate fee as: `fee = sum(inputs) - sum(outputs)`
- Add the fee to the miner's coinbase transaction
- Modify `mine_pending_transactions()` to calculate total fees

**Hint:** Look at the `_validate_transaction()` method to see how input/output sums are calculated.

## Exercise 2: Mempool Priority

Transactions are currently processed first-come-first-served. Implement a priority system.

**Task:**
- Create a `Mempool` class that stores pending transactions
- Prioritize transactions by fee-per-byte
- Modify mining to select highest-fee transactions first

**Hint:** Calculate transaction size as `len(tx.serialize_for_hashing())`.

## Exercise 3: Merkle Tree

Implement a Merkle tree for transactions in a block.

**Task:**
- Create a `calculate_merkle_root()` function
- Build a binary tree from transaction hashes
- Store merkle root in Block
- Verify transactions belong to a block using merkle proof

**Algorithm:**
```
Txs: [A, B, C, D]

Level 0:  Hash(A)  Hash(B)  Hash(C)  Hash(D)
            |         |         |         |
Level 1:    Hash(AB)            Hash(CD)
                 |                  |
Level 2:           Hash(ABCD)  <-- Root
```

## Exercise 4: SPV (Simplified Payment Verification)

Implement lightweight client verification.

**Task:**
- Create a `SPVClient` class that only stores block headers
- Implement `verify_transaction()` using merkle proof
- Client should verify transaction without downloading full blocks

## Exercise 5: Difficulty Adjustment

Bitcoin adjusts difficulty every 2016 blocks to maintain 10-minute block time.

**Task:**
- Track block timestamps
- Calculate average mining time every N blocks
- Adjust difficulty up if blocks are too fast, down if too slow

**Formula:**
```
new_difficulty = old_difficulty * (actual_time / target_time)
```

## Exercise 6: Multiple Inputs

Currently, transactions use single inputs. Support multiple inputs.

**Task:**
- Allow transaction to consume multiple UTXOs
- Sign each input separately
- Verify all signatures

**Example:**
```python
# Spend 3 UTXOs to send 25 BTC
inputs = [
    TxInput(utxo1),  # 10 BTC
    TxInput(utxo2),  # 10 BTC
    TxInput(utxo3),  # 10 BTC
]
outputs = [
    TxOutput(25, bob_address),
    TxOutput(5, alice_address)  # change
]
```

## Exercise 7: Block Size Limit

Add a maximum block size (like Bitcoin's 1MB limit).

**Task:**
- Calculate block size: header + all transactions
- Limit block to MAX_BLOCK_SIZE bytes
- Miners must select transactions that fit

## Exercise 8: Double Spend Prevention

Test that double-spending is prevented.

**Task:**
- Create two transactions spending the same UTXO
- Try to add both to blockchain
- Verify that second transaction is rejected

## Exercise 9: Chain Reorganization

Handle competing chains (blockchain fork).

**Task:**
- If you receive a longer valid chain, replace your chain
- Implement `replace_chain()` method
- Return replaced transactions back to mempool

## Exercise 10: P2P Message Protocol

Implement proper P2P networking.

**Task:**
- Define message types: VERSION, VERACK, TX, BLOCK, GETDATA
- Implement message serialization/deserialization
- Handle peer discovery and connection

## Exercise 11: Wallet Import/Export

Add wallet persistence.

**Task:**
- Implement `wallet.export_to_file(filename)` 
- Implement `Wallet.import_from_file(filename)`
- Support BIP39 mnemonic phrases (12/24 words)

## Exercise 12: Script Engine (Advanced)

Implement a basic Bitcoin Script interpreter.

**Task:**
- Define opcodes: OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG
- Create a stack-based execution engine
- Execute scripts to validate transactions

**Example P2PKH Script:**
```
ScriptPubKey: OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
ScriptSig: <signature> <pubKey>
```

---

## Solutions

### Exercise 1: Transaction Fees (Partial Solution)

```python
def calculate_fee(self, tx: Transaction, utxo_set: UTXOSet) -> int:
    """Calculate transaction fee"""
    total_input = 0
    for inp in tx.inputs:
        utxo_key = f"{inp.prev_tx_hash}:{inp.prev_output_index}"
        if utxo_key in utxo_set.utxos:
            total_input += utxo_set.utxos[utxo_key].amount
    
    total_output = sum(out.amount for out in tx.outputs)
    return total_input - total_output

def mine_pending_transactions(self, miner_address: str) -> Block:
    # Calculate total fees
    total_fees = sum(
        self.calculate_fee(tx, self.utxo_set) 
        for tx in self.pending_transactions
    )
    
    # Create coinbase with reward + fees
    coinbase_tx = create_coinbase_transaction(
        miner_address=miner_address,
        block_height=len(self.chain),
        reward=self.mining_reward + total_fees
    )
    
    # ... rest of the method
```

### Exercise 3: Merkle Tree (Partial Solution)

```python
def calculate_merkle_root(transactions: List[Transaction]) -> str:
    """Calculate merkle root from transaction hashes"""
    if not transactions:
        return "0" * 64
    
    # Start with transaction hashes
    hashes = [tx.tx_hash for tx in transactions]
    
    # Build tree bottom-up
    while len(hashes) > 1:
        # If odd number, duplicate last hash
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        
        # Pair up and hash
        next_level = []
        for i in range(0, len(hashes), 2):
            combined = hashes[i] + hashes[i+1]
            next_level.append(hash256(combined.encode()).hex())
        
        hashes = next_level
    
    return hashes[0]
```

### Exercise 5: Difficulty Adjustment (Partial Solution)

```python
def adjust_difficulty(self):
    """Adjust mining difficulty based on block times"""
    ADJUSTMENT_INTERVAL = 10  # Adjust every 10 blocks
    TARGET_TIME = 60  # Target 60 seconds per block
    
    if len(self.chain) % ADJUSTMENT_INTERVAL != 0:
        return
    
    # Get last adjustment interval
    start_block = self.chain[-ADJUSTMENT_INTERVAL]
    end_block = self.chain[-1]
    
    actual_time = end_block.timestamp - start_block.timestamp
    target_time = TARGET_TIME * ADJUSTMENT_INTERVAL
    
    # Calculate adjustment
    if actual_time < target_time / 2:
        self.difficulty += 1  # Blocks too fast, increase difficulty
    elif actual_time > target_time * 2:
        self.difficulty = max(1, self.difficulty - 1)  # Too slow, decrease
    
    print(f"⚙️  Difficulty adjusted to {self.difficulty}")
```

### Exercise 8: Double Spend Prevention (Test)

```python
def test_double_spend():
    """Test that double-spending is prevented"""
    blockchain = Blockchain()
    alice = Wallet()
    bob = Wallet()
    charlie = Wallet()
    
    # Give Alice some coins
    blockchain.mine_pending_transactions(alice.address)
    
    # Get Alice's UTXO
    utxos = blockchain.utxo_set.get_utxos_for_address(alice.address)
    tx_hash, idx, utxo = utxos[0]
    
    # Create first transaction: Alice -> Bob
    tx1_input = TxInput(tx_hash, idx)
    tx1 = Transaction(
        inputs=[tx1_input],
        outputs=[TxOutput(10_00000000, bob.address)]
    )
    tx1.sign_inputs(alice, blockchain.utxo_set)
    
    # Create second transaction: Alice -> Charlie (SAME UTXO!)
    tx2_input = TxInput(tx_hash, idx)
    tx2 = Transaction(
        inputs=[tx2_input],
        outputs=[TxOutput(10_00000000, charlie.address)]
    )
    tx2.sign_inputs(alice, blockchain.utxo_set)
    
    # Add first transaction
    assert blockchain.add_transaction(tx1) == True
    
    # Try to add second transaction (double spend)
    # This should fail because UTXO is already spent
    blockchain.mine_pending_transactions(alice.address)
    
    # Now the UTXO is consumed, tx2 should fail
    assert blockchain.add_transaction(tx2) == False
    
    print("✅ Double spend prevented!")
```

---

## Challenge Project Ideas

### Beginner
1. **Transaction Explorer**: Build a web UI to view blockchain and transactions
2. **Wallet App**: Create a simple wallet with QR code generation
3. **Block Monitor**: Track mining statistics (hash rate, block time)

### Intermediate
4. **Lightning Network**: Implement payment channels
5. **Mining Pool**: Simulate collaborative mining with reward distribution
6. **Atomic Swap**: Enable cross-chain trades

### Advanced
7. **Smart Contract Layer**: Add Turing-complete scripting
8. **Privacy Features**: Implement CoinJoin or ring signatures
9. **Sidechains**: Create a two-way peg with another blockchain

---

## Learning Tips

1. **Start Small**: Do exercises in order, they build on each other
2. **Test Everything**: Write tests for each feature
3. **Read Code**: Study Bitcoin Core implementation for comparison
4. **Ask Questions**: Join Bitcoin developer communities
5. **Build Projects**: The best way to learn is by building

## Resources

- Bitcoin Developer Guide: https://developer.bitcoin.org/devguide/
- Bitcoin Improvement Proposals: https://github.com/bitcoin/bips
- Bitcoin Stack Exchange: https://bitcoin.stackexchange.com/
- Bitcoin Core source: https://github.com/bitcoin/bitcoin

Happy Coding! 🚀
