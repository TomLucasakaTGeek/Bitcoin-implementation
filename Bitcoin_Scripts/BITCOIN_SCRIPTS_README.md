# Bitcoin Script Engine - Complete Implementation

A comprehensive, educational implementation of Bitcoin's scripting language with all major script types.

## 🎯 What is Bitcoin Script?

Bitcoin Script is a **stack-based**, **Forth-like** programming language used to define **spending conditions** for transaction outputs. It's:

- ✅ **Simple**: No loops, limited opcodes
- ✅ **Deterministic**: Same inputs = same outputs
- ✅ **Stack-based**: Operations use a stack data structure
- ✅ **Non-Turing-complete**: Prevents infinite loops (by design)

## 📚 What's Implemented

### ✅ Script Types

1. **P2PKH** (Pay-to-PubKey-Hash) - Standard transactions
2. **P2SH** (Pay-to-Script-Hash) - Complex scripts
3. **P2WPKH** (Pay-to-Witness-PubKey-Hash) - SegWit v0
4. **P2WSH** (Pay-to-Witness-Script-Hash) - SegWit v0
5. **Multisig** (M-of-N) - Multiple signatures required
6. **CLTV** (CheckLockTimeVerify) - Absolute timelocks
7. **CSV** (CheckSequenceVerify) - Relative timelocks
8. **HTLC** (Hash Time Locked Contracts) - Lightning Network

### ✅ Opcodes (50+)

**Constants**: OP_0, OP_1 through OP_16, OP_TRUE, OP_FALSE

**Stack Operations**:
- OP_DUP, OP_DROP, OP_SWAP, OP_OVER, OP_ROT
- OP_2DUP, OP_3DUP, OP_2DROP, OP_2SWAP

**Arithmetic**:
- OP_ADD, OP_SUB, OP_1ADD, OP_1SUB
- Comparison: OP_EQUAL, OP_EQUALVERIFY

**Crypto**:
- OP_SHA256, OP_HASH160, OP_HASH256
- OP_CHECKSIG, OP_CHECKSIGVERIFY
- OP_CHECKMULTISIG, OP_CHECKMULTISIGVERIFY

**Timelocks**:
- OP_CHECKLOCKTIMEVERIFY (CLTV)
- OP_CHECKSEQUENCEVERIFY (CSV)

**Flow Control**:
- OP_IF, OP_ELSE, OP_ENDIF
- OP_VERIFY, OP_RETURN

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         Script Templates                    │
│  (P2PKH, P2SH, Multisig, Timelocks)        │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│         Script Interpreter                  │
│  (Stack-based VM, Opcode Execution)        │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│         Opcodes & Operations                │
│  (Stack, Crypto, Arithmetic, Logic)        │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│      Cryptographic Primitives               │
│  (SHA256, HASH160, Signatures)             │
└─────────────────────────────────────────────┘
```

## 📖 Script Types Explained

### 1. P2PKH (Pay-to-PubKey-Hash) ⭐ Most Common

**What it is:**
The standard way to send Bitcoin to someone. ~90% of transactions use this.

**Locking Script (ScriptPubKey):**
```
OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
```

**Unlocking Script (ScriptSig):**
```
<signature> <pubKey>
```

**How it works:**
```
Stack execution:

1. Push signature and pubkey from ScriptSig
   Stack: [signature, pubkey]

2. OP_DUP duplicates pubkey
   Stack: [signature, pubkey, pubkey]

3. OP_HASH160 hashes top item
   Stack: [signature, pubkey, hash160(pubkey)]

4. Push expected pubKeyHash
   Stack: [signature, pubkey, hash160(pubkey), pubKeyHash]

5. OP_EQUALVERIFY checks equality
   Stack: [signature, pubkey]

6. OP_CHECKSIG verifies signature
   Stack: [1] if valid, [0] if invalid
