import timeit
from functools import lru_cache
import matplotlib.pyplot as plt

# ------------------------------
# 1. LRU-BASED FIBONACCI
# ------------------------------
@lru_cache(maxsize=None)
def fibonacci_lru(n: int) -> int:
    """
    Compute the nth Fibonacci number using recursion
    and Python's built-in @lru_cache decorator.
    """
    if n < 2:
        return n
    return fibonacci_lru(n - 1) + fibonacci_lru(n - 2)

# ------------------------------
# 2. SPLAY TREE IMPLEMENTATION
# ------------------------------
class SplayTreeNode:
    """
    A simple node for a Splay Tree storing (key, value).
    In our case: key = n, value = fibonacci(n).
    """
    __slots__ = ('key', 'value', 'left', 'right', 'parent')
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.parent = None

class SplayTree:
    """
    A basic Splay Tree implementation to store computed Fibonacci values.
    On every access (search/insert), the accessed node is splayed (moved) to the root.
    """
    def __init__(self):
        self.root = None

    def _rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left:
            y.left.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _rotate_right(self, x):
        y = x.left
        x.left = y.right
        if y.right:
            y.right.parent = x
        y.parent = x.parent
        if not x.parent:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def _splay(self, x):
        """
        Bring node x to the root of the tree.
        """
        while x.parent:
            if not x.parent.parent:
                # Zig step
                if x.parent.left == x:
                    self._rotate_right(x.parent)
                else:
                    self._rotate_left(x.parent)
            elif x.parent.left == x and x.parent.parent.left == x.parent:
                # Zig-zig step (right-right)
                self._rotate_right(x.parent.parent)
                self._rotate_right(x.parent)
            elif x.parent.right == x and x.parent.parent.right == x.parent:
                # Zig-zig step (left-left)
                self._rotate_left(x.parent.parent)
                self._rotate_left(x.parent)
            elif x.parent.left == x and x.parent.parent.right == x.parent:
                # Zig-zag step (right-left)
                self._rotate_right(x.parent)
                self._rotate_left(x.parent)
            else:
                # Zig-zag step (left-right)
                self._rotate_left(x.parent)
                self._rotate_right(x.parent)

    def search(self, key) -> SplayTreeNode:
        """
        Search for a node with the given key. If found, splay it. 
        If not found, splay the last accessed node.
        """
        node = self.root
        prev = None
        while node:
            prev = node
            if key == node.key:
                self._splay(node)
                return node
            elif key < node.key:
                node = node.left
            else:
                node = node.right
        if prev:
            self._splay(prev)
        return None  # key not found

    def insert(self, key, value):
        """
        Insert a new node (key, value) into the Splay Tree, then splay it to root.
        """
        if not self.root:
            self.root = SplayTreeNode(key, value)
            return
        node = self.root
        parent = None
        while node:
            parent = node
            if key < node.key:
                node = node.left
            elif key > node.key:
                node = node.right
            else:
                # If key already exists, just update the value and splay
                node.value = value
                self._splay(node)
                return
        new_node = SplayTreeNode(key, value)
        new_node.parent = parent
        if key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node
        self._splay(new_node)

# ------------------------------
# 3. SPLAY-BASED FIBONACCI
# ------------------------------
def fibonacci_splay(n: int, tree: SplayTree) -> int:
    """
    Compute the nth Fibonacci number using a Splay Tree to cache previously computed values.
    - If 'n' is found in the tree, return the cached value.
    - Otherwise compute recursively, store in tree, and return.
    """
    node = tree.search(n)
    if node:
        # Found it in the tree
        return node.value
    # Not found, compute recursively
    if n < 2:
        fib_val = n
    else:
        fib_val = fibonacci_splay(n - 1, tree) + fibonacci_splay(n - 2, tree)
    tree.insert(n, fib_val)
    return fib_val

# ------------------------------
# 4. PERFORMANCE COMPARISON
# ------------------------------
def measure_execution_times(ns):
    """
    Measures execution times for fibonacci_lru and fibonacci_splay for given list of n-values.
    :param ns: list of integer n-values (e.g., [0, 50, 100, ...]).
    :return: two lists of times: times_lru, times_splay
    """
    times_lru = []
    times_splay = []

    # We create a single SplayTree instance for all Fibonacci computations
    # because we want the caching effect to persist across calls.
    tree = SplayTree()

    # Clear LRU cache before measurement
    fibonacci_lru.cache_clear()

    # We'll use 'timeit.timeit' with a small number of repeats to get an average
    for n in ns:
        # LRU measurement
        setup_code_lru = (
            "from __main__ import fibonacci_lru\n"
            f"n = {n}"
        )
        stmt_lru = "fibonacci_lru(n)"
        time_lru = timeit.timeit(stmt=stmt_lru, setup=setup_code_lru, number=5)
        avg_lru = time_lru / 5.0
        times_lru.append(avg_lru)

        # Splay measurement
        setup_code_splay = (
            "from __main__ import fibonacci_splay, SplayTreeNode, SplayTree\n"
            f"tree_arg = tree\n"  # we need the same 'tree' across calls
            f"n = {n}"
        )
        # Because we reference the same object `tree` from measure_execution_times scope,
        # we can do it by using 'global' or direct referencing. We'll demonstrate the logic.
        # We'll define a snippet to call fibonacci_splay(n, tree_arg).
        stmt_splay = "fibonacci_splay(n, tree_arg)"
        # We'll rely on the fact that Python 3 closures can capture 'tree' var, 
        # or you can do a trick with partial. 
        # For timeit to see 'tree_arg', it either needs to be global or in the setup_code_splay.
        # We put 'tree_arg = tree' into the main code, but let's be consistent with global usage.
        # It's a simplified approach; in a real scenario, you'd pass references differently.
        
        # Because timeit won't directly see `tree` unless we do something explicit,
        # we will define a function inside measure_execution_times:
        def fib_splay_call():
            return fibonacci_splay(n, tree)

        # We measure time with timeit but use a lambda or direct function call
        time_splay = timeit.timeit(
            fib_splay_call,
            number=5
        )
        avg_splay = time_splay / 5.0
        times_splay.append(avg_splay)

    return times_lru, times_splay

def main():
    # 4.1 Create the sequence of n
    ns = list(range(0, 1001, 50))  # 0, 50, 100, 150, ..., 950, 1000
    # If you only want up to 950, do: range(0, 951, 50)

    # 4.2 Measure execution times
    times_lru, times_splay = measure_execution_times(ns)

    # 4.3 Build the comparison plot
    plt.figure(figsize=(8, 5))
    plt.plot(ns, times_lru, marker='o', label='LRU Cache')
    plt.plot(ns, times_splay, marker='x', label='Splay Tree')
    plt.title('Comparison of Fibonacci Computation with LRU Cache vs Splay Tree')
    plt.xlabel('Fibonacci number index (n)')
    plt.ylabel('Execution time (seconds)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # 4.4 Print a textual table
    print(f"{'n':<10} {'LRU Cache Time (s)':<20} {'Splay Tree Time (s)':<20}")
    print('-' * 54)
    for n, t_lru, t_splay in zip(ns, times_lru, times_splay):
        print(f"{n:<10} {t_lru:<20.8f} {t_splay:<20.8f}")

    # 4.5 Draw short conclusions (example):
    # Compare the times for large n (like 950 or 1000)
    # This is just a placeholder for any further analysis you might do:
    print("\nConclusions:")
    print(" - LRU Cache often performs very well due to Python's built-in memoization.")
    print(" - Splay Tree may show different performance characteristics, "
          "especially if the same values are accessed repeatedly.")

if __name__ == "__main__":
    main()
