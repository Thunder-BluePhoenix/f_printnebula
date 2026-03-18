import frappe
import sys

def setup():
	frappe.init(site="genbi")
	frappe.connect()

	try:
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
				"permissions": [
					{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}
				]
			})
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
				"permissions": [
					{"role": "All", "read": 1, "write": 1, "create": 1}
				]
			})
			doc.insert(ignore_permissions=True)
		
		frappe.db.commit()
		print("Successfully created PrintNebula Snippet and PrintNebula Log Doctypes.")
	except Exception as e:
		print(f"Error: {str(e)}")
		sys.exit(1)

setup()
