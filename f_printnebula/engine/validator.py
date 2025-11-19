# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
import json
import re
from jinja2 import Environment, BaseLoader, TemplateSyntaxError
from typing import Dict, List


class TemplateValidator:
	"""Validator for template syntax and fields"""

	def __init__(self, template):
		"""
		Initialize validator with template

		Args:
			template: PrintNebula Template document
		"""
		self.template = template
		self.errors = []
		self.warnings = []
		self.meta = frappe.get_meta(template.doctype_link) if template.doctype_link else None

	def validate(self) -> Dict:
		"""
		Validate template

		Returns:
			Dictionary with validation results
		"""
		self.errors = []
		self.warnings = []

		# Validate basic info
		self.validate_basic_info()

		# Validate field mappings
		self.validate_field_mappings()

		# Validate child table config
		self.validate_child_table_config()

		# Validate Jinja2 syntax
		self.validate_jinja_syntax()

		# Validate field references
		self.validate_field_references()

		# Validate conditions
		self.validate_conditions_syntax()

		return {
			'valid': len(self.errors) == 0,
			'errors': self.errors,
			'warnings': self.warnings
		}

	def validate_basic_info(self):
		"""Validate basic template information"""
		if not self.template.template_name:
			self.errors.append("Template name is required")

		if not self.template.doctype_link:
			self.errors.append("Doctype link is required")

		if not self.template.header and not self.template.body and not self.template.footer:
			self.warnings.append("Template has no content in any section")

	def validate_field_mappings(self):
		"""Validate field mappings JSON"""
		if not self.template.field_mappings:
			return

		try:
			mappings = json.loads(self.template.field_mappings)

			if not isinstance(mappings, dict):
				self.errors.append("Field mappings must be a JSON object")
				return

			# Validate mapped fields exist
			for alias, fieldname in mappings.items():
				if isinstance(fieldname, str) and self.meta:
					if not self.meta.get_field(fieldname):
						self.warnings.append(f"Mapped field '{fieldname}' (alias: '{alias}') not found in {self.template.doctype_link}")

		except json.JSONDecodeError as e:
			self.errors.append(f"Invalid JSON in field mappings: {str(e)}")

	def validate_child_table_config(self):
		"""Validate child table configuration"""
		if not self.template.child_table_config:
			return

		try:
			config = json.loads(self.template.child_table_config)

			if not isinstance(config, dict):
				self.errors.append("Child table config must be a JSON object")
				return

			# Validate child tables exist
			if self.meta:
				for table_name, fields in config.items():
					table_field = self.meta.get_field(table_name)

					if not table_field:
						self.warnings.append(f"Child table '{table_name}' not found in {self.template.doctype_link}")
					elif table_field.fieldtype != 'Table':
						self.errors.append(f"Field '{table_name}' is not a table field")

		except json.JSONDecodeError as e:
			self.errors.append(f"Invalid JSON in child table config: {str(e)}")

	def validate_jinja_syntax(self):
		"""Validate Jinja2 syntax in template sections"""
		sections = {
			'Header': self.template.header,
			'Body': self.template.body,
			'Footer': self.template.footer
		}

		env = Environment(loader=BaseLoader())

		for section_name, content in sections.items():
			if not content:
				continue

			try:
				# Try to parse Jinja2 template
				env.from_string(content)
			except TemplateSyntaxError as e:
				self.errors.append(f"{section_name} has Jinja2 syntax error: {str(e)}")

	def validate_field_references(self):
		"""Validate that fields referenced in template exist"""
		if not self.meta:
			return

		# Get all field references from template
		all_content = f"{self.template.header or ''} {self.template.body or ''} {self.template.footer or ''}"

		# Find all {fieldname} references
		pattern = r'\{([a-zA-Z0-9_]+)(?:\|[^}]+)?\}'
		matches = re.findall(pattern, all_content)

		# Check each field
		for fieldname in set(matches):
			# Skip Jinja2 keywords
			if fieldname in ['for', 'if', 'else', 'endif', 'endfor', 'row', 'loop']:
				continue

			# Check if field exists
			if not self.meta.get_field(fieldname):
				# Check if it's a standard field
				if fieldname not in ['name', 'owner', 'creation', 'modified', 'modified_by', 'docstatus']:
					self.warnings.append(f"Field '{fieldname}' not found in {self.template.doctype_link}")

	def validate_conditions_syntax(self):
		"""Validate conditions JSON syntax"""
		if not self.template.conditions:
			return

		try:
			conditions = json.loads(self.template.conditions)

			if not isinstance(conditions, list):
				self.errors.append("Conditions must be a JSON array")
				return

			# Validate each condition
			for i, condition in enumerate(conditions):
				if not isinstance(condition, dict):
					self.errors.append(f"Condition {i+1} must be a JSON object")
					continue

				if 'section' not in condition:
					self.errors.append(f"Condition {i+1} missing 'section' field")

				if 'show_if' not in condition:
					self.errors.append(f"Condition {i+1} missing 'show_if' field")

		except json.JSONDecodeError as e:
			self.errors.append(f"Invalid JSON in conditions: {str(e)}")
