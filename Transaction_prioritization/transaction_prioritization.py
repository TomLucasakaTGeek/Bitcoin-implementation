"""
Transaction Prioritization Problem - Bitcoin Mining Optimization

PROBLEM STATEMENT:
Given a set of transactions with fees and sizes, select transactions to include
in a block (max 1MB) that maximize total fees while respecting:
1. Block size limit
2. Transaction dependencies (parent must be included before child)

This is a variant of the Knapsack Problem with dependencies.

ALGORITHMS IMPLEMENTED:
1. Greedy (Fee-per-byte ratio)
2. Dynamic Programming (Knapsack)
3. Ancestor Set Mining (Bitcoin Core approach)
4. Simulated Annealing (Optimization)
"""

import random
import time
from typing import List, Set, Dict, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
import heapq


# ============================================================================
# TRANSACTION REPRESENTATION
# ============================================================================

@dataclass
class MempoolTransaction:
    """
    Represents a transaction in the mempool waiting to be mined
    """
    tx_id: str
    fee: int  # Fee in satoshis
    size: int  # Size in bytes (weight in real Bitcoin)
    parents: Set[str] = field(default_factory=set)  # Parent transaction IDs
    children: Set[str] = field(default_factory=set)  # Child transaction IDs
    
    def fee_per_byte(self) -> float:
        """Calculate fee per byte (mining score)"""
        return self.fee / self.size if self.size > 0 else 0
    
    def __repr__(self):
        return f"Tx({self.tx_id}, fee={self.fee}, size={self.size}, fpb={self.fee_per_byte():.2f})"
    
    def __lt__(self, other):
        """For heap operations - higher fee/byte is "less" (priority)"""
        return self.fee_per_byte() > other.fee_per_byte()


# ============================================================================
# MEMPOOL - Transaction Pool
# ============================================================================

class Mempool:
    """
    Transaction mempool with dependency tracking
    """
    
    def __init__(self):
        self.transactions: Dict[str, MempoolTransaction] = {}
    
    def add_transaction(self, tx: MempoolTransaction):
        """Add transaction to mempool"""
        self.transactions[tx.tx_id] = tx
        
        # Update parent-child relationships
        for parent_id in tx.parents:
            if parent_id in self.transactions:
                self.transactions[parent_id].children.add(tx.tx_id)
    
    def get_transaction(self, tx_id: str) -> Optional[MempoolTransaction]:
        """Get transaction by ID"""
        return self.transactions.get(tx_id)
    
    def remove_transaction(self, tx_id: str):
        """Remove transaction from mempool"""
        if tx_id in self.transactions:
            tx = self.transactions[tx_id]
            
            # Update parent references
            for parent_id in tx.parents:
                if parent_id in self.transactions:
                    self.transactions[parent_id].children.discard(tx_id)
            
            # Update child references
            for child_id in tx.children:
                if child_id in self.transactions:
                    self.transactions[child_id].parents.discard(tx_id)
            
            del self.transactions[tx_id]
    
    def get_all_transactions(self) -> List[MempoolTransaction]:
        """Get all transactions"""
        return list(self.transactions.values())
    
    def get_stats(self) -> Dict:
        """Get mempool statistics"""
        txs = self.get_all_transactions()
        return {
            'count': len(txs),
            'total_size': sum(tx.size for tx in txs),
            'total_fees': sum(tx.fee for tx in txs),
            'avg_fee_per_byte': sum(tx.fee for tx in txs) / sum(tx.size for tx in txs) if txs else 0
        }
    
    def __len__(self):
        return len(self.transactions)


# ============================================================================
# ALGORITHM 1: GREEDY (FEE-PER-BYTE)
# ============================================================================