```

**Use case:**
Sending Bitcoin to an address like `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`

---

### 2. P2SH (Pay-to-Script-Hash)

**What it is:**
Allows complex scripts while keeping the output simple. The sender doesn't need to know the script details.

**Locking Script:**
```
OP_HASH160 <scriptHash> OP_EQUAL
```

**Unlocking Script:**
```
<data> ... <redeemScript>
```

**How it works:**
1. Hash the redeem script
2. Check it matches the script hash
3. Execute the redeem script

**Use case:**
- Multisig wallets
- Complex spending conditions
- Lightning Network channels

**Example: 2-of-3 Multisig P2SH:**
```
Redeem Script: 2 <pubkey1> <pubkey2> <pubkey3> 3 OP_CHECKMULTISIG
Script Hash: HASH160(redeem_script)
ScriptPubKey: OP_HASH160 <script_hash> OP_EQUAL
ScriptSig: 0 <sig1> <sig2> <redeem_script>
```

---

### 3. P2WPKH (Pay-to-Witness-PubKey-Hash) - SegWit

**What it is:**
SegWit version of P2PKH. Signature data moved to "witness" field.

**ScriptPubKey:**
```
OP_0 <20-byte-pubkey-hash>
```

**Witness:**
```
<signature> <pubkey>
```

**Benefits:**
- ✅ **~40% cheaper** fees (witness discount)
- ✅ **Fixes transaction malleability**
- ✅ **Enables Lightning Network**
- ✅ **Cleaner transaction structure**

**Use case:**
Modern Bitcoin wallets (bc1 addresses)

---

### 4. Multisig (M-of-N Signatures)

**What it is:**
Requires M signatures out of N possible public keys.

**Script:**
```
M <pubkey1> <pubkey2> ... <pubkeyN> N OP_CHECKMULTISIG
```

**Common Configurations:**
- **1-of-2**: Either party can spend
- **2-of-2**: Both parties must agree
- **2-of-3**: Any 2 of 3 can spend (escrow)
- **3-of-5**: Corporate wallets

**Example: 2-of-3 Multisig:**
```
ScriptPubKey: 2 <alice_pubkey> <bob_pubkey> <charlie_pubkey> 3 OP_CHECKMULTISIG
ScriptSig: 0 <alice_sig> <bob_sig>  # 0 is for OP_CHECKMULTISIG bug
```

**Use cases:**
- Shared wallets (couples, businesses)
- Escrow services
- Cold storage with backup keys
- Corporate treasury management

---

### 5. CLTV (CheckLockTimeVerify) - Absolute Timelock

**What it is:**
Funds can only be spent after a specific time or block height.

**Script:**
```
<locktime> OP_CHECKLOCKTIMEVERIFY OP_DROP
OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
```

**Locktime Types:**
- **Block height**: `<500000>` = Block #500,000
- **Timestamp**: `<1609459200>` = Jan 1, 2021

**How it works:**
1. Push locktime value
2. OP_CHECKLOCKTIMEVERIFY checks if current time/block >= locktime
3. If yes, continue; if no, fail
4. Rest is standard P2PKH

**Use cases:**
- Trust funds (release on 18th birthday)
- Vesting schedules
- Time-delayed payments
- Estate planning

**Example:**
```python
# Lock until block 700,000
locktime = 700000
script = timelock_script_cltv(locktime, pubkey_hash)

# Can only spend when blockchain height >= 700,000
```

---

### 6. CSV (CheckSequenceVerify) - Relative Timelock

**What it is:**
Funds can be spent N blocks AFTER the UTXO was created.

**Script:**
```
<sequence> OP_CHECKSEQUENCEVERIFY OP_DROP
OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
```

**How it works:**
- `<144>` = Can spend 144 blocks (~24 hours) after UTXO creation
- Measured from when UTXO entered blockchain, not absolute time

**Use cases:**
- Lightning Network (penalty transactions)
- Payment channels
- Refund mechanisms
- Dispute resolution periods

**Difference from CLTV:**
```
CLTV: "Can spend after Jan 1, 2025"  (absolute)
CSV:  "Can spend 100 blocks after receiving"  (relative)
```

---

### 7. HTLC (Hash Time Locked Contract)

**What it is:**
Combination of hash lock + time lock. Core primitive for Lightning Network.

**Script:**
```
OP_IF
    OP_SHA256 <hash> OP_EQUALVERIFY
    OP_DUP OP_HASH160 <recipient_pubkey_hash>
OP_ELSE
    <timeout> OP_CHECKLOCKTIMEVERIFY OP_DROP
    OP_DUP OP_HASH160 <sender_pubkey_hash>
OP_ENDIF
OP_EQUALVERIFY OP_CHECKSIG
```

**Two spending paths:**
1. **Recipient with preimage**: Proves they know secret (hash preimage)
2. **Sender after timeout**: Gets refund if recipient doesn't claim

**How it works:**
```
Alice wants to pay Bob atomically:

