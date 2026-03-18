import frappe
import unittest

class TestSetupPhase4(unittest.TestCase):
	def test_create_doctypes(self):
		from f_printnebula.api.automation import setup
		setup()
		self.assertTrue(frappe.db.exists("DocType", "PrintNebula Snippet"))
		self.assertTrue(frappe.db.exists("DocType", "PrintNebula Log"))
		print("Successfully installed Phase 4 doctypes!")
