import random
import time
from collections import OrderedDict

class LRUCache:
    """
    LRUCache(capacity=1000)

    A simple LRU (Least Recently Used) cache implementation based on OrderedDict.
    Stores computed sums for (L, R) segments. If the cache reaches the maximum 
    capacity, the least recently used element is evicted.
    """

    def __init__(self, capacity=1000):
        """
        Initialize the LRU cache with a specified capacity.
        
        :param capacity: Maximum number of items the cache can store.
        """
        self.capacity = capacity
        self.cache = OrderedDict()  # key: (L, R), value: sum for that range

    def get(self, key):
        """
        Retrieve a value from the cache by key and move it to the 
        'most recently used' position.

        :param key: A tuple (L, R) representing the segment of the array.
        :return: The cached sum if it exists, otherwise None.
        """
        if key not in self.cache:
            return None
        # Move this key to the end (most recently used).
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        """
        Store or update a key-value pair in the cache. 
        If adding the new item exceeds the capacity, the least recently used item is evicted.

        :param key: A tuple (L, R) representing the segment of the array.
        :param value: Computed sum for that segment.
        """
        # If the key already exists, move it to the end.
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value

        # Evict the least recently used item if capacity is exceeded.
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def invalidate(self, condition_func):
        """
        Remove cache entries that match a certain condition. 
        Typically used after an update operation that changes part of the array.

        :param condition_func: A function that takes (L, R) and returns True
                               if the entry should be removed.
        """
        keys_to_remove = [k for k in self.cache.keys() if condition_func(k)]
        for k in keys_to_remove:
            del self.cache[k]

def range_sum_no_cache(array, L, R):
    """
    Compute the sum of array elements from index L to R (inclusive)
    by simply iterating over the range. No caching involved.

    :param array: The array of integers.
    :param L: Start index (inclusive).
    :param R: End index (inclusive).
    :return: The sum of array[L : R+1].
    """
    total = 0
    for i in range(L, R+1):
        total += array[i]
    return total

def update_no_cache(array, index, value):
    """
    Update a single array element at the given index to a new value.
    No caching involved.

    :param array: The array of integers.
    :param index: The position in the array to be updated.
    :param value: The new value to store at array[index].
    """
    array[index] = value

def range_sum_with_cache(array, L, R, cache: LRUCache):
    """
    Compute the sum of array elements from L to R (inclusive) 
    using an LRU cache to store previously computed sums.
    
    :param array: The array of integers.
    :param L: Start index (inclusive).
    :param R: End index (inclusive).
    :param cache: An LRUCache object.
    :return: The sum of array[L : R+1], using the cache if available.
    """
    cached_sum = cache.get((L, R))
    if cached_sum is not None:
        return cached_sum

    # If not in the cache, compute and store it.
    total = 0
    for i in range(L, R+1):
        total += array[i]
    cache.put((L, R), total)
    return total

def update_with_cache(array, index, value, cache: LRUCache):
    """
    Update the array at a given index and invalidate any cached sums 
    that involve the updated index.

    :param array: The array of integers.
    :param index: The position in the array to be updated.
    :param value: The new value to store at array[index].
    :param cache: An LRUCache object, which will be invalidated
                  for all segments that include 'index'.
    """
    array[index] = value

    # Condition to find (L, R) segments that include 'index'.
    def invalidation_condition(interval):
        (start, end) = interval
        return start <= index <= end

    cache.invalidate(invalidation_condition)


def main():
    """
    Demonstrates the usage of the above functions and LRUCache
    by generating a random array and random queries (both Range and Update).
    Measures execution time with and without caching.
    Includes debug prints every 10,000 operations to indicate progress.
    """
    N = 100_000
    Q = 50_000
    K = 1000

    # 4.1 Generate a random array
    array = [random.randint(1, 100) for _ in range(N)]

    # 4.2 Generate a list of queries
    queries = []
    for _ in range(Q):
        query_type = random.choices(["Range", "Update"], weights=[0.7, 0.3], k=1)[0]
        if query_type == "Range":
            L = random.randint(0, N-1)
            R = random.randint(L, N-1)
            queries.append(("Range", L, R))
        else:
            idx = random.randint(0, N-1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))

    print("Starting execution WITHOUT cache...")
    start_no_cache = time.time()
    for i, q in enumerate(queries, start=1):
        if q[0] == "Range":
            _, L, R = q
            range_sum_no_cache(array, L, R)
        else:
            _, idx, val = q
            update_no_cache(array, idx, val)

        # Debug print every 10,000 queries
        if i % 10000 == 0:
            print(f"[NO CACHE] Processed {i} queries out of {Q}...")

    end_no_cache = time.time()
    no_cache_time = end_no_cache - start_no_cache

    # For a fair comparison, re-generate array and queries
    array = [random.randint(1, 100) for _ in range(N)]
    queries = []
    for _ in range(Q):
        query_type = random.choices(["Range", "Update"], weights=[0.7, 0.3], k=1)[0]
        if query_type == "Range":
            L = random.randint(0, N-1)
            R = random.randint(L, N-1)
            queries.append(("Range", L, R))
        else:
            idx = random.randint(0, N-1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))

    print("Starting execution WITH LRU cache...")
    lru_cache = LRUCache(capacity=K)
    start_with_cache = time.time()
    for i, q in enumerate(queries, start=1):
        if q[0] == "Range":
            _, L, R = q
            range_sum_with_cache(array, L, R, lru_cache)
        else:
            _, idx, val = q
            update_with_cache(array, idx, val, lru_cache)

        # Debug print every 10,000 queries
        if i % 10000 == 0:
            print(f"[LRU CACHE] Processed {i} queries out of {Q}...")

    end_with_cache = time.time()
    with_cache_time = end_with_cache - start_with_cache

    print(f"Execution time without cache: {no_cache_time:.2f} seconds")
    print(f"Execution time with LRU cache: {with_cache_time:.2f} seconds")

if __name__ == "__main__":
    main()
