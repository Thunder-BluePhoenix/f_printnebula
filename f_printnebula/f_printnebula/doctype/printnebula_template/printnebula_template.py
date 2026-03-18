# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class PrintNebulaTemplate(Document):
	"""Controller class for PrintNebula Template doctype"""

	def before_save(self):
		"""Validate and process template before saving"""
		self.validate_field_mappings()
		self.validate_child_table_config()
		self.validate_conditions()
		self.set_created_by()

	def validate_field_mappings(self):
		"""Validate field mappings JSON"""
		if self.field_mappings:
			try:
				mappings = json.loads(self.field_mappings)
				if not isinstance(mappings, dict):
					frappe.throw("Field Mappings must be a JSON object")
			except json.JSONDecodeError as e:
				frappe.throw(f"Invalid JSON in Field Mappings: {str(e)}")

	def validate_child_table_config(self):
		"""Validate child table configuration JSON"""
		if self.child_table_config:
			try:
				config = json.loads(self.child_table_config)
				if not isinstance(config, dict):
					frappe.throw("Child Table Config must be a JSON object")
			except json.JSONDecodeError as e:
				frappe.throw(f"Invalid JSON in Child Table Config: {str(e)}")

	def validate_conditions(self):
		"""Validate conditions JSON"""
		if self.conditions:
			try:
				conditions = json.loads(self.conditions)
				if not isinstance(conditions, list):
					frappe.throw("Conditions must be a JSON array")
			except json.JSONDecodeError as e:
				frappe.throw(f"Invalid JSON in Conditions: {str(e)}")

	def set_created_by(self):
		"""Set created_by field on first save"""
		if not self.created_by:
			self.created_by = frappe.session.user

	def on_update(self):
		"""Handle template updates"""
		self.update_default_template()
		self.sync_frappe_print_format()

	def on_trash(self):
		self.delete_frappe_print_format()

	def get_preview_html(self, docname):
		"""Returns generated HTML for frappe Print Format integration"""
		from f_printnebula.engine.renderer import TemplateRenderer
		renderer = TemplateRenderer(self.name)
		return renderer.render(docname)

	def sync_frappe_print_format(self):
		"""Automatically create/update standard Frappe Print Format for native integration"""
		print_format_name = f"PrintNebula - {self.template_name}"
		
		# Prevent recursive saving or missing fields
		if not self.template_name or not self.doctype_link:
			return
			
		if not frappe.db.exists("Print Format", print_format_name):
			doc = frappe.new_doc("Print Format")
			doc.name = print_format_name
			doc.doc_type = self.doctype_link
			doc.custom_format = 1
			doc.print_format_type = "Jinja"
			doc.module = "F Printnebula" # Link to our module
		else:
			doc = frappe.get_doc("Print Format", print_format_name)
			
		doc.doc_type = self.doctype_link
		
		if self.get("template_type") == "Word Document":
			doc.html = f"""<div style="text-align: center; padding: 50px;">
				<h3>Generate Word Document</h3>
				<p>This is a Word Document Template.</p>
				<p>Please use the PrintNebula APIs directly to output DOCX payloads.</p>
			</div>"""
		else:
			doc.html = f"{{{{ frappe.get_doc('PrintNebula Template', '{self.name}').get_preview_html(doc.name) }}}}"
			
		doc.save(ignore_permissions=True)

	def delete_frappe_print_format(self):
		print_format_name = f"PrintNebula - {self.template_name}"
		if frappe.db.exists("Print Format", print_format_name):
			frappe.delete_doc("Print Format", print_format_name, ignore_permissions=True)

	def update_default_template(self):
		"""If this is set as default, unset other default templates for the same doctype"""
		if self.is_default:
			frappe.db.sql("""
				UPDATE `tabPrintNebula Template`
				SET is_default = 0
				WHERE doctype_link = %s AND name != %s
			""", (self.doctype_link, self.name))

	def increment_usage_count(self):
		"""Increment usage counter"""
		self.usage_count = (self.usage_count or 0) + 1
		self.last_used = frappe.utils.now()
		self.save(ignore_permissions=True)


@frappe.whitelist()
def get_template_for_doctype(doctype, template_name=None):
	"""
	Get template for a specific doctype

	Args:
		doctype (str): The doctype name
		template_name (str, optional): Specific template name. If not provided, returns default template.

	Returns:
		dict: Template document as dict
	"""
	filters = {
		"doctype_link": doctype,
		"is_active": 1
	}

	if template_name:
		filters["name"] = template_name
	else:
		filters["is_default"] = 1

	template = frappe.get_all(
		"PrintNebula Template",
		filters=filters,
		fields=["*"],
		limit=1
	)

	if template:
		return template[0]

	frappe.throw(f"No active template found for {doctype}")


@frappe.whitelist()
def get_templates_for_doctype(doctype):
	"""
	Get all templates for a specific doctype

	Args:
		doctype (str): The doctype name

	Returns:
		list: List of template documents
	"""
	templates = frappe.get_all(
		"PrintNebula Template",
		filters={
			"doctype_link": doctype,
			"is_active": 1
		},
		fields=["name", "template_name", "is_default", "description"],
		order_by="is_default DESC, template_name ASC"
	)

	return templates


@frappe.whitelist()
def clone_template(template_name, new_name):
	"""
	Clone an existing template

	Args:
		template_name (str): Source template name
		new_name (str): New template name

	Returns:
		dict: New template document
	"""
	source = frappe.get_doc("PrintNebula Template", template_name)

	# Create new template
	new_template = frappe.copy_doc(source)
	new_template.template_name = new_name
	new_template.is_default = 0
	new_template.parent_template = template_name
	new_template.usage_count = 0
	new_template.last_used = None
	new_template.change_log = f"Cloned from {template_name}"

	new_template.insert()

	return new_template.as_dict()


@frappe.whitelist()
def validate_template_syntax(template_name):
	"""
	Validate template syntax and fields

	Args:
		template_name (str): Template name to validate

	Returns:
		dict: Validation result with errors and warnings
	"""
	from f_printnebula.engine.validator import TemplateValidator

	template = frappe.get_doc("PrintNebula Template", template_name)
	validator = TemplateValidator(template)

	return validator.validate()
