# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.pdf import get_pdf
from frappe.utils import get_files_path, now
import os
import time
from typing import Dict, Optional


class PDFGenerator:
	"""Generator for creating PDFs from HTML"""

	def __init__(self, template_name: str):
		"""
		Initialize PDF generator

		Args:
			template_name: PrintNebula Template name
		"""
		self.template_name = template_name
		self.template = frappe.get_doc("PrintNebula Template", template_name)

	def generate(
		self,
		docname: str,
		output_format: str = "pdf",
		save_file: bool = True
	) -> Dict:
		"""
		Generate PDF for a document

		Args:
			docname: Document name
			output_format: Output format (pdf, html, docx)
			save_file: Whether to save file to disk

		Returns:
			Dictionary with file info
		"""
		start_time = time.time()
		status = "Success"
		error_msg = ""
		file_data = {}
		
		try:
			if self.template.template_type == "Word Document":
				from f_printnebula.engine.word_renderer import WordRenderer
				renderer = WordRenderer(self.template_name)
				file_name = f"{self.template.doctype_link}_{docname}_{now()}.docx".replace(" ", "_").replace(":", "-")
				file_path = os.path.join(get_files_path(), file_name)
				
				renderer.render(docname, file_path)
				
				if save_file:
					file_doc = frappe.get_doc({
						"doctype": "File",
						"file_name": file_name,
						"is_private": 1,
						"file_url": f"/private/files/{file_name}",
						"attached_to_doctype": self.template.doctype_link,
						"attached_to_name": docname
					})
					file_doc.insert(ignore_permissions=True)
					file_url = file_doc.file_url
				else:
					file_url = None
					
				file_data = {
					'file_url': file_url,
					'file_size': os.path.getsize(file_path),
					'file_name': file_name
				}
				output_format = "docx"
			else:
				# Render HTML
				from f_printnebula.engine.renderer import TemplateRenderer
				renderer = TemplateRenderer(self.template_name)
				html_content = renderer.render(docname)

				# Generate based on format
				if output_format.lower() == "pdf":
					file_data = self.generate_pdf(html_content, docname, save_file)
				elif output_format.lower() == "html":
					file_data = self.generate_html(html_content, docname, save_file)
				else:
					frappe.throw(f"Unsupported output format: {output_format}")
			return {
				'success': True,
				'file_url': file_data.get('file_url'),
				'file_size': file_data.get('file_size'),
				'format': output_format
			}
		except Exception as e:
			status = "Failed"
			error_msg = str(e)
			frappe.throw(f"PDF generation failed: {str(e)}")
		finally:
			# Log generation metrics
			duration = time.time() - start_time
			file_url = file_data.get('file_url', "")
			try:
				import frappe.utils.background_jobs
				frappe.enqueue(
					"f_printnebula.api.automation.log_generation",
					queue="short",
					template=self.template_name,
					doctype_link=self.template.doctype_link,
					docname=docname,
					status=status,
					duration=duration,
					error_log=error_msg
				)
			except Exception:
				pass

	def generate_pdf(self, html_content: str, docname: str, save_file: bool) -> Dict:
		"""
		Generate PDF from HTML

		Args:
			html_content: HTML content
			docname: Document name
			save_file: Whether to save to disk

		Returns:
			File info dictionary
		"""
		# Get PDF options from template
		options = self.get_pdf_options()

		# Generate PDF
		pdf_data = get_pdf(html_content, options=options)

		if save_file:
			# Save to file
			file_name = f"{self.template.doctype_link}_{docname}_{now()}.pdf".replace(" ", "_").replace(":", "-")
			file_path = os.path.join(get_files_path(), file_name)

			with open(file_path, "wb") as f:
				f.write(pdf_data)

			# Create file document
			file_doc = frappe.get_doc({
				"doctype": "File",
				"file_name": file_name,
				"is_private": 1,
				"file_url": f"/private/files/{file_name}",
				"attached_to_doctype": self.template.doctype_link,
				"attached_to_name": docname
			})
			file_doc.insert(ignore_permissions=True)

			return {
				'file_url': file_doc.file_url,
				'file_size': len(pdf_data),
				'file_name': file_name
			}
		else:
			return {
				'file_data': pdf_data,
				'file_size': len(pdf_data)
			}

	def generate_html(self, html_content: str, docname: str, save_file: bool) -> Dict:
		"""
		Save HTML to file

		Args:
			html_content: HTML content
			docname: Document name
			save_file: Whether to save to disk

		Returns:
			File info dictionary
		"""
		if save_file:
			file_name = f"{self.template.doctype_link}_{docname}_{now()}.html".replace(" ", "_").replace(":", "-")
			file_path = os.path.join(get_files_path(), file_name)

			with open(file_path, "w", encoding="utf-8") as f:
				f.write(html_content)

			# Create file document
			file_doc = frappe.get_doc({
				"doctype": "File",
				"file_name": file_name,
				"is_private": 1,
				"file_url": f"/private/files/{file_name}",
				"attached_to_doctype": self.template.doctype_link,
				"attached_to_name": docname
			})
			file_doc.insert(ignore_permissions=True)

			return {
				'file_url': file_doc.file_url,
				'file_size': len(html_content.encode('utf-8')),
				'file_name': file_name
			}
		else:
			return {
				'file_data': html_content,
				'file_size': len(html_content.encode('utf-8'))
			}

	def get_pdf_options(self) -> Dict:
		"""
		Get PDF generation options from template

		Returns:
			PDF options dictionary
		"""
		options = {
			'page-size': self.template.page_size or 'A4',
			'orientation': self.template.page_orientation or 'Portrait',
			'margin-top': f"{self.template.margin_top or 15}mm",
			'margin-bottom': f"{self.template.margin_bottom or 15}mm",
			'margin-left': f"{self.template.margin_left or 15}mm",
			'margin-right': f"{self.template.margin_right or 15}mm"
		}

		return options

