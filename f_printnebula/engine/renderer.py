# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
import json
from jinja2 import Template, Environment, BaseLoader
from typing import Dict, Any, Optional
from functools import lru_cache
from .parser import VariableParser
from .formatter import FormatterEngine
from .resolver import FieldResolver


@lru_cache(maxsize=100)
def get_jinja_template(content: str):
	env = Environment(loader=BaseLoader())
	return env.from_string(content)


class TemplateRenderer:
	"""Main template rendering engine"""

	def __init__(self, template_name: str):
		"""
		Initialize renderer with template

		Args:
			template_name: PrintNebula Template name
		"""
		self.template = frappe.get_doc("PrintNebula Template", template_name)
		self.resolver = FieldResolver(self.template.doctype_link)

	def render(self, docname: str) -> str:
		"""
		Render template for a document

		Args:
			docname: Document name

		Returns:
			Rendered HTML string
		"""
		# Fetch document data
		doc = self.resolver.get_document_with_children(docname)

		# Parse field mappings
		field_mappings = self.parse_field_mappings()

		# Render header, body, footer
		header_html = self.render_section(
			self.template.header or "",
			doc,
			field_mappings
		)

		body_html = self.render_section(
			self.template.body or "",
			doc,
			field_mappings
		)

		footer_html = self.render_section(
			self.template.footer or "",
			doc,
			field_mappings
		)

		# Combine sections
		final_html = self.combine_sections(header_html, body_html, footer_html)

		# Apply custom CSS
		if self.template.custom_css:
			final_html = self.apply_custom_css(final_html)

		return final_html

	def render_section(
		self,
		section_content: str,
		doc: Dict[str, Any],
		field_mappings: Dict
	) -> str:
		"""
		Render a template section (header, body, or footer)

		Args:
			section_content: Section HTML content
			doc: Document data
			field_mappings: Field mappings dictionary

		Returns:
			Rendered section HTML
		"""
		if not section_content:
			return ""

		# Step 1: Process Jinja2 loops (child tables)
		section_content = self.process_jinja_loops(section_content, doc)

		# Step 2: Parse curly-brace variables
		parser = VariableParser(doc, field_mappings)
		section_content = parser.parse(section_content)

		return section_content

	def process_jinja_loops(self, content: str, doc: Dict[str, Any]) -> str:
		"""
		Process Jinja2 loop syntax for child tables

		Args:
			content: Template content with Jinja2 syntax
			doc: Document data with child tables

		Returns:
			Content with loops processed
		"""
		try:
			# Get template from cache
			template = get_jinja_template(content)

			# Render with document data
			rendered = template.render(**doc)

			return rendered
		except Exception as e:
			frappe.log_error(f"Jinja2 rendering error: {str(e)}", "PrintNebula Jinja Error")
			return content

	def parse_field_mappings(self) -> Dict:
		"""
		Parse field mappings from template

		Returns:
			Field mappings dictionary
		"""
		if not self.template.field_mappings:
			return {}

		try:
			return json.loads(self.template.field_mappings)
		except json.JSONDecodeError:
			frappe.log_error("Invalid field mappings JSON", "PrintNebula Field Mappings")
			return {}

	def combine_sections(self, header: str, body: str, footer: str) -> str:
		"""
		Combine header, body, and footer into final HTML

		Args:
			header: Header HTML
			body: Body HTML
			footer: Footer HTML

		Returns:
			Combined HTML document
		"""
		html_template = f"""
<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>{self.template.template_name}</title>
	<style>
		@page {{
			size: {self.template.page_size} {self.template.page_orientation.lower()};
			margin-top: {self.template.margin_top}mm;
			margin-bottom: {self.template.margin_bottom}mm;
			margin-left: {self.template.margin_left}mm;
			margin-right: {self.template.margin_right}mm;
		}}

		body {{
			font-family: Arial, sans-serif;
			font-size: 12pt;
			line-height: 1.6;
		}}

		.header {{
			margin-bottom: 20px;
		}}

		.footer {{
			margin-top: 20px;
		}}

		table {{
			width: 100%;
			border-collapse: collapse;
		}}

		table, th, td {{
			border: 1px solid #ddd;
		}}

		th, td {{
			padding: 8px;
			text-align: left;
		}}

		th {{
			background-color: #f2f2f2;
		}}
	</style>
</head>
<body>
	{f'<div class="header">{header}</div>' if self.template.enable_header_footer and header else ''}

	<div class="body">
		{body}
	</div>

	{f'<div class="footer">{footer}</div>' if self.template.enable_header_footer and footer else ''}
</body>
</html>
"""
		return html_template

	def apply_custom_css(self, html: str) -> str:
		"""
		Apply custom CSS to HTML

		Args:
			html: HTML content

		Returns:
			HTML with custom CSS injected
		"""
		# Find </style> tag and insert custom CSS before it
		custom_css = self.template.custom_css

		if "</style>" in html:
			html = html.replace("</style>", f"\n{custom_css}\n</style>")

		return html

	def get_preview_html(self, docname: str = None, sample_data: Dict = None) -> str:
		"""
		Generate preview HTML

		Args:
			docname: Document name for preview (optional)
			sample_data: Sample data for preview (optional)

		Returns:
			Preview HTML
		"""
		if docname:
			return self.render(docname)
		elif sample_data:
			# Render with sample data
			field_mappings = self.parse_field_mappings()

			header_html = self.render_section(
				self.template.header or "",
				sample_data,
				field_mappings
			)

			body_html = self.render_section(
				self.template.body or "",
				sample_data,
				field_mappings
			)

			footer_html = self.render_section(
				self.template.footer or "",
				sample_data,
				field_mappings
			)

			return self.combine_sections(header_html, body_html, footer_html)
		else:
			frappe.throw("Either docname or sample_data must be provided for preview")
