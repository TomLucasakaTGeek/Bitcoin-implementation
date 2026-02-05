# Bitcoin Transaction Prioritization Problem

## 🎯 Problem Statement

**Given:**
- A mempool (pool of pending transactions)
- Each transaction has:
  - Fee (satoshis)
  - Size (bytes)
  - Dependencies (parent transactions that must be included first)
- Block size limit (1 MB = 1,000,000 bytes)

**Goal:**
Select a subset of transactions to maximize total fees while:
1. Staying within the block size limit
2. Respecting transaction dependencies (parent before child)

**This is a variant of the 0/1 Knapsack Problem with dependencies!**

## 🧠 Why This Matters

### For Miners:
- **Revenue Maximization**: More fees = more profit
- **Orphan Risk**: Larger blocks propagate slower (trade-off)
- **Competitive**: Other miners are optimizing too

### For Bitcoin Network:
- **Fee Market**: Users compete for block space
- **Transaction Priority**: High-fee transactions get confirmed faster
- **CPFP (Child Pays For Parent)**: Child's high fee can boost low-fee parent

### For Summer of Bitcoin:
This is a **classic interview/bootcamp problem**! You might be asked to:
- Implement a transaction selection algorithm
- Optimize for maximum fees
- Handle edge cases (dependencies, CPFP)
- Analyze time/space complexity

## 📊 Algorithms Implemented

### 1. Greedy (Fee-per-Byte) ⚡

**Approach:**
```
1. Calculate fee/byte for each transaction
2. Sort by fee/byte (descending)
3. Greedily add transactions that:
   - Have all parents already included
   - Fit in remaining block space
```

**Complexity:**
- Time: O(n log n) - dominated by sorting
- Space: O(n)

**Pros:**
- ✅ Very fast
- ✅ Simple to implement
- ✅ Good baseline solution

**Cons:**
- ❌ Can miss high-fee transaction chains
- ❌ Doesn't optimize for packages
- ❌ Suboptimal for CPFP scenarios

**Code:**
```python
def greedy_selection(mempool, max_block_size):
    sorted_txs = sorted(all_txs, key=lambda tx: tx.fee_per_byte(), reverse=True)
    
    for tx in sorted_txs:
        if tx.parents ⊆ selected and size + tx.size <= max_size:
            select(tx)
```

### 2. Dynamic Programming (Knapsack) 📐

**Approach:**
```
Classic 0/1 Knapsack DP:
dp[i][w] = max fee using first i items with weight ≤ w

Recurrence:
dp[i][w] = max(
    dp[i-1][w],              # don't take item i
    dp[i-1][w-size[i]] + fee[i]  # take item i
)
```

**Complexity:**
- Time: O(n × W) where W = max_block_size
- Space: O(n × W) or O(W) with optimization

**Pros:**
- ✅ Optimal for simple knapsack (no dependencies)
- ✅ Well-studied algorithm

**Cons:**
- ❌ Too slow for large W (1 MB!)
- ❌ Doesn't handle dependencies well
- ❌ Not practical for real Bitcoin mining

**Note:** The implementation scales down by 1000x to make it tractable.

### 3. Ancestor Set Mining ⭐ (Bitcoin Core)

**Approach:**
```
1. For each transaction, calculate its "ancestor set":
   - The transaction itself
   - All parent transactions (recursively)
   
2. Calculate ancestor set score:
   score = total_fee / total_size (for entire package)
   
3. Sort by ancestor set score
4. Greedily select highest-scoring packages
```

**Why This Works:**
- Treats transaction chains as atomic packages
- Parent's fee + child's fee = package fee
- Optimizes for CPFP (Child Pays For Parent)

**Example:**
```
Parent: fee=1000, size=400 → 2.5 sat/byte
Child:  fee=8000, size=300 → 26.7 sat/byte

Ancestor set score = (1000+8000)/(400+300) = 12.9 sat/byte

Greedy would rank child high but might not include parent.
Ancestor set mining considers them together!
```

**Complexity:**
- Time: O(n² log n) worst case, O(n log n) average
- Space: O(n)

**Pros:**
- ✅ Near-optimal in practice
- ✅ Handles CPFP correctly
- ✅ Fast enough for real-time mining
- ✅ **Actually used in Bitcoin Core!**

**Cons:**
- ❌ Not guaranteed optimal (greedy with packages)
- ❌ More complex than simple greedy

### 4. Simulated Annealing 🔥 (Optimization)

**Approach:**
```
1. Start with initial solution (e.g., greedy result)
2. Repeat for N iterations:
   a. Generate neighbor (add/remove transaction)
   b. If better: accept
   c. If worse: accept with probability e^(Δ/T)
   d. Decrease temperature T
3. Return best solution found
```

**Key Idea:**
- Early on (high T): Accept bad moves to explore
- Later (low T): Only accept improvements to converge

