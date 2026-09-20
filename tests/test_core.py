"""Tests for memoize.core.Memoizer."""

import unittest

from memoize import Memoizer


class TestMemoizer(unittest.TestCase):
    def test_caches_simple_calls(self):
        calls = []

        def f(x):
            calls.append(x)
            return x * 2

        m = Memoizer(f)
        self.assertEqual(m(3), 6)
        self.assertEqual(m(3), 6)
        self.assertEqual(calls, [3])
        self.assertEqual(m.cache_info(), (1, 1, 128, 1))

    def test_custom_key_func(self):
        calls = []

        def f(a, b):
            calls.append((a, b))
            return a + b

        def key_func(a, b):
            return a

        m = Memoizer(f, key_func=key_func)
        self.assertEqual(m(1, 10), 11)
        self.assertEqual(m(1, 20), 11)
        self.assertEqual(calls, [(1, 10)])

    def test_kwargs_are_part_of_default_key(self):
        calls = []

        def f(a, b=0):
            calls.append((a, b))
            return a + b

        m = Memoizer(f)
        self.assertEqual(m(5, b=1), 6)
        self.assertEqual(m(5, b=1), 6)
        self.assertEqual(m(5, b=2), 7)
        self.assertEqual(calls, [(5, 1), (5, 2)])

    def test_max_size_evicts_oldest(self):
        calls = []

        def f(x):
            calls.append(x)
            return x

        m = Memoizer(f, max_size=2)
        m(1)
        m(2)
        m(3)
        self.assertEqual(len(m._cache), 2)
        self.assertNotIn(1, m._cache)
        self.assertIn((2,), m._cache)
        self.assertIn((3,), m._cache)

    def test_clear_empties_cache(self):
        def f(x):
            return x

        m = Memoizer(f)
        m(1)
        m.clear()
        self.assertEqual(m.cache_info()[3], 0)

    def test_unhashable_key_not_cached(self):
        def f(x):
            return len(x)

        m = Memoizer(f)
        lst = [1, 2, 3]
        self.assertEqual(m(lst), 3)
        self.assertEqual(m(lst), 3)
        self.assertEqual(m.misses, 2)
        self.assertEqual(m.cache_info()[3], 0)

    def test_invalid_max_size(self):
        with self.assertRaises(ValueError):
            Memoizer(lambda x: x, max_size=0)
        with self.assertRaises(ValueError):
            Memoizer(lambda x: x, max_size=-1)
        with self.assertRaises(ValueError):
            Memoizer(lambda x: x, max_size=True)

    def test_recursive_call_does_not_deadlock(self):
        def fib(n):
            if n < 2:
                return n
            return fib_memo(n - 1) + fib_memo(n - 2)

        fib_memo = Memoizer(fib)
        self.assertEqual(fib_memo(10), 55)


if __name__ == "__main__":
    unittest.main()
