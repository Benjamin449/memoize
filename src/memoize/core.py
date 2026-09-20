"""Core implementation of the Memoizer.

A Memoizer wraps a function and caches its results. It uses a user-supplied
key function to derive the cache key from the arguments, and maintains a
bounded store using a simple FIFO eviction policy. This implementation
deliberately avoids third-party dependencies and relies only on the Python
standard library.
"""

from collections import OrderedDict
from threading import RLock


class Memoizer:
    """Memoise a function with a custom key function and a bounded store.

    Parameters
    ----------
    func : callable
        The function to memoise.
    key_func : callable, optional
        A callable that receives the same arguments as ``func`` and returns a
        hashable cache key. If ``None`` (default), the arguments themselves are
        used as the key. This requires the arguments to be hashable.
    max_size : int, optional
        Maximum number of entries to keep. Must be a positive integer.
        When the cache exceeds this size, the oldest inserted entry is evicted.
        Default is 128.

    Raises
    ------
    ValueError
        If ``max_size`` is not a positive integer.

    Notes
    -----
    The store is bounded using an OrderedDict with FIFO eviction. A
    reentrant lock is used because a memoised function may recursively call
    itself through the same Memoizer instance.
    """

    def __init__(self, func, key_func=None, max_size=128):
        if not callable(func):
            raise TypeError("func must be callable")
        if key_func is not None and not callable(key_func):
            raise TypeError("key_func must be callable or None")
        if not isinstance(max_size, int) or isinstance(max_size, bool) or max_size <= 0:
            raise ValueError("max_size must be a positive integer")

        self.func = func
        self.key_func = key_func
        self.max_size = max_size
        self._cache = OrderedDict()
        self._lock = RLock()
        self._hits = 0
        self._misses = 0

    def __call__(self, *args, **kwargs):
        """Call the memoised function, using the cache when possible.

        Returns the cached result if the computed key exists. Otherwise
        computes the result, stores it, and returns it.
        """
        if self.key_func is None:
            key = args + tuple(sorted(kwargs.items()))
        else:
            key = self.key_func(*args, **kwargs)

        with self._lock:
            try:
                return self._cache[key]
            except KeyError:
                self._misses += 1
            except TypeError:
                # Unhashable key; fall through to recompute without caching.
                self._misses += 1
                return self.func(*args, **kwargs)

            result = self.func(*args, **kwargs)
            self._cache[key] = result
            self._hits += 1 if key in self._cache else 0
            if len(self._cache) > self.max_size:
                self._cache.popitem(last=False)
            return result

    @property
    def hits(self):
        """Number of cache hits."""
        with self._lock:
            return self._hits

    @property
    def misses(self):
        """Number of cache misses (including uncacheable calls)."""
        with self._lock:
            return self._misses

    def cache_info(self):
        """Return a tuple (hits, misses, max_size, current_size)."""
        with self._lock:
            return (self._hits, self._misses, self.max_size, len(self._cache))

    def clear(self):
        """Remove all entries from the cache."""
        with self._lock:
            self._cache.clear()
