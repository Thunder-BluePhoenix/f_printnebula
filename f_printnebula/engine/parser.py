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

		# Extract global Snippets first!
		content = self.parse_snippets(content)

		# Parse conditional blocks
		content = self.parse_conditionals(content)

		# Parse regular variables
		content = self.parse_variables(content)

		# Parse math operations {=qty * rate}
		content = self.parse_math(content)

		# Parse media (QR codes, barcodes)
		content = self.parse_media(content)

		return content

	def parse_snippets(self, content: str) -> str:
		"""
		Parse {snippet:MyName} and instantly replace logic pulling from database prior to generic parsing algorithms
		"""
		pattern = r'\{snippet:([^}]+)\}'

		def replace_snippet(match):
			snippet_name = match.group(1).strip()
			try:
				html_content = frappe.db.get_value("PrintNebula Snippet", snippet_name, "html_content")
				if html_content:
					# Support nested snippets flawlessly
					return self.parse_snippets(html_content)
				return f"<!-- Snippet '{snippet_name}' not found -->"
			except Exception as e:
				return f"<!-- Snippet '{snippet_name}' error: {str(e)} -->"

		return re.sub(pattern, replace_snippet, content)

	def parse_variables(self, content: str) -> str:
		"""
		Parse and replace {field} and {field|formatter} variables

		Args:
			content: Content with variables

		Returns:
			Content with variables replaced
		"""
		# Pattern: {field_name} or {field_name|formatter1|formatter2:args}
		pattern = r'\{([a-zA-Z0-9_.]+)(?:\|([^}]+))?\}'

		def replace_variable(match):
			field_path = match.group(1)
			formatters_str = match.group(2)

			# Get field value
			value = self.get_field_value(field_path)

			# Apply formatters sequentially if specified
			if formatters_str:
				from .formatter import FormatterEngine
				formatter_engine = FormatterEngine()
				formatters = formatters_str.split('|')
				for formatter in formatters:
					value = formatter_engine.format(value, formatter)

			# Convert None to empty string
			return str(value) if value is not None else ""

		return re.sub(pattern, replace_variable, content)

	def parse_math(self, content: str) -> str:
		pattern = r'\{=([^}]+)\}'
		def replace_math(match):
			return self.evaluate_math(match.group(1).strip())
		return re.sub(pattern, replace_math, content)

	def evaluate_math(self, expr: str) -> str:
		try:
			context = self.doc.copy() if hasattr(self.doc, 'copy') else dict(self.doc)
			
			def _sum(arr, field=None):
				if not arr: return 0
				if field: return sum(frappe.utils.flt(row.get(field)) for row in arr if isinstance(row, dict))
				# Try direct dict access simulation, or fall back to object access
				return sum(frappe.utils.flt(getattr(row, field, 0)) if not isinstance(row, dict) else 0 for row in arr) if field else sum(frappe.utils.flt(x) for x in arr)
				
			def _avg(arr, field=None):
				if not arr: return 0
				return _sum(arr, field) / len(arr)
				
			context.update({
				'sum': _sum,
				'avg': _avg,
				'count': lambda arr: len(arr) if arr else 0,
			})

			res = frappe.safe_eval(expr, None, context)
			if isinstance(res, float):
				return str(round(res, 2))
			return str(res)
		except Exception as e:
			frappe.log_error(f"Math Error: {str(e)}", "PrintNebula Parser")
			return f"[Math Error: {expr}]"

	def parse_media(self, content: str) -> str:
		pattern_media = r'\{(qrcode|barcode):([^}]+)\}'
		def replace_media(match):
			media_type = match.group(1)
			params = match.group(2).split('|')
			data = params[0]
			
			if media_type == 'qrcode':
				return self.generate_qrcode(data)
			else:
				return self.generate_barcode(data)
		
		return re.sub(pattern_media, replace_media, content)

	def generate_qrcode(self, data: str) -> str:
		try:
			import qrcode
			import io
			import base64
			qr = qrcode.QRCode(version=1, box_size=4, border=1)
			qr.add_data(data)
			qr.make(fit=True)
			img = qr.make_image(fill_color="black", back_color="white")
			buffered = io.BytesIO()
			img.save(buffered, format="PNG")
			img_str = base64.b64encode(buffered.getvalue()).decode()
			return f'<img src="data:image/png;base64,{img_str}" class="printnebula-qrcode" />'
		except Exception as e:
			return f"[QR Code Error: {str(e)}]"

	def generate_barcode(self, data: str) -> str:
		try:
			import barcode
			from barcode.writer import ImageWriter
			import io
			import base64
			CODE128 = barcode.get_barcode_class('code128')
			bc = CODE128(data, writer=ImageWriter())
			buffered = io.BytesIO()
			bc.write(buffered, options={'module_width': 0.2, 'module_height': 10, 'font_size': 8})
			img_str = base64.b64encode(buffered.getvalue()).decode()
			return f'<img src="data:image/png;base64,{img_str}" class="printnebula-barcode" />'
		except Exception as e:
			return f"[Barcode Error: {str(e)}]"

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