1. Alice locks: "Bob can spend if he reveals X where SHA256(X) = H"
2. Bob reveals X to claim (hash lock path)
3. If Bob doesn't claim within timeout, Alice gets refund (timelock path)
```

**Use cases:**
- **Lightning Network** payment routing
- **Atomic Swaps** between chains
- **Submarine Swaps** (on-chain ↔ Lightning)
- Conditional payments

---

## 💻 Usage Examples

### Example 1: Simple P2PKH Transaction

```python
from bitcoin_scripts import *

# 1. Generate keys
private_key = secrets.token_bytes(32)
public_key = sha256(private_key + b'pubkey')
pubkey_hash = hash160(public_key)

# 2. Create locking script
script_pubkey = ScriptTemplates.p2pkh_script_pubkey(pubkey_hash)

# 3. Sign transaction
tx_data = b"transaction_to_sign"
signature = sign_message(private_key, tx_data)

# 4. Create unlocking script
script_sig = ScriptTemplates.p2pkh_script_sig(signature, public_key)

# 5. Execute and verify
interpreter = ScriptInterpreter({'tx_data': tx_data})
interpreter.execute(script_sig)
valid = interpreter.execute(script_pubkey)

print(f"Transaction valid: {valid}")
```

### Example 2: 2-of-3 Multisig

```python
# Generate 3 key pairs
keys = [secrets.token_bytes(32) for _ in range(3)]
pubkeys = [sha256(k + b'pubkey') for k in keys]

# Create 2-of-3 multisig
redeem_script = ScriptTemplates.multisig_script_pubkey(2, pubkeys)

# Sign with Alice and Bob
tx_data = b"multisig_tx"
sig1 = sign_message(keys[0], tx_data)  # Alice
sig2 = sign_message(keys[1], tx_data)  # Bob

# Create ScriptSig
script_sig = ScriptTemplates.multisig_script_sig([sig1, sig2])

# Verify
interpreter = ScriptInterpreter({'tx_data': tx_data})
interpreter.execute(script_sig)
valid = interpreter.execute(redeem_script)
```

### Example 3: Timelock (CLTV)

```python
# Lock funds until specific time
future_time = int(time.time()) + 86400  # 24 hours from now

script = ScriptTemplates.timelock_script_cltv(future_time, pubkey_hash)

# Try to spend before locktime - FAILS
interpreter = ScriptInterpreter({
    'tx_data': tx_data,
    'current_time': int(time.time())
})
# This will fail with "locktime not met"

# Try to spend after locktime - SUCCESS
interpreter = ScriptInterpreter({
    'tx_data': tx_data,
    'current_time': future_time + 1
})
# This will succeed
```

## 🔍 How Script Execution Works

### Stack-Based Execution

Bitcoin Script operates on a **stack** - a last-in-first-out (LIFO) data structure.

**Example: `2 3 OP_ADD`**

```
Step 1: Push 2
Stack: [2]

Step 2: Push 3
Stack: [2, 3]

Step 3: OP_ADD pops 3 and 2, adds them, pushes 5
Stack: [5]
```

### Complete P2PKH Execution

```
ScriptSig: <sig> <pubkey>
ScriptPubKey: OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG

Initial: []

1. Push <sig>: [sig]
2. Push <pubkey>: [sig, pubkey]
3. OP_DUP: [sig, pubkey, pubkey]
4. OP_HASH160: [sig, pubkey, hash160(pubkey)]
5. Push <pubKeyHash>: [sig, pubkey, hash160(pubkey), pubKeyHash]
6. OP_EQUALVERIFY: [sig, pubkey]  (verified equal, popped both)
7. OP_CHECKSIG: [1]  (signature valid)

Final: [1] = TRUE = Script succeeds!
```

## 🎓 Key Concepts

### 1. ScriptSig vs ScriptPubKey

**ScriptPubKey** (Locking Script):
- In the output being spent
- Defines spending conditions
- Created by recipient

**ScriptSig** (Unlocking Script):
- In the input spending the output
- Provides proof of ownership
- Created by sender

**Execution Order:**
```
1. Execute ScriptSig (push data to stack)
2. Execute ScriptPubKey (verify conditions)
3. If stack top is TRUE → valid!
```

### 2. Why Stack-Based?

✅ **Simple**: Easy to implement and verify
✅ **Deterministic**: No ambiguity
✅ **Compact**: Efficient encoding
✅ **Safe**: Limited operations prevent exploits

### 3. Why Not Turing-Complete?

Bitcoin Script intentionally lacks:
- ❌ Loops (no infinite loops)
- ❌ Complex control flow
- ❌ State (besides stack)

**Benefits:**
- ✅ Predictable execution time
- ✅ Predictable costs
- ✅ No halting problem
- ✅ Easier to analyze security

### 4. Script Limitations

**Max sizes:**
- Script: 10,000 bytes
- Stack elements: 520 bytes
- Stack depth: 1,000 items

**Disabled opcodes:**
- String operations (security)
- Bitwise operations (except basic)
- Multiplication/division (safety)

## 🚀 Advanced Topics

### SegWit (Segregated Witness)

**Problem:** Transaction malleability
**Solution:** Move signatures to witness field

**Benefits:**
```
Traditional:  scriptSig + scriptPubKey = full transaction
SegWit:      witness (separate) + scriptPubKey