def greedy_selection(mempool: Mempool, max_block_size: int = 1_000_000) -> Tuple[List[str], int, int]:
    """
    Greedy algorithm: Select transactions by highest fee-per-byte ratio
    Time Complexity: O(n log n) for sorting
    
    Returns: (selected_tx_ids, total_fee, total_size)
    """
    print("\n" + "="*70)
    print("ALGORITHM 1: GREEDY (Fee-per-Byte)")
    print("="*70)
    
    start_time = time.time()
    
    # Get all transactions
    all_txs = mempool.get_all_transactions()
    
    # Sort by fee-per-byte (descending)
    sorted_txs = sorted(all_txs, key=lambda tx: tx.fee_per_byte(), reverse=True)
    
    selected = []
    selected_ids = set()
    current_size = 0
    total_fee = 0
    
    for tx in sorted_txs:
        # Check if all parents are included
        if not tx.parents.issubset(selected_ids):
            continue
        
        # Check if it fits
        if current_size + tx.size <= max_block_size:
            selected.append(tx.tx_id)
            selected_ids.add(tx.tx_id)
            current_size += tx.size
            total_fee += tx.fee
    
    elapsed = time.time() - start_time
    
    print(f"Selected: {len(selected)} transactions")
    print(f"Total Fee: {total_fee:,} satoshis")
    print(f"Total Size: {current_size:,} / {max_block_size:,} bytes ({current_size/max_block_size*100:.1f}%)")
    print(f"Avg Fee/Byte: {total_fee/current_size:.2f} sat/byte" if current_size > 0 else "N/A")
    print(f"Time: {elapsed*1000:.2f}ms")
    
    return selected, total_fee, current_size


# ============================================================================
# ALGORITHM 2: DYNAMIC PROGRAMMING (KNAPSACK)
# ============================================================================

def dp_knapsack_selection(mempool: Mempool, max_block_size: int = 1_000_000) -> Tuple[List[str], int, int]:
    """
    Dynamic Programming approach (0/1 Knapsack variant)
    
    Note: This is simplified and doesn't handle dependencies optimally.
    For demonstration purposes only - too slow for large mempools.
    
    Time Complexity: O(n * W) where W is max_block_size
    """
    print("\n" + "="*70)
    print("ALGORITHM 2: DYNAMIC PROGRAMMING (Knapsack)")
    print("="*70)
    
    start_time = time.time()
    
    # Get transactions without dependencies (simplified)
    all_txs = [tx for tx in mempool.get_all_transactions() if not tx.parents]
    
    if len(all_txs) > 100:  # Too slow for large sets
        print("⚠️  Too many transactions for DP, limiting to 100 highest fee/byte...")
        all_txs = sorted(all_txs, key=lambda tx: tx.fee_per_byte(), reverse=True)[:100]
    
    n = len(all_txs)
    
    # DP table: dp[i][w] = max fee using first i items with weight <= w
    # Using size-reduced approach (scale down by 1000 to make it tractable)
    scale = 1000
    max_size_scaled = max_block_size // scale
    
    dp = [[0] * (max_size_scaled + 1) for _ in range(n + 1)]
    
    # Fill DP table
    for i in range(1, n + 1):
        tx = all_txs[i - 1]
        tx_size_scaled = tx.size // scale
        
        for w in range(max_size_scaled + 1):
            # Don't take this transaction
            dp[i][w] = dp[i-1][w]
            
            # Take this transaction if it fits
            if tx_size_scaled <= w:
                dp[i][w] = max(dp[i][w], dp[i-1][w - tx_size_scaled] + tx.fee)
    
    # Backtrack to find selected transactions
    selected = []
    w = max_size_scaled
    total_size = 0
    
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            tx = all_txs[i - 1]
            selected.append(tx.tx_id)
            total_size += tx.size
            w -= tx.size // scale
    
    total_fee = dp[n][max_size_scaled]
    elapsed = time.time() - start_time
    
    print(f"Selected: {len(selected)} transactions")
    print(f"Total Fee: {total_fee:,} satoshis")
    print(f"Total Size: {total_size:,} / {max_block_size:,} bytes")
    print(f"Time: {elapsed*1000:.2f}ms")
    print(f"⚠️  Note: Simplified version without full dependency handling")
    
    return selected, total_fee, total_size


