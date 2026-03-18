# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
import json
import os
import zipfile
from frappe.utils import get_files_path

@frappe.whitelist()
def generate_batch(template_name, doctype, docnames):
	"""Initialize and queue a background batch PDF generation job"""
	docnames_list = json.loads(docnames)
	job_id = frappe.generate_hash(length=10)
	
	frappe.cache().set_value(f"printnebula_batch_{job_id}", {
		"status": "Starting",
		"progress": 0,
		"status_message": "Initializing batch generation...",
		"file_url": ""
	}, expires_in_sec=86400)
	
	frappe.enqueue(
		"f_printnebula.f_printnebula.api.batch_api.process_batch",
		queue="long",
		template_name=template_name,
		doctype=doctype,
		docnames=docnames_list,
		job_id=job_id,
		user=frappe.session.user
	)
	
	return {"job_id": job_id}

@frappe.whitelist()
def get_job_status(job_id):
	"""Return the current progress status of a running batch job"""
	status = frappe.cache().get_value(f"printnebula_batch_{job_id}")
	if status:
		return status
	return {"status": "Unknown", "progress": 0, "status_message": "Job not found or expired"}

def process_batch(template_name, doctype, docnames, job_id, user):
	"""Background worker logic looping through documents and collecting outputs into a ZIP"""
	frappe.set_user(user)
	try:
		total = len(docnames)
		files = []
		
		from f_printnebula.utils.pdf_generator import PDFGenerator
		generator = PDFGenerator(template_name)
		
		for i, docname in enumerate(docnames):
			# Update progress hook
			progress = (i / total) * 90
			frappe.cache().set_value(f"printnebula_batch_{job_id}", {
				"status": "In Progress",
				"progress": progress,
				"status_message": f"Generating {i+1} of {total}: {docname}",
				"file_url": ""
			}, expires_in_sec=86400)
			
			try:
				result = generator.generate(docname=docname, output_format="pdf", save_file=True)
				file_url = result.get('file_url')
				if file_url:
					file_doc = frappe.get_doc("File", {"file_url": file_url})
					files.append((file_doc.file_name, file_doc.get_full_path()))
			except Exception as e:
				frappe.log_error(f"Batch Gen Error for {docname}: {str(e)}", f"Batch {job_id}")
		
		# Create ZIP archive
		frappe.cache().set_value(f"printnebula_batch_{job_id}", {
			"status": "In Progress",
			"progress": 95,
			"status_message": "Zipping output files...",
			"file_url": ""
		}, expires_in_sec=86400)
		
		zip_filename = f"PrintNebula_Batch_{job_id}.zip"
		zip_path = os.path.join(get_files_path(), zip_filename)
		
		with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
			for file_name, file_path in files:
				if os.path.exists(file_path):
					zipf.write(file_path, arcname=file_name)
					
		# Save zip securely to Frappe Files architecture
		file_doc = frappe.get_doc({
			"doctype": "File",
			"file_name": zip_filename,
			"is_private": 1,
			"file_url": f"/private/files/{zip_filename}",
			"attached_to_doctype": "PrintNebula Template",
			"attached_to_name": template_name
		})
		file_doc.insert(ignore_permissions=True)
		frappe.db.commit()
		
		# Flag Complete state containing the download payload
		frappe.cache().set_value(f"printnebula_batch_{job_id}", {
			"status": "Completed",
			"progress": 100,
			"status_message": "Completed successfully.",
			"file_url": file_doc.file_url
		}, expires_in_sec=86400)
		
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Batch generation failed: {str(e)}", f"Batch {job_id}")
		frappe.cache().set_value(f"printnebula_batch_{job_id}", {
			"status": "Failed",
			"progress": 100,
			"status_message": f"Failed: {str(e)}",
			"file_url": ""
		}, expires_in_sec=86400)
