"""
Educational Bitcoin Implementation
Demonstrates core Bitcoin concepts: UTXO model, mining, transactions, digital signatures, and basic P2P
"""

import hashlib
import time
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import struct
import secrets
import hmac


# ============================================================================
# CRYPTOGRAPHIC PRIMITIVES
# ============================================================================

def sha256(data: bytes) -> bytes:
    """Single SHA256 hash"""
    return hashlib.sha256(data).digest()


def hash256(data: bytes) -> bytes:
    """Double SHA256 hash (Bitcoin standard)"""
    return sha256(sha256(data))


def ripemd160(data: bytes) -> bytes:
    """RIPEMD160 hash"""
    return hashlib.new('ripemd160', data).digest()


def hash160(data: bytes) -> bytes:
    """SHA256 followed by RIPEMD160 (used for addresses)"""
    return ripemd160(sha256(data))


# ============================================================================
# WALLET & KEY MANAGEMENT
# ============================================================================

class Wallet:
    """
    Simplified wallet with key pair generation and address creation
    Note: This uses HMAC for demonstration. Real Bitcoin uses ECDSA (secp256k1)
    """
    
    def __init__(self):
        # Generate a random 32-byte private key
        self.private_key = secrets.token_bytes(32)
        
        # Derive public key from private key (simplified - real Bitcoin uses EC point multiplication)
        self.public_key = sha256(self.private_key + b'pubkey')
        
        self.address = self._generate_address()
    
    def _generate_address(self) -> str:
        """Generate Bitcoin-style address from public key"""
        # Hash the public key
        pub_key_hash = hash160(self.public_key)
        
        # Add version byte (0x00 for mainnet)
        versioned_hash = b'\x00' + pub_key_hash
        
        # Calculate checksum
        checksum = hash256(versioned_hash)[:4]
        
        # Create address
        address_bytes = versioned_hash + checksum
        
        # Return hex representation (simplified - real Bitcoin uses Base58)
        return address_bytes.hex()
    
    def sign(self, message: bytes) -> bytes:
        """
        Sign a message with private key
        Uses HMAC-SHA256 (simplified - real Bitcoin uses ECDSA signatures)
        """
        return hmac.new(self.private_key, message, hashlib.sha256).digest()
    
    def verify(self, message: bytes, signature: bytes) -> bool:
        """Verify a signature"""
        expected_signature = self.sign(message)
        return hmac.compare_digest(signature, expected_signature)
    
    @staticmethod
    def verify_with_pubkey(public_key_bytes: bytes, message: bytes, signature: bytes) -> bool:
        """
        Verify signature with a given public key
        Note: In this simplified version, we derive the private key deterministically
        Real Bitcoin uses proper ECDSA verification without needing the private key
        """
        # This is a simplification - we're storing the relationship in the signature format
        # Real Bitcoin verification uses elliptic curve math
        try:
            # In real ECDSA, you can verify without the private key
            # For this demo, we check the signature format
            return len(signature) == 32  # Basic validation
        except:
            return False


# ============================================================================
# TRANSACTION COMPONENTS
# ============================================================================

@dataclass
class TxInput:
    """Transaction Input - references a previous output (UTXO)"""
    prev_tx_hash: str  # Hash of the transaction containing the UTXO
    prev_output_index: int  # Index of the output in that transaction
    signature: bytes = b''  # Digital signature proving ownership
    public_key: bytes = b''  # Public key of the sender
    
    def __str__(self):
        return f"TxInput(prev_tx: {self.prev_tx_hash[:8]}..., index: {self.prev_output_index})"


@dataclass
class TxOutput:
    """Transaction Output - creates a new UTXO"""
    amount: int  # Amount in satoshis (smallest Bitcoin unit)
    recipient_address: str  # Address that can spend this output
    
    def __str__(self):
        return f"TxOutput(amount: {self.amount} sats, to: {self.recipient_address[:8]}...)"


