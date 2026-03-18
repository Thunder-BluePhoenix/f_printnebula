import frappe
import json

def execute_scheduled_generations(frequency):
	"""
	Iterate over all active templates matching the frequency and dispatch batch generation jobs
	"""
	templates = frappe.get_all(
		"PrintNebula Template",
		filters={"is_active": 1, "enable_scheduled_generation": 1, "schedule_frequency": frequency},
		fields=["name", "doctype_link", "schedule_filters"]
	)
	
	for tmpl in templates:
		filters = {}
		if tmpl.schedule_filters:
			try:
				filters = json.loads(tmpl.schedule_filters)
			except Exception as e:
				frappe.log_error(f"Invalid JSON filters for template {tmpl.name} schedule", "PrintNebula Scheduler")
				continue
		
		try:
			# Pull matching records based on the JSON filters
			docs = frappe.get_all(tmpl.doctype_link, filters=filters, pluck="name")
			if not docs:
				continue
				
			# Hand off the target array to our Batch UI engine asynchronously!
			frappe.enqueue(
				"f_printnebula.f_printnebula.api.batch_api.process_batch",
				queue="long",
				job_id=f"scheduled_{tmpl.name}_{frappe.utils.now().replace(':', '-')}".replace(' ', '_'),
				template=tmpl.name,
				doctype=tmpl.doctype_link,
				docnames=json.dumps(docs)
			)
			frappe.logger("printnebula").info(f"Queued scheduled {frequency} generation for {tmpl.name} ({len(docs)} documents)")
		except Exception as e:
			frappe.log_error(f"Scheduled generation failed for {tmpl.name}: {str(e)}", "PrintNebula Scheduler")

def run_daily():
	execute_scheduled_generations("Daily")

def run_weekly():
	execute_scheduled_generations("Weekly")

def run_monthly():
	execute_scheduled_generations("Monthly")
