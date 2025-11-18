# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from typing import Dict, Optional


@frappe.whitelist()
def generate_pdf(
	template: str,
	doctype: str,
	docname: str,
	output_format: str = "pdf",
	save_file: bool = True
) -> Dict:
	"""
	Generate PDF for a document using a template

	Args:
		template: Template name
		doctype: Doctype name
		docname: Document name
		output_format: Output format (pdf, html, docx)
		save_file: Whether to save file to disk

	Returns:
		Generation result dictionary
	"""
	from f_printnebula.utils.pdf_generator import PDFGenerator

	# Validate template
	template_doc = frappe.get_doc("PrintNebula Template", template)

	if template_doc.doctype_link != doctype:
		frappe.throw(f"Template {template} is not for doctype {doctype}")

	if not template_doc.is_active:
		frappe.throw(f"Template {template} is not active")

	# Generate PDF
	generator = PDFGenerator(template)
	result = generator.generate(docname, output_format, save_file)

	return result


@frappe.whitelist()
def preview_template(
	template: str,
	docname: Optional[str] = None,
	sample_data: Optional[Dict] = None
) -> Dict:
	"""
	Preview template with a document or sample data

	Args:
		template: Template name
		docname: Document name (optional)
		sample_data: Sample data dictionary (optional)

	Returns:
		Preview HTML
	"""
	from f_printnebula.engine.renderer import TemplateRenderer

	renderer = TemplateRenderer(template)

	if docname:
		html = renderer.render(docname)
	elif sample_data:
		html = renderer.get_preview_html(sample_data=sample_data)
	else:
		frappe.throw("Either docname or sample_data must be provided")

	return {
		'html': html
	}


@frappe.whitelist()
def validate_template(template: str) -> Dict:
	"""
	Validate template syntax and fields

	Args:
		template: Template name

	Returns:
		Validation result
	"""
	from f_printnebula.engine.validator import TemplateValidator

	template_doc = frappe.get_doc("PrintNebula Template", template)
	validator = TemplateValidator(template_doc)

	return validator.validate()


@frappe.whitelist()
def bulk_generate(
	template: str,
	doctype: str,
	filters: Optional[Dict] = None,
	output_format: str = "pdf",
	background: bool = True,
	email: bool = False
) -> Dict:
	"""
	Bulk generate PDFs for multiple documents

	Args:
		template: Template name
		doctype: Doctype name
		filters: Filters for selecting documents
		output_format: Output format
		background: Run in background
		email: Email generated PDFs

	Returns:
		Job information
	"""
	filters = filters or {}

	# Get documents
	documents = frappe.get_all(doctype, filters=filters, pluck='name')

	if not documents:
		frappe.throw("No documents found matching filters")

	if background:
		# Queue background job
		job = frappe.enqueue(
			'f_printnebula.api.template_api.process_bulk_generation',
			template=template,
			doctype=doctype,
			documents=documents,
			output_format=output_format,
			email=email,
			queue='long',
			timeout=3600
		)

		return {
			'job_id': job.id,
			'total_documents': len(documents),
			'status': 'queued'
		}
	else:
		# Process synchronously
		result = process_bulk_generation(template, doctype, documents, output_format, email)
		return result


def process_bulk_generation(
	template: str,
	doctype: str,
	documents: list,
	output_format: str = "pdf",
	email: bool = False
) -> Dict:
	"""
	Process bulk PDF generation

	Args:
		template: Template name
		doctype: Doctype name
		documents: List of document names
		output_format: Output format
		email: Email generated PDFs

	Returns:
		Generation results
	"""
	from f_printnebula.utils.pdf_generator import PDFGenerator

	generator = PDFGenerator(template)
	results = {
		'total': len(documents),
		'completed': 0,
		'failed': 0,
		'errors': []
	}

	for docname in documents:
		try:
			result = generator.generate(docname, output_format, save_file=True)

			if email and result.get('success'):
				# TODO: Implement email sending
				pass

			results['completed'] += 1

		except Exception as e:
			results['failed'] += 1
			results['errors'].append({
				'document': docname,
				'error': str(e)
			})

	return results


@frappe.whitelist()
def get_template_fields(doctype: str) -> Dict:
	"""
	Get available fields for a doctype

	Args:
		doctype: Doctype name

	Returns:
		Fields list
	"""
	from f_printnebula.engine.resolver import FieldResolver

	resolver = FieldResolver(doctype)
	fields = resolver.get_field_list()

	return {
		'fields': fields,
		'child_tables': [f.fieldname for f in resolver.get_child_table_fields()]
	}


@frappe.whitelist()
def get_child_table_fields(doctype: str, child_table: str) -> Dict:
	"""
	Get fields for a child table

	Args:
		doctype: Parent doctype name
		child_table: Child table field name

	Returns:
		Child table fields
	"""
	from f_printnebula.engine.resolver import FieldResolver

	# Get child table doctype
	parent_meta = frappe.get_meta(doctype)
	child_field = parent_meta.get_field(child_table)

	if not child_field or child_field.fieldtype != 'Table':
		frappe.throw(f"'{child_table}' is not a table field in {doctype}")

	# Get child table fields
	child_doctype = child_field.options
	resolver = FieldResolver(child_doctype)
	fields = resolver.get_field_list()

	return {
		'child_doctype': child_doctype,
		'fields': fields
	}