# ============================================================================
# ALGORITHM 3: ANCESTOR SET MINING (Bitcoin Core Approach)
# ============================================================================

@dataclass
class AncestorSet:
    """Represents a transaction with all its ancestors"""
    tx_ids: Set[str]
    total_fee: int
    total_size: int
    
    def score(self) -> float:
        """Mining score (fee per byte for the entire package)"""
        return self.total_fee / self.total_size if self.total_size > 0 else 0


def calculate_ancestor_set(tx_id: str, mempool: Mempool, memo: Dict[str, AncestorSet]) -> AncestorSet:
    """
    Calculate ancestor set for a transaction (recursive with memoization)
    Includes the transaction itself and all its ancestors
    """
    if tx_id in memo:
        return memo[tx_id]
    
    tx = mempool.get_transaction(tx_id)
    if not tx:
        return AncestorSet(set(), 0, 0)
    
    # Start with this transaction
    ancestor_ids = {tx_id}
    total_fee = tx.fee
    total_size = tx.size
    
    # Add all parent ancestor sets
    for parent_id in tx.parents:
        parent_set = calculate_ancestor_set(parent_id, mempool, memo)
        ancestor_ids.update(parent_set.tx_ids)
        total_fee += parent_set.total_fee
        total_size += parent_set.total_size
    
    result = AncestorSet(ancestor_ids, total_fee, total_size)
    memo[tx_id] = result
    return result


def ancestor_set_mining(mempool: Mempool, max_block_size: int = 1_000_000) -> Tuple[List[str], int, int]:
    """
    Ancestor Set Mining Algorithm (Bitcoin Core approach)
    
    1. Calculate ancestor sets for all transactions
    2. Sort by ancestor set fee-per-byte
    3. Greedily select highest-scoring sets that fit
    
    This properly handles transaction dependencies!
    """
    print("\n" + "="*70)
    print("ALGORITHM 3: ANCESTOR SET MINING (Bitcoin Core)")
    print("="*70)
    
    start_time = time.time()
    
    # Calculate ancestor sets for all transactions
    memo = {}
    ancestor_sets = []
    
    for tx_id in mempool.transactions:
        ancestor_set = calculate_ancestor_set(tx_id, mempool, memo)
        ancestor_sets.append((tx_id, ancestor_set))
    
    # Sort by ancestor set score (descending)
    ancestor_sets.sort(key=lambda x: x[1].score(), reverse=True)
    
    selected = set()
    current_size = 0
    total_fee = 0
    
    # Greedily select ancestor sets
    for tx_id, ancestor_set in ancestor_sets:
        # Check if transaction already selected
        if tx_id in selected:
            continue
        
        # Check which ancestors are not yet selected
        missing_ancestors = ancestor_set.tx_ids - selected
        missing_size = sum(mempool.get_transaction(aid).size for aid in missing_ancestors)
        
        # Check if the complete ancestor set fits
        if current_size + missing_size <= max_block_size:
            # Add all missing ancestors
            for ancestor_id in missing_ancestors:
                ancestor_tx = mempool.get_transaction(ancestor_id)
                selected.add(ancestor_id)
                current_size += ancestor_tx.size
                total_fee += ancestor_tx.fee
    
    elapsed = time.time() - start_time
    
    print(f"Selected: {len(selected)} transactions")
    print(f"Total Fee: {total_fee:,} satoshis")
    print(f"Total Size: {current_size:,} / {max_block_size:,} bytes ({current_size/max_block_size*100:.1f}%)")
    print(f"Avg Fee/Byte: {total_fee/current_size:.2f} sat/byte" if current_size > 0 else "N/A")
    print(f"Time: {elapsed*1000:.2f}ms")
    
    return list(selected), total_fee, current_size


