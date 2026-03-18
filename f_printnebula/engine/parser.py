# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import re
import frappe
from typing import Dict, Any, Optional


class VariableParser:
	"""
	Parser for handling curly-brace variables in templates
	Supports: {field}, {nested.field}, {field|formatter}, {?condition}...{/condition}
	"""

	def __init__(self, doc: Dict[str, Any], mappings: Optional[Dict] = None):
		"""
		Initialize parser with document and field mappings

		Args:
			doc: Document data as dictionary
			mappings: Optional field mappings dictionary
		"""
		self.doc = doc
		self.mappings = mappings or {}

	def parse(self, content: str) -> str:
		"""
		Parse template content and replace variables

		Args:
			content: Template content with variables

		Returns:
			Parsed content with variables replaced
		"""
		if not content:
			return ""

		# Parse conditional blocks first
		content = self.parse_conditionals(content)

		# Parse regular variables
		content = self.parse_variables(content)

		return content

	def parse_variables(self, content: str) -> str:
		"""
		Parse and replace {field} and {field|formatter} variables

		Args:
			content: Content with variables

		Returns:
			Content with variables replaced
		"""
		# Pattern: {field_name} or {field_name|formatter:args}
		pattern = r'\{([a-zA-Z0-9_.]+)(?:\|([a-zA-Z0-9_:]+(?::[^}]+)?))?\}'

		def replace_variable(match):
			field_path = match.group(1)
			formatter = match.group(2)

			# Get field value
			value = self.get_field_value(field_path)

			# Apply formatter if specified
			if formatter and value is not None:
				from .formatter import FormatterEngine
				formatter_engine = FormatterEngine()
				value = formatter_engine.format(value, formatter)

			# Convert None to empty string
			return str(value) if value is not None else ""

		return re.sub(pattern, replace_variable, content)

	def parse_conditionals(self, content: str) -> str:
		"""
		Parse conditional blocks: {?field}...{/field}

		Args:
			content: Content with conditional blocks

		Returns:
			Content with conditionals resolved
		"""
		# Pattern: {?field_name}content{/field_name}
		pattern = r'\{\?([a-zA-Z0-9_.]+)(?:([=!<>]+)([^}]+))?\}(.*?)\{/\1\}'

		def replace_conditional(match):
			field_path = match.group(1)
			operator = match.group(2)
			compare_value = match.group(3)
			inner_content = match.group(4)

			# Get field value
			value = self.get_field_value(field_path)

			# Evaluate condition
			show_content = False

			if operator and compare_value:
				# Comparison operator specified
				show_content = self.evaluate_comparison(value, operator, compare_value.strip())
			else:
				# Boolean check - show if field has truthy value
				show_content = bool(value)

			return inner_content if show_content else ""

		return re.sub(pattern, replace_conditional, content, flags=re.DOTALL)

	def get_field_value(self, field_path: str) -> Any:
		"""
		Get field value from document with support for nested fields

		Args:
			field_path: Field path (e.g., "name" or "customer.customer_name")

		Returns:
			Field value or None
		"""
		# Check if field is mapped
		if field_path in self.mappings:
			field_path = self.mappings[field_path]

		# Handle nested fields
		if '.' in field_path:
			return self.get_nested_field(field_path)

		# Direct field access
		return self.doc.get(field_path)

	def get_nested_field(self, field_path: str) -> Any:
		"""
		Get nested field value (e.g., customer.customer_name)

		Args:
			field_path: Dot-separated field path

		Returns:
			Field value or None
		"""
		parts = field_path.split('.')
		current_value = self.doc

		for part in parts:
			if isinstance(current_value, dict):
				current_value = current_value.get(part)
			elif isinstance(current_value, str):
				# Link field - fetch the linked document
				try:
					# Get the doctype from meta
					meta = frappe.get_meta(self.doc.get('doctype'))
					field_meta = meta.get_field(parts[0])
					if field_meta and field_meta.fieldtype == 'Link':
						linked_doc = frappe.get_doc(field_meta.options, current_value)
						current_value = linked_doc.get(part)
					else:
						return None
				except Exception:
					return None
			else:
				return None

			if current_value is None:
				break

		return current_value

	def evaluate_comparison(self, value: Any, operator: str, compare_value: str) -> bool:
		"""
		Evaluate comparison operation

		Args:
			value: Field value
			operator: Comparison operator (=, !=, >, <, >=, <=)
			compare_value: Value to compare against

		Returns:
			Boolean result of comparison
		"""
		# Convert to string for comparison and sanitize input
		import html
		value_str = str(value) if value is not None else ""
		compare_str = html.escape(str(compare_value).strip())

		# Try numeric comparison if both are numbers
		try:
			value_num = float(value_str)
			compare_num = float(compare_str)

			if operator == '=' or operator == '==':
				return value_num == compare_num
			elif operator == '!=':
				return value_num != compare_num
			elif operator == '>':
				return value_num > compare_num
			elif operator == '<':
				return value_num < compare_num
			elif operator == '>=':
				return value_num >= compare_num
			elif operator == '<=':
				return value_num <= compare_num
		except (ValueError, TypeError):
			# Fall back to string comparison
			if operator == '=' or operator == '==':
				return value_str == compare_str
			elif operator == '!=':
				return value_str != compare_str

		return False