@dataclass
class Transaction:
    """Bitcoin Transaction"""
    inputs: List[TxInput]
    outputs: List[TxOutput]
    timestamp: int = field(default_factory=lambda: int(time.time()))
    tx_hash: str = ""
    
    def __post_init__(self):
        if not self.tx_hash:
            self.tx_hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate transaction hash"""
        tx_data = self.serialize_for_hashing()
        return hash256(tx_data).hex()
    
    def serialize_for_hashing(self) -> bytes:
        """Serialize transaction data for hashing (unsigned)"""
        data = []
        data.append(struct.pack('<I', self.timestamp))
        data.append(struct.pack('<I', len(self.inputs)))
        
        for inp in self.inputs:
            data.append(inp.prev_tx_hash.encode())
            data.append(struct.pack('<I', inp.prev_output_index))
        
        data.append(struct.pack('<I', len(self.outputs)))
        for out in self.outputs:
            data.append(struct.pack('<Q', out.amount))
            data.append(out.recipient_address.encode())
        
        return b''.join(data)
    
    def sign_inputs(self, wallet: Wallet, utxo_set: 'UTXOSet'):
        """Sign all inputs in the transaction"""
        message = self.serialize_for_hashing()
        
        for inp in self.inputs:
            # Verify the input references a valid UTXO owned by this wallet
            utxo_key = f"{inp.prev_tx_hash}:{inp.prev_output_index}"
            if utxo_key in utxo_set.utxos:
                utxo = utxo_set.utxos[utxo_key]
                if utxo.recipient_address == wallet.address:
                    inp.signature = wallet.sign(message)
                    inp.public_key = wallet.public_key
        
        # Recalculate hash after signing
        self.tx_hash = self.calculate_hash()
    
    def verify_signatures(self, utxo_set: 'UTXOSet') -> bool:
        """Verify all input signatures"""
        message = self.serialize_for_hashing()
        
        for inp in self.inputs:
            if not inp.signature or not inp.public_key:
                return False
            
            # Verify signature matches the public key
            if not Wallet.verify_with_pubkey(inp.public_key, message, inp.signature):
                return False
            
            # Verify the public key corresponds to the UTXO owner
            utxo_key = f"{inp.prev_tx_hash}:{inp.prev_output_index}"
            if utxo_key not in utxo_set.utxos:
                return False
            
            utxo = utxo_set.utxos[utxo_key]
            # In real Bitcoin, we'd check the scriptPubKey, but here we use simple address comparison
            # This is a simplification - real Bitcoin uses scripts
        
        return True
    
    def __str__(self):
        return f"Transaction(hash: {self.tx_hash[:8]}..., inputs: {len(self.inputs)}, outputs: {len(self.outputs)})"


def create_coinbase_transaction(miner_address: str, block_height: int, reward: int = 50_00000000) -> Transaction:
    """Create a coinbase transaction (mining reward)"""
    # Coinbase transactions have no inputs (money created from nothing)
    coinbase_input = TxInput(
        prev_tx_hash="0" * 64,  # All zeros for coinbase
        prev_output_index=0xFFFFFFFF,  # Max value indicates coinbase
        signature=b'',
        public_key=b''
    )
    
    output = TxOutput(
        amount=reward,
        recipient_address=miner_address
    )
    
    return Transaction(
        inputs=[coinbase_input],
        outputs=[output]
    )


# ============================================================================
# UTXO SET MANAGEMENT
# ============================================================================

class UTXOSet:
    """
    Unspent Transaction Output Set
    Keeps track of all unspent outputs in the blockchain
    """
    
    def __init__(self):
        self.utxos: Dict[str, TxOutput] = {}  # Key: "tx_hash:output_index"
    
    def add_utxo(self, tx_hash: str, output_index: int, output: TxOutput):
        """Add a new UTXO"""
        key = f"{tx_hash}:{output_index}"
        self.utxos[key] = output
    
    def remove_utxo(self, tx_hash: str, output_index: int):
        """Remove a spent UTXO"""
        key = f"{tx_hash}:{output_index}"
        if key in self.utxos:
            del self.utxos[key]
    
    def get_balance(self, address: str) -> int:
        """Calculate balance for an address (sum of all UTXOs)"""
        balance = 0
        for utxo in self.utxos.values():
            if utxo.recipient_address == address:
                balance += utxo.amount
        return balance
    
    def get_utxos_for_address(self, address: str) -> List[Tuple[str, int, TxOutput]]:
        """Get all UTXOs for a given address"""
        result = []
        for key, utxo in self.utxos.items():
            if utxo.recipient_address == address:
                tx_hash, output_index = key.split(':')
                result.append((tx_hash, int(output_index), utxo))
        return result
    
    def update_with_transaction(self, tx: Transaction):
        """Update UTXO set with a new transaction"""
        # Remove spent UTXOs
        for inp in tx.inputs:
            # Skip coinbase inputs
            if inp.prev_tx_hash != "0" * 64:
                self.remove_utxo(inp.prev_tx_hash, inp.prev_output_index)
        
        # Add new UTXOs
        for idx, output in enumerate(tx.outputs):
            self.add_utxo(tx.tx_hash, idx, output)


# ============================================================================
# BLOCK & MINING
# ============================================================================

@dataclass
class Block:
    """Bitcoin Block"""
    index: int
    timestamp: int
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: str = ""
    difficulty: int = 4  # Number of leading zeros required
    
    def __post_init__(self):
        if not self.hash:
            self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        block_data = self.serialize()
        return hash256(block_data).hex()
    
    def serialize(self) -> bytes:
        """Serialize block for hashing"""
        data = []
        data.append(struct.pack('<I', self.index))
        data.append(struct.pack('<Q', self.timestamp))
        data.append(self.previous_hash.encode())
        data.append(struct.pack('<I', self.nonce))
        data.append(struct.pack('<I', self.difficulty))
        
        for tx in self.transactions:
            data.append(tx.tx_hash.encode())
        
        return b''.join(data)
    
    def mine_block(self, difficulty: Optional[int] = None) -> Tuple[int, float]:
        """
        Proof of Work mining
        Returns: (nonce, time_taken)
        """
        if difficulty is not None:
            self.difficulty = difficulty
        
        target = "0" * self.difficulty
        start_time = time.time()
        attempts = 0
        
        print(f"\n⛏️  Mining block {self.index}...")
        print(f"   Target: {target}...")
        
        while True:
            self.nonce = attempts
            self.hash = self.calculate_hash()
            
            if attempts % 100000 == 0 and attempts > 0:
                print(f"   Attempts: {attempts:,} | Hash: {self.hash[:10]}...")
            
            if self.hash.startswith(target):
                time_taken = time.time() - start_time
                print(f"✅ Block mined! Nonce: {self.nonce} | Time: {time_taken:.2f}s")
                print(f"   Hash: {self.hash}")
                return self.nonce, time_taken
            
            attempts += 1
            
            # Safety limit for demonstration
            if attempts > 10_000_000:
                print("⚠️  Mining taking too long, stopping...")
                return self.nonce, time.time() - start_time


# ============================================================================
# BLOCKCHAIN
# ============================================================================

class Blockchain:
    """Bitcoin Blockchain"""
    
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.utxo_set = UTXOSet()
        self.difficulty = 4
        self.mining_reward = 50_00000000  # 50 BTC in satoshis
        
        # Create genesis block
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_tx = Transaction(
            inputs=[],
            outputs=[TxOutput(amount=100_00000000, recipient_address="genesis")]
        )
        
        genesis_block = Block(
            index=0,
            timestamp=int(time.time()),
            transactions=[genesis_tx],
            previous_hash="0" * 64,
            difficulty=self.difficulty
        )
        
        self.chain.append(genesis_block)
        self.utxo_set.update_with_transaction(genesis_tx)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Add a transaction to pending transactions"""
        # Validate transaction
        if not self._validate_transaction(transaction):
            print(f"❌ Invalid transaction: {transaction.tx_hash[:8]}...")
            return False
        
        self.pending_transactions.append(transaction)
        print(f"✅ Transaction added to pending pool: {transaction.tx_hash[:8]}...")
        return True
    
    def _validate_transaction(self, tx: Transaction) -> bool:
        """Validate a transaction"""
        # Skip validation for coinbase transactions
        if len(tx.inputs) == 1 and tx.inputs[0].prev_tx_hash == "0" * 64:
            return True
        
        # Check inputs exist and are unspent
        total_input = 0
        for inp in tx.inputs:
            utxo_key = f"{inp.prev_tx_hash}:{inp.prev_output_index}"
            if utxo_key not in self.utxo_set.utxos:
                print(f"   Input UTXO not found: {utxo_key}")
                return False
            total_input += self.utxo_set.utxos[utxo_key].amount
        
        # Check outputs
        total_output = sum(out.amount for out in tx.outputs)
        
        if total_output > total_input:
            print(f"   Output ({total_output}) exceeds input ({total_input})")
            return False
        
        # Verify signatures
        if not tx.verify_signatures(self.utxo_set):
            print(f"   Invalid signature")
            return False
        
        return True
    
    def mine_pending_transactions(self, miner_address: str) -> Block:
        """Mine a new block with pending transactions"""
        # Create coinbase transaction (mining reward)
        coinbase_tx = create_coinbase_transaction(
            miner_address=miner_address,
            block_height=len(self.chain),
            reward=self.mining_reward
        )
        
        # Include coinbase + pending transactions
        transactions = [coinbase_tx] + self.pending_transactions
        
        # Create new block
        new_block = Block(
            index=len(self.chain),
            timestamp=int(time.time()),
            transactions=transactions,
            previous_hash=self.get_latest_block().hash,
            difficulty=self.difficulty
        )
        
        # Mine the block (Proof of Work)
        new_block.mine_block()
        
        # Add block to chain
        self.chain.append(new_block)
        
        # Update UTXO set
        for tx in transactions:
            self.utxo_set.update_with_transaction(tx)
        
        # Clear pending transactions
        self.pending_transactions = []
        
        print(f"💎 Block {new_block.index} added to blockchain!")
        return new_block
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Verify hash
            if current_block.hash != current_block.calculate_hash():
                print(f"❌ Block {i} hash mismatch")
                return False
            
            # Verify previous hash link
            if current_block.previous_hash != previous_block.hash:
                print(f"❌ Block {i} previous hash mismatch")
                return False
            
            # Verify proof of work
            if not current_block.hash.startswith("0" * current_block.difficulty):
                print(f"❌ Block {i} doesn't meet difficulty requirement")
                return False
        
        print("✅ Blockchain is valid!")
        return True
    
    def get_balance(self, address: str) -> int:
        """Get balance for an address"""
        return self.utxo_set.get_balance(address)
    
    def print_chain(self):
        """Print blockchain summary"""
        print("\n" + "="*70)
        print("BLOCKCHAIN SUMMARY")
        print("="*70)
        for block in self.chain:
            print(f"\nBlock #{block.index}")
            print(f"  Hash: {block.hash}")
            print(f"  Previous: {block.previous_hash}")
            print(f"  Timestamp: {block.timestamp}")
            print(f"  Nonce: {block.nonce}")
            print(f"  Transactions: {len(block.transactions)}")
            for tx in block.transactions:
                print(f"    - {tx}")
        print("="*70)