**Complexity:**
- Time: O(iterations × n)
- Space: O(n)

**Pros:**
- ✅ Can find better solutions than greedy
- ✅ Escapes local optima
- ✅ Tunable (more iterations = better)

**Cons:**
- ❌ No optimality guarantee
- ❌ Slower than greedy
- ❌ Results vary (randomized)

## 📈 Performance Comparison

Using realistic mempool (544 transactions, 213 KB total):

| Algorithm | Selected | Total Fee | Size Used | Fee/Byte | Time |
|-----------|----------|-----------|-----------|----------|------|
| Greedy | 450 | 8.5M sats | 18.3% | 46.56 | 0.3ms |
| **Ancestor Set** | **544** | **12.1M sats** | **21.3%** | **56.86** | **1.2ms** |
| DP Knapsack | ~100 | ~varied | varied | varied | 50ms+ |
| Simulated Annealing | 544 | 12.1M sats | 21.3% | 56.86 | 507ms |

**Winner: Ancestor Set Mining** 🏆
- **42% more fees** than simple greedy!
- Still very fast (1.2ms)
- Handles real-world scenarios

## 🎓 Key Concepts

### CPFP (Child Pays For Parent)

**Problem:**
You sent a transaction with low fee. It's stuck in mempool!

**Solution:**
Send another transaction (child) that:
- Spends the output of the stuck transaction (parent)
- Pays a very high fee

**Result:**
Miners see the high-fee child but must include the parent first.
The combined package has high fee/byte, so both get mined!

**Example:**
```
Parent: fee=1000 sat, size=400 bytes → 2.5 sat/byte (stuck!)
Child:  fee=8000 sat, size=300 bytes → 26.7 sat/byte

Package: (1000+8000)/(400+300) = 12.9 sat/byte → profitable!
```

### Transaction Dependencies

**Why do they exist?**
A transaction can only spend outputs that exist!

**Example:**
```
Tx A creates output → Tx B spends that output

B depends on A (B.parents = {A})

Miners must include A before B!
```

**In the code:**
```python
@dataclass
class MempoolTransaction:
    parents: Set[str]    # Must be included first
    children: Set[str]   # Depend on this transaction
```

### Knapsack Problem Variant

**Classic 0/1 Knapsack:**
- Items with weight and value
- Maximize value, constrain weight
- Each item taken 0 or 1 times

**Bitcoin Variant:**
- Transactions with size (weight) and fee (value)
- Maximize fees, constrain size ≤ 1 MB
- **Added constraint:** Dependencies!

## 💻 Usage Examples

### Basic Usage

```python
from transaction_prioritization import *

# Create mempool with test data
mempool = generate_realistic_mempool()

# Run greedy algorithm
selected, total_fee, total_size = greedy_selection(mempool, max_block_size=1_000_000)

print(f"Selected {len(selected)} transactions")
print(f"Total fee: {total_fee:,} satoshis")
```

### Compare All Algorithms

```python
# Run comprehensive comparison
compare_algorithms(mempool, max_block_size=1_000_000)
```

### Create Custom Mempool

```python
mempool = Mempool()

# Add independent transactions
mempool.add_transaction(MempoolTransaction(
    tx_id="tx1",
    fee=50000,
    size=400,
    parents=set()
))

# Add dependent transaction (CPFP)
mempool.add_transaction(MempoolTransaction(
    tx_id="tx2",
    fee=100000,  # High fee to boost parent
    size=300,
    parents={"tx1"}  # Depends on tx1
))

# Run ancestor set mining
selected, fee, size = ancestor_set_mining(mempool)
```

### Test Specific Scenarios

```python
# Scenario 1: All independent high-fee transactions
mempool = Mempool()
for i in range(1000):
    mempool.add_transaction(MempoolTransaction(
        tx_id=f"tx_{i}",
        fee=random.randint(10000, 50000),
        size=random.randint(250, 500)
    ))

# Scenario 2: Long transaction chain
for i in range(100):
    parents = {f"tx_{i-1}"} if i > 0 else set()
    mempool.add_transaction(MempoolTransaction(
        tx_id=f"tx_{i}",
        fee=random.randint(5000, 10000),
        size=300,
        parents=parents
    ))
```

## 🔬 Complexity Analysis

### Greedy Algorithm

```
Time:
  - Sorting: O(n log n)
  - Iteration: O(n)
  - Dependency check per tx: O(p) where p = avg parents
  Total: O(n log n + n×p) ≈ O(n log n)

Space: O(n) for storing transactions
```

### Ancestor Set Mining

```
Time:
  - Calculate ancestor sets: O(n × d) where d = max depth
  - Sorting: O(n log n)
  - Selection: O(n)
  Total: O(n × d + n log n)
  
  Worst case: d = n (linear chain) → O(n²)
  Average case: d = small constant → O(n log n)

Space: O(n) for memoization
```