# ============================================================================
# ALGORITHM 4: SIMULATED ANNEALING (OPTIMIZATION)
# ============================================================================

def simulated_annealing_selection(mempool: Mempool, max_block_size: int = 1_000_000, 
                                 iterations: int = 10000) -> Tuple[List[str], int, int]:
    """
    Simulated Annealing optimization
    
    1. Start with a random valid selection
    2. Iteratively try random modifications
    3. Accept improvements always, accept deteriorations with decreasing probability
    
    Good for finding near-optimal solutions when exact optimization is too slow.
    """
    print("\n" + "="*70)
    print("ALGORITHM 4: SIMULATED ANNEALING")
    print("="*70)
    
    start_time = time.time()
    
    all_txs = mempool.get_all_transactions()
    tx_dict = {tx.tx_id: tx for tx in all_txs}
    
    def is_valid_selection(selected_ids: Set[str]) -> bool:
        """Check if selection satisfies dependencies"""
        for tx_id in selected_ids:
            tx = tx_dict[tx_id]
            if not tx.parents.issubset(selected_ids):
                return False
        return True
    
    def calculate_score(selected_ids: Set[str]) -> Tuple[int, int]:
        """Calculate total fee and size"""
        total_fee = sum(tx_dict[tx_id].fee for tx_id in selected_ids)
        total_size = sum(tx_dict[tx_id].size for tx_id in selected_ids)
        return total_fee, total_size
    
    # Start with greedy solution as initial state
    initial_selected, _, _ = greedy_selection(mempool, max_block_size)
    current_selection = set(initial_selected)
    current_fee, current_size = calculate_score(current_selection)
    
    best_selection = current_selection.copy()
    best_fee = current_fee
    
    # Simulated annealing parameters
    temperature = 1000.0
    cooling_rate = 0.995
    
    for iteration in range(iterations):
        # Generate neighbor solution
        neighbor = current_selection.copy()
        
        # Random modification
        if random.random() < 0.5 and neighbor:
            # Remove a random transaction (and dependents)
            to_remove = random.choice(list(neighbor))
            neighbor.remove(to_remove)
            
            # Remove children that depend on it
            to_check = [to_remove]
            while to_check:
                tx_id = to_check.pop()
                tx = tx_dict[tx_id]
                for child_id in tx.children:
                    if child_id in neighbor:
                        neighbor.discard(child_id)
                        to_check.append(child_id)
        else:
            # Add a random transaction (with parents)
            candidates = [tx for tx in all_txs if tx.tx_id not in neighbor]
            if candidates:
                to_add = random.choice(candidates)
                
                # Add parents first
                to_add_set = {to_add.tx_id}
                queue = [to_add.tx_id]
                while queue:
                    tx_id = queue.pop(0)
                    tx = tx_dict[tx_id]
                    for parent_id in tx.parents:
                        if parent_id not in neighbor and parent_id not in to_add_set:
                            to_add_set.add(parent_id)
                            queue.append(parent_id)
                
                # Check if it fits
                add_size = sum(tx_dict[tx_id].size for tx_id in to_add_set)
                neighbor_size = sum(tx_dict[tx_id].size for tx_id in neighbor)
                
                if neighbor_size + add_size <= max_block_size:
                    neighbor.update(to_add_set)
        
        # Evaluate neighbor
        if is_valid_selection(neighbor):
            neighbor_fee, neighbor_size = calculate_score(neighbor)
            
            if neighbor_size <= max_block_size:
                # Accept if better
                if neighbor_fee > current_fee:
                    current_selection = neighbor
                    current_fee = neighbor_fee
                    current_size = neighbor_size
                    
                    if current_fee > best_fee:
                        best_selection = current_selection.copy()
                        best_fee = current_fee
                else:
                    # Accept with probability based on temperature
                    delta = neighbor_fee - current_fee
                    acceptance_prob = min(1.0, float(delta) / temperature) if temperature > 0 else 0
                    
                    if random.random() < acceptance_prob:
                        current_selection = neighbor
                        current_fee = neighbor_fee
                        current_size = neighbor_size
        
        # Cool down
        temperature *= cooling_rate
    
    best_size = sum(tx_dict[tx_id].size for tx_id in best_selection)
    elapsed = time.time() - start_time
    
    print(f"Iterations: {iterations:,}")
    print(f"Selected: {len(best_selection)} transactions")
    print(f"Total Fee: {best_fee:,} satoshis")
    print(f"Total Size: {best_size:,} / {max_block_size:,} bytes ({best_size/max_block_size*100:.1f}%)")
    print(f"Avg Fee/Byte: {best_fee/best_size:.2f} sat/byte" if best_size > 0 else "N/A")
    print(f"Time: {elapsed*1000:.2f}ms")
    
    return list(best_selection), best_fee, best_size


