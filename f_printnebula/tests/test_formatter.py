# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import unittest
from datetime import datetime
from f_printnebula.engine.formatter import FormatterEngine


class TestFormatterEngine(unittest.TestCase):
	"""Test cases for FormatterEngine"""

	def setUp(self):
		"""Set up formatter instance"""
		self.formatter = FormatterEngine()

	def test_format_currency(self):
		"""Test currency formatting"""
		result = self.formatter.format(1234.56, "currency")
		self.assertIn("1,234.56", result)

	def test_format_number(self):
		"""Test number formatting"""
		result = self.formatter.format(1234.567, "number:2")
		self.assertIn("1,234.57", result)

	def test_format_int(self):
		"""Test integer formatting"""
		result = self.formatter.format(1234.567, "int")
		self.assertEqual(result, "1234")

	def test_format_percent(self):
		"""Test percentage formatting"""
		result = self.formatter.format(15.5, "percent:1")
		self.assertEqual(result, "15.5%")

	def test_format_upper(self):
		"""Test uppercase transformation"""
		result = self.formatter.format("hello world", "upper")
		self.assertEqual(result, "HELLO WORLD")

	def test_format_lower(self):
		"""Test lowercase transformation"""
		result = self.formatter.format("HELLO WORLD", "lower")
		self.assertEqual(result, "hello world")

	def test_format_title(self):
		"""Test title case transformation"""
		result = self.formatter.format("hello world", "title")
		self.assertEqual(result, "Hello World")

	def test_format_round(self):
		"""Test rounding"""
		result = self.formatter.format(123.456, "round:2")
		self.assertEqual(result, "123.46")

	def test_format_round_no_decimals(self):
		"""Test rounding to integer"""
		result = self.formatter.format(123.456, "round:0")
		self.assertEqual(result, "123")

	def test_format_default_with_value(self):
		"""Test default formatter with existing value"""
		result = self.formatter.format("existing", "default:N/A")
		self.assertEqual(result, "existing")

	def test_format_default_with_empty(self):
		"""Test default formatter with empty value"""
		result = self.formatter.format("", "default:N/A")
		self.assertEqual(result, "N/A")

	def test_format_default_with_none(self):
		"""Test default formatter with None value"""
		result = self.formatter.format(None, "default:N/A")
		self.assertEqual(result, "N/A")

	def test_unknown_formatter(self):
		"""Test unknown formatter (should return value as-is)"""
		result = self.formatter.format("test", "unknown_formatter")
		self.assertEqual(result, "test")

	def test_none_value(self):
		"""Test formatting None value"""
		result = self.formatter.format(None, "currency")
		self.assertEqual(result, "")

	def test_empty_string_value(self):
		"""Test formatting empty string"""
		result = self.formatter.format("", "upper")
		self.assertEqual(result, "")


class TestFormatterEdgeCases(unittest.TestCase):
	"""Test edge cases for FormatterEngine"""

	def test_invalid_number_format(self):
		"""Test invalid number for currency format"""
		formatter = FormatterEngine()
		result = formatter.format("not a number", "currency")
		# Should handle gracefully
		self.assertIsInstance(result, str)

	def test_chained_formatters_concept(self):
		"""Test concept of multiple formatters (note: not implemented yet)"""
		# This is a future enhancement idea
		# result = formatter.format("hello", "upper|default:N/A")
		pass


if __name__ == "__main__":
	unittest.main()