Result:
- Transaction ID doesn't include witness
- Fixes malleability
- Enables Lightning Network
- ~40% fee discount
```

### Lightning Network HTLCs

Lightning uses HTLCs for routing:

```
Alice → Bob → Charlie

1. Charlie creates preimage R, hash H = SHA256(R)
2. Bob creates HTLC: "Pay Alice if she reveals R, or refund me after 24h"
3. Alice creates HTLC: "Pay Bob if he reveals R, or refund me after 48h"
4. Charlie reveals R to Bob (gets payment)
5. Bob reveals R to Alice (gets payment)

All atomic - either all succeed or all fail!
```

## 📊 Script Type Comparison

| Type | Size | Privacy | Fees | Complexity | Use Case |
|------|------|---------|------|----------|----------|
| P2PKH | Medium | Low | Medium | Simple | Standard payments |
| P2SH | Small | Medium | Medium | Flexible | Multisig, complex |
| P2WPKH | Small | Low | Low (SegWit) | Simple | Modern wallets |
| P2WSH | Small | Medium | Low (SegWit) | Flexible | Advanced scripts |
| Multisig | Large | Low | High | Medium | Shared control |
| Timelock | Medium | Low | Medium | Medium | Delayed payments |

## 🎯 Interview Questions

### Q1: How does OP_CHECKSIG work?

**Answer:**
1. Pops public key and signature from stack
2. Reconstructs transaction data being signed
3. Verifies ECDSA signature with public key
4. Pushes 1 (true) if valid, 0 (false) if invalid

### Q2: What's the difference between P2SH and P2PKH?

**Answer:**
- **P2PKH**: Pay to public key hash (simple)
- **P2SH**: Pay to script hash (complex scripts hidden)

P2SH allows complex conditions (multisig, timelocks) while keeping outputs small.

### Q3: Why does OP_CHECKMULTISIG have a bug?

**Answer:**
Due to an off-by-one error, OP_CHECKMULTISIG pops one extra value from the stack. To compensate, we push OP_0 before signatures. This bug is now part of consensus rules and can't be fixed (would fork the chain).

### Q4: How do timelocks prevent double-spending?

**Answer:**
Timelocks don't prevent double-spending directly. They prevent spending before a certain time/block. Double-spend prevention comes from blockchain consensus. Timelocks enable use cases like escrow and refunds.

## 🛠️ Extensions & Exercises

### Easy:
1. Add OP_CAT (concatenate two stack elements)
2. Implement OP_SIZE (push size of top stack element)
3. Add more comparison operations

### Medium:
4. Implement Taproot (P2TR) scripts
5. Add script size/complexity limits
6. Create a script debugger with step-through

### Hard:
7. Implement full SegWit v1 (Taproot)
8. Add Schnorr signatures
9. Create a script optimizer
10. Implement MAST (Merkelized Abstract Syntax Trees)

## 📚 Further Reading

- **BIP 16**: P2SH specification
- **BIP 65**: CHECKLOCKTIMEVERIFY
- **BIP 112**: CHECKSEQUENCEVERIFY
- **BIP 141**: Segregated Witness
- **BIP 342**: Taproot validation

## ⚠️ Important Notes

**This is educational code!**

**Simplifications:**
- Uses HMAC instead of ECDSA for signatures
- Simplified signature verification
- Missing some opcodes
- No full Taproot support

**DO NOT use for:**
- Production systems
- Real Bitcoin
- Security-critical applications

**DO use for:**
- Learning Bitcoin Script
- Understanding script execution
- Preparing for Summer of Bitcoin
- Building educational projects

---

**You now understand Bitcoin Script deeply! 🎓**

This is exactly the kind of knowledge that will impress in Summer of Bitcoin interviews and bootcamp challenges!