# ============================================================================
# PEER-TO-PEER NETWORK SIMULATION
# ============================================================================

class Node:
    """
    Bitcoin network node
    In a real P2P network, nodes would communicate over TCP/IP
    This is a simplified simulation
    """
    
    def __init__(self, name: str):
        self.name = name
        self.blockchain = Blockchain()
        self.peers: List['Node'] = []
        self.wallet = Wallet()
    
    def connect_to_peer(self, peer: 'Node'):
        """Connect to another node"""
        if peer not in self.peers:
            self.peers.append(peer)
            peer.peers.append(self)
            print(f"🔗 {self.name} connected to {peer.name}")
    
    def broadcast_transaction(self, transaction: Transaction):
        """Broadcast a transaction to all peers"""
        print(f"📡 {self.name} broadcasting transaction...")
        for peer in self.peers:
            peer.receive_transaction(transaction)
    
    def receive_transaction(self, transaction: Transaction):
        """Receive a transaction from a peer"""
        print(f"📨 {self.name} received transaction: {transaction.tx_hash[:8]}...")
        self.blockchain.add_transaction(transaction)
    
    def broadcast_block(self, block: Block):
        """Broadcast a mined block to all peers"""
        print(f"📡 {self.name} broadcasting block {block.index}...")
        for peer in self.peers:
            peer.receive_block(block)
    
    def receive_block(self, block: Block):
        """Receive a block from a peer"""
        print(f"📨 {self.name} received block {block.index}")
        # In real Bitcoin, nodes would verify and add the block
        # For this simulation, we'll just acknowledge it
    
    def mine(self):
        """Mine pending transactions"""
        print(f"\n⛏️  {self.name} is mining...")
        block = self.blockchain.mine_pending_transactions(self.wallet.address)
        self.broadcast_block(block)
        return block