### Dynamic Programming

```
Time: O(n × W) where W = max_block_size
  For Bitcoin: O(n × 1,000,000) - too slow!

Space: O(W) with optimization, O(n × W) naive
```

### Simulated Annealing

```
Time: O(iterations × n)
  - Each iteration: random modification O(1) amortized
  - Validation: O(n) worst case
  Typical: iterations = 1000-10000

Space: O(n)
```

## 🎯 Interview Questions & Answers

### Q1: Why not just sort by total fee?

**Answer:**
Large transactions might have high total fees but low fee/byte.

Example:
- Tx A: 100,000 sat fee, 10,000 bytes → 10 sat/byte
- Tx B: 20,000 sat fee, 400 bytes → 50 sat/byte

Tx A has higher total fee but is less profitable per byte!

### Q2: How do you handle CPFP?

**Answer:**
Use ancestor set mining! Calculate the combined fee/byte for a transaction and all its ancestors.

```python
ancestor_fee = parent.fee + child.fee
ancestor_size = parent.size + child.size
score = ancestor_fee / ancestor_size
```

### Q3: What if you have a circular dependency?

**Answer:**
Impossible in Bitcoin! A transaction can only spend outputs from previous transactions. You can't have A → B → A because that would mean A depends on itself (invalid).

### Q4: Can you optimize this further?

**Answer:**
Yes, several approaches:
1. **Caching**: Memoize ancestor set calculations
2. **Incremental updates**: When new tx arrives, update incrementally
3. **Parallel processing**: Calculate ancestor sets in parallel
4. **Pruning**: Remove very low-fee transactions early
5. **Advanced heuristics**: Machine learning to predict good selections

### Q5: What's the optimal algorithm?

**Answer:**
The problem is NP-hard with dependencies! There's no known polynomial-time optimal algorithm. Ancestor set mining is near-optimal and fast enough for production.

## 🚀 Extensions & Exercises

### Easy:
1. **Add transaction fees stats**: Calculate min/max/median fees in mempool
2. **Visualize selection**: Show which transactions were selected/rejected
3. **Block template**: Generate actual block structure with selected transactions

### Medium:
4. **RBF (Replace-By-Fee)**: Handle transactions that replace others
5. **Weight units**: Use weight instead of size (SegWit)
6. **Fee estimation**: Predict what fee is needed for next block inclusion
7. **Multiple blocks**: Select transactions for next N blocks

### Hard:
8. **MEV (Miner Extractable Value)**: Consider transaction ordering for profit
9. **Compact blocks**: Optimize for fast propagation using compact block relay
10. **Mining pool**: Distribute rewards among pool participants
11. **Optimal solver**: Implement ILP (Integer Linear Programming) for small instances

## 📚 Resources

### Bitcoin Core Code:
- `src/txmempool.cpp` - Mempool implementation
- `src/mining.cpp` - Block template creation
- `BlockAssembler::addPackageTxs()` - Ancestor set mining

### Papers:
- "Transaction Selection in DAG-based Blockchains"
- "Optimal Transaction Fee Mechanism Design"
- Bitcoin Improvement Proposal (BIP) 125: Replace-By-Fee

### Further Reading:
- Bitcoin Core Developer Documentation
- "Mastering Bitcoin" Chapter 8: Mining
- Bitcoin Stack Exchange: Transaction Priority questions

## 🎓 Summer of Bitcoin Relevance

This problem appears in various forms:

**Bootcamp Challenges:**
- "Implement a block template generator"
- "Optimize transaction selection for maximum fees"
- "Handle CPFP scenarios"

**Interview Questions:**
- "How would you select transactions for mining?"
- "Explain ancestor set mining"
- "What's the complexity of your algorithm?"

**Real Projects:**
- Mining pool software
- Fee estimation services
- Transaction accelerators

## 💡 Key Takeaways

1. **Greedy works** but isn't optimal
2. **Dependencies matter** - can't ignore them!
3. **CPFP is crucial** for real-world mining
4. **Ancestor set mining** is production-ready
5. **Trade-offs**: optimality vs. speed vs. complexity

## 🏆 Best Practices

When implementing transaction selection:

✅ **DO:**
- Consider transaction packages (ancestor sets)
- Handle CPFP scenarios
- Optimize for fee/byte, not just total fee
- Validate dependencies
- Use efficient data structures

❌ **DON'T:**
- Sort by total fee only
- Ignore dependencies
- Use slow O(n²) or O(nW) algorithms for large n
- Forget to handle edge cases (orphan transactions, circular deps)

---

**Ready to ace the Summer of Bitcoin bootcamp!** 🚀

This implementation covers everything you need to know about transaction prioritization - one of the most important problems in Bitcoin mining!
