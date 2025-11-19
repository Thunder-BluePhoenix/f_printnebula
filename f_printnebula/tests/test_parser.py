# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import unittest
from f_printnebula.engine.parser import VariableParser


class TestVariableParser(unittest.TestCase):
	"""Test cases for VariableParser"""

	def setUp(self):
		"""Set up test data"""
		self.doc = {
			"name": "SI-00001",
			"customer_name": "John Doe",
			"posting_date": "2025-11-18",
			"grand_total": 1234.56,
			"status": "Submitted",
			"is_paid": 1,
			"discount_amount": 100,
			"custom_field": None
		}
		self.parser = VariableParser(self.doc)

	def test_simple_variable_parsing(self):
		"""Test simple {field} parsing"""
		content = "Invoice: {name}, Customer: {customer_name}"
		result = self.parser.parse(content)
		self.assertEqual(result, "Invoice: SI-00001, Customer: John Doe")

	def test_missing_field_handling(self):
		"""Test handling of missing fields"""
		content = "Field: {nonexistent_field}"
		result = self.parser.parse(content)
		self.assertEqual(result, "Field: ")

	def test_none_field_handling(self):
		"""Test handling of None values"""
		content = "Custom: {custom_field}"
		result = self.parser.parse(content)
		self.assertEqual(result, "Custom: ")

	def test_conditional_true(self):
		"""Test conditional rendering when true"""
		content = "{?is_paid}PAID{/is_paid}"
		result = self.parser.parse(content)
		self.assertEqual(result, "PAID")

	def test_conditional_false(self):
		"""Test conditional rendering when false"""
		self.doc["is_paid"] = 0
		parser = VariableParser(self.doc)
		content = "{?is_paid}PAID{/is_paid}"
		result = parser.parse(content)
		self.assertEqual(result, "")

	def test_conditional_with_comparison(self):
		"""Test conditional with comparison operator"""
		content = "{?status=Submitted}Approved{/status}"
		result = self.parser.parse(content)
		self.assertEqual(result, "Approved")

	def test_conditional_with_comparison_false(self):
		"""Test conditional with comparison operator (false)"""
		content = "{?status=Draft}In Progress{/status}"
		result = self.parser.parse(content)
		self.assertEqual(result, "")

	def test_numeric_comparison_greater(self):
		"""Test numeric comparison (greater than)"""
		content = "{?discount_amount>50}Big Discount{/discount_amount}"
		result = self.parser.parse(content)
		self.assertEqual(result, "Big Discount")

	def test_numeric_comparison_less(self):
		"""Test numeric comparison (less than)"""
		content = "{?discount_amount<50}Small Discount{/discount_amount}"
		result = self.parser.parse(content)
		self.assertEqual(result, "")

	def test_field_mappings(self):
		"""Test field mappings/aliases"""
		mappings = {
			"inv_no": "name",
			"cust": "customer_name"
		}
		parser = VariableParser(self.doc, mappings)
		content = "Invoice: {inv_no}, Customer: {cust}"
		result = parser.parse(content)
		self.assertEqual(result, "Invoice: SI-00001, Customer: John Doe")

	def test_multiple_variables(self):
		"""Test multiple variables in one template"""
		content = """
		Invoice: {name}
		Customer: {customer_name}
		Total: {grand_total}
		Status: {status}
		"""
		result = self.parser.parse(content)
		self.assertIn("SI-00001", result)
		self.assertIn("John Doe", result)
		self.assertIn("1234.56", result)
		self.assertIn("Submitted", result)


class TestVariableParserEdgeCases(unittest.TestCase):
	"""Test edge cases for VariableParser"""

	def test_empty_content(self):
		"""Test with empty content"""
		parser = VariableParser({})
		result = parser.parse("")
		self.assertEqual(result, "")

	def test_none_content(self):
		"""Test with None content"""
		parser = VariableParser({})
		result = parser.parse(None)
		self.assertEqual(result, "")

	def test_no_variables(self):
		"""Test content without variables"""
		parser = VariableParser({})
		content = "This is plain text without variables"
		result = parser.parse(content)
		self.assertEqual(result, content)

	def test_malformed_braces(self):
		"""Test with malformed braces"""
		parser = VariableParser({"name": "Test"})
		content = "Name: {name and other stuff"
		result = parser.parse(content)
		# Should not crash, just leave malformed syntax as-is
		self.assertIn("{name and other stuff", result)

	def test_nested_braces(self):
		"""Test with nested braces"""
		parser = VariableParser({"outer": "value"})
		content = "{outer} and {{inner}}"
		result = parser.parse(content)
		self.assertIn("value", result)


if __name__ == "__main__":
	unittest.main()
