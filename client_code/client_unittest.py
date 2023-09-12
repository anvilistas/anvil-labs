# SPDX-License-Identifier: MIT
# Copyright (c) 2021 anvilistas

__version__ = "0.0.1"

"""This is a test module."""
import unittest


class TestClass(unittest.TestCase):
    """This is a testclass."""

    def setUp(self):
        self.var_1 = True
        print("This is a setup")

    def tearDown(self):
        print("This is a teardown")

    def test_method_1(self):
        """Test Method 1."""
        try:
            assert False
        except AssertionError:
            pass

    def test_method_2(self):
        """Test Method 2."""
        pass

    def test_method_final(self):
        """Final passing test."""
        assert(self.var_1)