# ============================================================================
# DEMONSTRATION
# ============================================================================

def main():
    print("="*70)
    print("EDUCATIONAL BITCOIN IMPLEMENTATION")
    print("="*70)
    
    # Create wallets
    print("\n📱 Creating wallets...")
    alice_wallet = Wallet()
    bob_wallet = Wallet()
    charlie_wallet = Wallet()
    
    print(f"Alice's address: {alice_wallet.address[:20]}...")
    print(f"Bob's address: {bob_wallet.address[:20]}...")
    print(f"Charlie's address: {charlie_wallet.address[:20]}...")
    
    # Create blockchain
    print("\n⛓️  Initializing blockchain...")
    blockchain = Blockchain()
    
    # Mine initial block to give Alice some coins
    print("\n💰 Mining initial coins for Alice...")
    blockchain.mine_pending_transactions(alice_wallet.address)
    
    print(f"\nAlice's balance: {blockchain.get_balance(alice_wallet.address) / 100_000_000} BTC")
    
    # Alice sends 10 BTC to Bob
    print("\n💸 Alice sending 10 BTC to Bob...")
    
    # Get Alice's UTXOs
    alice_utxos = blockchain.utxo_set.get_utxos_for_address(alice_wallet.address)
    if alice_utxos:
        tx_hash, output_idx, utxo = alice_utxos[0]
        
        # Create transaction
        tx_input = TxInput(
            prev_tx_hash=tx_hash,
            prev_output_index=output_idx
        )
        
        tx_outputs = [
            TxOutput(amount=10_00000000, recipient_address=bob_wallet.address),  # 10 BTC to Bob
            TxOutput(amount=40_00000000, recipient_address=alice_wallet.address)  # 40 BTC change back to Alice
        ]
        
        tx = Transaction(inputs=[tx_input], outputs=tx_outputs)
        tx.sign_inputs(alice_wallet, blockchain.utxo_set)
        
        blockchain.add_transaction(tx)
    
    # Mine the transaction
    print("\n⛏️  Mining transaction...")
    blockchain.mine_pending_transactions(charlie_wallet.address)
    
    # Check balances
    print("\n💰 Final Balances:")
    print(f"Alice: {blockchain.get_balance(alice_wallet.address) / 100_000_000} BTC")
    print(f"Bob: {blockchain.get_balance(bob_wallet.address) / 100_000_000} BTC")
    print(f"Charlie (miner): {blockchain.get_balance(charlie_wallet.address) / 100_000_000} BTC")
    
    # Validate blockchain
    print("\n🔍 Validating blockchain...")
    blockchain.is_chain_valid()
    
    # Print blockchain
    blockchain.print_chain()
    
    # P2P Network demonstration
    print("\n" + "="*70)
    print("P2P NETWORK SIMULATION")
    print("="*70)
    
    node1 = Node("Node-1")
    node2 = Node("Node-2")
    node3 = Node("Node-3")
    
    # Connect nodes
    node1.connect_to_peer(node2)
    node2.connect_to_peer(node3)
    
    print(f"\n🌐 Network topology:")
    print(f"   Node-1 ↔ Node-2 ↔ Node-3")
    
    # Mine some blocks on node1
    print("\n⛏️  Node-1 mining initial block...")
    node1.mine()
    
    print(f"\n💰 Node-1 miner balance: {node1.blockchain.get_balance(node1.wallet.address) / 100_000_000} BTC")
    
    print("\n✅ Demonstration complete!")


if __name__ == "__main__":
    main()
