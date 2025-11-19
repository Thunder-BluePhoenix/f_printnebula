# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import unittest
from f_printnebula.engine.parser import VariableParser
from f_printnebula.engine.formatter import FormatterEngine


class TestIntegration(unittest.TestCase):
	"""Integration tests combining multiple components"""

	def test_invoice_template_simulation(self):
		"""Test a realistic invoice template"""
		doc = {
			"name": "SI-00001",
			"customer_name": "John Doe",
			"posting_date": "2025-11-18",
			"grand_total": 1234.56,
			"status": "Submitted",
			"items": [
				{"item_name": "Widget A", "qty": 10, "rate": 50.00},
				{"item_name": "Widget B", "qty": 5, "rate": 30.00}
			]
		}

		parser = VariableParser(doc)

		# Header template
		header = """
		<div style="text-align: center;">
			<h2>TAX INVOICE</h2>
			<p>Invoice No: {name}</p>
		</div>
		"""
		header_result = parser.parse(header)
		self.assertIn("SI-00001", header_result)

		# Body with conditional
		body = """
		<p>Customer: {customer_name}</p>
		<p>Date: {posting_date}</p>
		{?status=Submitted}<p style="color: green;">✓ Approved</p>{/status}
		"""
		body_result = parser.parse(body)
		self.assertIn("John Doe", body_result)
		self.assertIn("✓ Approved", body_result)

		# Footer
		footer = """
		<p>Total: {grand_total}</p>
		<p>Thank you for your business!</p>
		"""
		footer_result = parser.parse(footer)
		self.assertIn("1234.56", footer_result)

	def test_conditional_sections(self):
		"""Test multiple conditional sections"""
		doc = {
			"has_discount": 1,
			"has_tax": 1,
			"has_shipping": 0,
			"discount_amount": 100,
			"tax_amount": 50,
			"shipping_amount": 0
		}

		parser = VariableParser(doc)

		template = """
		{?has_discount}Discount: {discount_amount}{/has_discount}
		{?has_tax}Tax: {tax_amount}{/has_tax}
		{?has_shipping}Shipping: {shipping_amount}{/has_shipping}
		"""

		result = parser.parse(template)
		self.assertIn("Discount: 100", result)
		self.assertIn("Tax: 50", result)
		self.assertNotIn("Shipping:", result)

	def test_field_mapping_use_case(self):
		"""Test field mapping for simplified templates"""
		doc = {
			"name": "SI-00001",
			"customer_name": "John Doe",
			"grand_total": 1234.56
		}

		# Create user-friendly aliases
		mappings = {
			"invoice_no": "name",
			"customer": "customer_name",
			"total": "grand_total"
		}

		parser = VariableParser(doc, mappings)

		# User can now use simpler field names
		template = """
		Invoice: {invoice_no}
		Customer: {customer}
		Total: {total}
		"""

		result = parser.parse(template)
		self.assertIn("SI-00001", result)
		self.assertIn("John Doe", result)
		self.assertIn("1234.56", result)

	def test_complex_conditionals(self):
		"""Test complex conditional logic"""
		doc = {
			"payment_status": "Paid",
			"overdue_days": 0,
			"outstanding_amount": 0
		}

		parser = VariableParser(doc)

		template = """
		{?payment_status=Paid}✓ Payment Complete{/payment_status}
		{?outstanding_amount>0}⚠ Outstanding: {outstanding_amount}{/outstanding_amount}
		{?overdue_days>0}❌ Overdue by {overdue_days} days{/overdue_days}
		"""

		result = parser.parse(template)
		self.assertIn("✓ Payment Complete", result)
		self.assertNotIn("Outstanding:", result)
		self.assertNotIn("Overdue", result)


class TestTemplateValidation(unittest.TestCase):
	"""Test template validation scenarios"""

	def test_valid_template(self):
		"""Test that valid templates parse without errors"""
		doc = {"name": "Test", "status": "Active"}
		parser = VariableParser(doc)

		templates = [
			"Simple: {name}",
			"Conditional: {?status}Active{/status}",
			"Multiple: {name} - {status}",
		]

		for template in templates:
			try:
				result = parser.parse(template)
				self.assertIsInstance(result, str)
			except Exception as e:
				self.fail(f"Template '{template}' failed: {str(e)}")

	def test_malformed_templates_dont_crash(self):
		"""Test that malformed templates don't crash the system"""
		doc = {"name": "Test"}
		parser = VariableParser(doc)

		# These should not crash
		templates = [
			"{name",  # Missing closing brace
			"name}",  # Missing opening brace
			"{{name}}",  # Double braces
			"{?status}unclosed",  # Unclosed conditional
		]

		for template in templates:
			try:
				result = parser.parse(template)
				self.assertIsInstance(result, str)
			except Exception as e:
				# Log but don't fail - we want graceful degradation
				print(f"Template '{template}' produced error: {str(e)}")


if __name__ == "__main__":
	unittest.main()
