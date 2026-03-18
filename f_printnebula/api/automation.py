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