# ============================================================================
# TEST DATA GENERATION
# ============================================================================

def generate_test_mempool(num_transactions: int = 1000, dependency_prob: float = 0.2) -> Mempool:
    """
    Generate a realistic test mempool with random transactions and dependencies
    
    Args:
        num_transactions: Number of transactions to generate
        dependency_prob: Probability that a transaction depends on previous ones
    """
    mempool = Mempool()
    tx_ids = []
    
    for i in range(num_transactions):
        tx_id = f"tx_{i:04d}"
        
        # Random fee and size (realistic distributions)
        # Fee: 1000-50000 satoshis
        # Size: 250-2000 bytes
        fee = random.randint(1000, 50000)
        size = random.randint(250, 2000)
        
        # Create dependencies
        parents = set()
        if tx_ids and random.random() < dependency_prob:
            # Depend on 1-3 previous transactions
            num_parents = random.randint(1, min(3, len(tx_ids)))
            parents = set(random.sample(tx_ids, num_parents))
        
        tx = MempoolTransaction(
            tx_id=tx_id,
            fee=fee,
            size=size,
            parents=parents
        )
        
        mempool.add_transaction(tx)
        tx_ids.append(tx_id)
    
    return mempool


def generate_realistic_mempool() -> Mempool:
    """
    Generate a more realistic mempool with transaction patterns
    """
    mempool = Mempool()
    
    # Scenario 1: High-fee single transactions
    for i in range(100):
        mempool.add_transaction(MempoolTransaction(
            tx_id=f"high_{i}",
            fee=random.randint(50000, 100000),
            size=random.randint(200, 400)
        ))
    
    # Scenario 2: Low-fee transactions
    for i in range(300):
        mempool.add_transaction(MempoolTransaction(
            tx_id=f"low_{i}",
            fee=random.randint(1000, 5000),
            size=random.randint(300, 600)
        ))
    
    # Scenario 3: Transaction chains (parent-child)
    for chain in range(20):
        parent_id = f"chain_{chain}_0"
        mempool.add_transaction(MempoolTransaction(
            tx_id=parent_id,
            fee=random.randint(5000, 10000),
            size=random.randint(250, 400)
        ))
        
        current_parent = parent_id
        for depth in range(1, random.randint(2, 6)):
            child_id = f"chain_{chain}_{depth}"
            mempool.add_transaction(MempoolTransaction(
                tx_id=child_id,
                fee=random.randint(10000, 30000),  # Higher fees for CPFP
                size=random.randint(250, 400),
                parents={current_parent}
            ))
            current_parent = child_id
    
    # Scenario 4: CPFP (Child Pays For Parent) - high-fee child with low-fee parent
    for i in range(30):
        parent_id = f"cpfp_parent_{i}"
        mempool.add_transaction(MempoolTransaction(
            tx_id=parent_id,
            fee=1000,  # Low fee
            size=400
        ))
        
        child_id = f"cpfp_child_{i}"
        mempool.add_transaction(MempoolTransaction(
            tx_id=child_id,
            fee=80000,  # Very high fee to compensate
            size=300,
            parents={parent_id}
        ))
    
    return mempool


