# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.core.doctype.communication.email import make

def send_auto_emails(doc, method):
	"""
	Hook attached to all documents on_submit
	Finds active templates for the doctype with auto-email enabled and queues them
	"""
	templates = frappe.get_all(
		"PrintNebula Template",
		filters={
			"doctype_link": doc.doctype,
			"is_active": 1,
			"enable_auto_email": 1
		},
		fields=["name", "email_to_field", "email_subject", "email_template", "template_type"]
	)

	for template in templates:
		frappe.enqueue(
			"f_printnebula.api.automation.process_auto_email",
			queue="long",
			docname=doc.name,
			doctype=doc.doctype,
			template_name=template.name
		)

def process_auto_email(docname, doctype, template_name):
	"""Background job worker to generate the PDF and send the email"""
	doc = frappe.get_doc(doctype, docname)
	template = frappe.get_doc("PrintNebula Template", template_name)

	# Determine recipient
	if not template.email_to_field:
		frappe.log_error("Auto-email failed: No 'Email To Field' configured", f"PrintNebula {template_name}")
		return
		
	recipient = doc.get(template.email_to_field)
	if not recipient:
		frappe.log_error(f"Auto-email failed: Document missing '{template.email_to_field}' value", f"PrintNebula {template_name}")
		return

	# Generate PDF/DOCX using our generator
	from f_printnebula.utils.pdf_generator import PDFGenerator
	generator = PDFGenerator(template_name)
	
	try:
		# output format handles routing internally based on template_type
		# Word templates generate docx, HTML templates generate PDF
		result = generator.generate(docname=docname, output_format="pdf", save_file=True)
		file_url = result.get('file_url')
		
		if not file_url:
			raise Exception("File URL missing after generation.")
	except Exception as e:
		frappe.log_error(f"Auto-email generation failed: {str(e)}", f"PrintNebula {template_name}")
		return

	# Parse email subject and body using PrintNebula variables engine!
	# We can use our VariableParser to parse the subject and body dynamically
	from f_printnebula.engine.parser import VariableParser
	import json
	
	mappings = {}
	if template.field_mappings:
		mappings = json.loads(template.field_mappings)
		
	parser = VariableParser(doc.as_dict(), mappings)
	
	subject = parser.parse(template.email_subject or f"Document {doc.name}")
	body = parser.parse(template.email_template or f"Please find the attached document: {doc.name}")

	# Send email using Frappe
	try:
		# Since the file is attached to the document, we can attach it to the email
		file_doc = frappe.get_doc("File", {"file_url": file_url})
		
		make(
			recipients=recipient,
			subject=subject,
			content=body,
			doctype=doctype,
			name=docname,
			send_email=True,
			attachments=[file_doc.name]
		)
		
		frappe.logger("printnebula").info(f"Successfully auto-emailed {docname} to {recipient}")
	except Exception as e:
		frappe.log_error(f"Auto-email sending failed: {str(e)}", f"PrintNebula {template_name}")


def setup():
	# 1. PrintNebula Snippet Doctype
	if not frappe.db.exists("DocType", "PrintNebula Snippet"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "PrintNebula Snippet",
			"module": "F Printnebula",
			"custom": 0,
			"naming_rule": "By fieldname",
			"autoname": "field:snippet_name",
			"fields": [
				{"fieldname": "snippet_name", "fieldtype": "Data", "label": "Snippet Name", "reqd": 1, "unique": 1},
				{"fieldname": "html_content", "fieldtype": "Text Editor", "label": "HTML Content"}
			],
			"permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}]
		})
		doc.flags.ignore_links = True
		doc.insert(ignore_permissions=True)

	# 2. PrintNebula Log Doctype
	if not frappe.db.exists("DocType", "PrintNebula Log"):
		doc = frappe.get_doc({
			"doctype": "DocType",
			"name": "PrintNebula Log",
			"module": "F Printnebula",
			"custom": 0,
			"fields": [
				{"fieldname": "template", "fieldtype": "Data", "label": "Template"},
				{"fieldname": "doctype_link", "fieldtype": "Link", "options": "DocType", "label": "Target DocType"},
				{"fieldname": "docname", "fieldtype": "Dynamic Link", "options": "doctype_link", "label": "Document Name"},
				{"fieldname": "status", "fieldtype": "Select", "options": "Success\nFailed", "label": "Status"},
				{"fieldname": "duration", "fieldtype": "Float", "label": "Duration (s)"},
				{"fieldname": "error_log", "fieldtype": "Text", "label": "Error Log"}
			],
			"permissions": [{"role": "All", "read": 1, "write": 1, "create": 1}]
		})
		doc.flags.ignore_links = True
		doc.insert(ignore_permissions=True)
	
	frappe.db.commit()

@frappe.whitelist()
def log_generation(template, doctype_link, docname, status, duration, error_log=""):
	try:
		log = frappe.get_doc({
			"doctype": "PrintNebula Log",
			"template": template,
			"doctype_link": doctype_link,
			"docname": docname,
			"status": status,
			"duration": duration,
			"error_log": error_log
		})
		log.insert(ignore_permissions=True)
		frappe.db.commit()
	except Exception as e:
		pass
