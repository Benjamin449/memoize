# Memoize

Memoize provides a `Memoizer` class that wraps a function and caches its results using a custom key function and a bounded FIFO store.

## Usage

```python
from memoize import Memoizer

def expensive_add(a, b):
    print("computing")
    return a + b

memoized = Memoizer(expensive_add, key_func=lambda a, b: (a, b), max_size=100)

print(memoized(1, 2))  # computing, 3
print(memoized(1, 2))  # 3 (cached)
```

## Why this library exists

Caching function results is a common need, but many caching utilities either use a fixed key strategy or rely on unbounded dictionaries. This library allows the caller to control how arguments map to cache keys, and it guarantees that the cache never grows beyond a chosen size. The trade-off is simplicity: the eviction policy is FIFO, not LRU or LFU, which keeps the implementation small and predictable.

## Edge case to be aware of

If the arguments or the custom key function produce an unhashable key, the function is called normally and the result is not cached. This avoids raising an exception for a situation that may be transient, but it means the same unhashable input will always be a cache miss.

## Exported names

- `Memoizer`
