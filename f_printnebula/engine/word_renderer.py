# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from docxtpl import DocxTemplate
from .resolver import FieldResolver
import os

class WordRenderer:
	"""Engine for rendering Microsoft Word (.docx) templates"""

	def __init__(self, template_name: str):
		self.template = frappe.get_doc("PrintNebula Template", template_name)
		self.resolver = FieldResolver(self.template.doctype_link)

	def render(self, docname: str, output_path: str):
		if not self.template.word_template:
			frappe.throw("Word template file not attached.")

		file_doc = frappe.get_doc("File", {"file_url": self.template.word_template})
		word_file_path = file_doc.get_full_path()

		if not os.path.exists(word_file_path):
			frappe.throw(f"Word template file does not exist at {word_file_path}")

		# Generate the template
		tpl = DocxTemplate(word_file_path)

		# Fetch actual record context
		doc_data = self.resolver.get_document_with_children(docname)
		
		# Replace variables inside the DOCX using jinja2 context internally supported by docxtpl
		tpl.render(doc_data)

		# Save directly to requested path
		tpl.save(output_path)
