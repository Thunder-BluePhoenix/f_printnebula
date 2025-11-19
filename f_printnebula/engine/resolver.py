# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from typing import Dict, Any, List


class FieldResolver:
	"""Resolver for fetching field values and metadata from documents"""

	def __init__(self, doctype: str):
		"""
		Initialize resolver for a doctype

		Args:
			doctype: Doctype name
		"""
		self.doctype = doctype
		self.meta = frappe.get_meta(doctype)

	def get_document(self, docname: str) -> Dict[str, Any]:
		"""
		Get complete document data

		Args:
			docname: Document name

		Returns:
			Document as dictionary
		"""
		doc = frappe.get_doc(self.doctype, docname)
		return doc.as_dict()

	def get_document_with_children(self, docname: str) -> Dict[str, Any]:
		"""
		Get document with all child table data

		Args:
			docname: Document name

		Returns:
			Document with child tables as dictionary
		"""
		doc = frappe.get_doc(self.doctype, docname)
		doc_dict = doc.as_dict()

		# Get all child table fields
		child_fields = self.get_child_table_fields()

		for field in child_fields:
			fieldname = field.fieldname
			if hasattr(doc, fieldname):
				child_data = getattr(doc, fieldname)
				doc_dict[fieldname] = [row.as_dict() for row in child_data]

		return doc_dict

	def get_field_list(self) -> List[Dict[str, str]]:
		"""
		Get list of all fields in doctype

		Returns:
			List of field dictionaries with name, label, type
		"""
		fields = []

		for field in self.meta.fields:
			if field.fieldtype not in ['Section Break', 'Column Break', 'Tab Break', 'HTML']:
				fields.append({
					'fieldname': field.fieldname,
					'label': field.label,
					'fieldtype': field.fieldtype,
					'options': field.options
				})

		return fields

	def get_child_table_fields(self) -> List[Any]:
		"""
		Get all child table fields

		Returns:
			List of child table field objects
		"""
		child_fields = []

		for field in self.meta.fields:
			if field.fieldtype == 'Table':
				child_fields.append(field)

		return child_fields

	def get_field_meta(self, fieldname: str) -> Dict[str, Any]:
		"""
		Get metadata for a specific field

		Args:
			fieldname: Field name

		Returns:
			Field metadata dictionary
		"""
		field = self.meta.get_field(fieldname)

		if field:
			return {
				'fieldname': field.fieldname,
				'label': field.label,
				'fieldtype': field.fieldtype,
				'options': field.options,
				'reqd': field.reqd,
				'read_only': field.read_only,
				'default': field.default
			}

		return None

	def validate_field_exists(self, fieldname: str) -> bool:
		"""
		Check if field exists in doctype

		Args:
			fieldname: Field name

		Returns:
			True if field exists, False otherwise
		"""
		return self.meta.get_field(fieldname) is not None

	def get_link_field_value(self, doc: Dict, fieldname: str, target_field: str) -> Any:
		"""
		Get value from linked document

		Args:
			doc: Source document
			fieldname: Link field name in source
			target_field: Field to fetch from linked document

		Returns:
			Value from linked document
		"""
		field_meta = self.meta.get_field(fieldname)

		if not field_meta or field_meta.fieldtype != 'Link':
			return None

		link_value = doc.get(fieldname)
		if not link_value:
			return None

		try:
			linked_doc = frappe.get_doc(field_meta.options, link_value)
			return linked_doc.get(target_field)
		except Exception:
			return None