# ============================================================================
# COMPARISON & BENCHMARKING
# ============================================================================

def compare_algorithms(mempool: Mempool, max_block_size: int = 1_000_000):
    """
    Run all algorithms and compare results
    """
    print("\n" + "="*70)
    print("TRANSACTION PRIORITIZATION COMPARISON")
    print("="*70)
    
    stats = mempool.get_stats()
    print(f"\nMempool Stats:")
    print(f"  Transactions: {stats['count']:,}")
    print(f"  Total Size: {stats['total_size']:,} bytes")
    print(f"  Total Fees: {stats['total_fees']:,} satoshis")
    print(f"  Avg Fee/Byte: {stats['avg_fee_per_byte']:.2f} sat/byte")
    print(f"\nBlock Size Limit: {max_block_size:,} bytes")
    
    results = {}
    
    # Run algorithms
    results['greedy'] = greedy_selection(mempool, max_block_size)
    results['ancestor_set'] = ancestor_set_mining(mempool, max_block_size)
    
    # Only run DP for small mempools
    if len(mempool) <= 100:
        results['dp'] = dp_knapsack_selection(mempool, max_block_size)
    
    results['simulated_annealing'] = simulated_annealing_selection(mempool, max_block_size, iterations=5000)
    
    # Summary comparison
    print("\n" + "="*70)
    print("SUMMARY COMPARISON")
    print("="*70)
    print(f"{'Algorithm':<25} {'Txs':>8} {'Total Fee':>15} {'Size %':>10} {'Fee/Byte':>12}")
    print("-"*70)
    
    for name, (selected, fee, size) in results.items():
        size_pct = size / max_block_size * 100
        fee_per_byte = fee / size if size > 0 else 0
        print(f"{name:<25} {len(selected):>8} {fee:>15,} {size_pct:>9.1f}% {fee_per_byte:>11.2f}")
    
    # Find best
    best_algo = max(results.items(), key=lambda x: x[1][1])
    print(f"\n🏆 Best Algorithm: {best_algo[0].upper()} with {best_algo[1][1]:,} satoshis")


# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

def main():
    print("="*70)
    print("BITCOIN TRANSACTION PRIORITIZATION PROBLEM")
    print("="*70)
    print("\nThis demonstrates different algorithms for selecting transactions")
    print("to maximize mining revenue while respecting block size limits and")
    print("transaction dependencies.")
    
    # Generate test data
    print("\n📊 Generating realistic mempool...")
    mempool = generate_realistic_mempool()
    
    # Run comparison
    compare_algorithms(mempool, max_block_size=1_000_000)
    
    print("\n" + "="*70)
    print("KEY INSIGHTS")
    print("="*70)
    print("""
1. GREEDY (Fee-per-Byte):
   - Fast and simple
   - May miss high-fee transaction chains
   - O(n log n) complexity
   
2. ANCESTOR SET MINING:
   - Bitcoin Core's actual approach
   - Properly handles CPFP (Child Pays For Parent)
   - Considers packages of dependent transactions
   - Near-optimal in practice
   
3. DYNAMIC PROGRAMMING:
   - Optimal for simple knapsack without dependencies
   - Too slow for large mempools (1000s of transactions)
   - Doesn't handle dependencies well
   
4. SIMULATED ANNEALING:
   - Can find better solutions than greedy
   - Tunable (more iterations = better but slower)
   - Good for exploring solution space
   
WINNER: Ancestor Set Mining
- Best balance of optimality and speed
- Handles real-world scenarios (CPFP, chains)
- Actually used in Bitcoin Core
""")


if __name__ == "__main__":
    main()
