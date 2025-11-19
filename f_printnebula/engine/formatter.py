# Copyright (c) 2025, BluePhoenix and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import (
	flt, cint, fmt_money, formatdate, get_datetime,
	now_datetime, add_days, date_diff
)
from typing import Any


class FormatterEngine:
	"""Engine for formatting field values"""

	def __init__(self, locale: str = None):
		"""
		Initialize formatter with optional locale

		Args:
			locale: Locale for formatting (e.g., 'en-US', 'hi')
		"""
		self.locale = locale or frappe.local.lang or 'en'

	def format(self, value: Any, formatter: str) -> str:
		"""
		Format value using specified formatter

		Args:
			value: Value to format
			formatter: Formatter specification (e.g., 'date', 'currency', 'date:dd-MM-yyyy')

		Returns:
			Formatted value as string
		"""
		if value is None or value == "":
			return ""

		# Parse formatter and arguments
		parts = formatter.split(':')
		formatter_type = parts[0].lower()
		formatter_args = parts[1] if len(parts) > 1 else None

		# Call appropriate formatter
		formatter_method = getattr(self, f'format_{formatter_type}', None)
		if formatter_method:
			return formatter_method(value, formatter_args)

		# Unknown formatter, return value as-is
		return str(value)

	def format_date(self, value: Any, format_string: str = None) -> str:
		"""
		Format date value

		Args:
			value: Date value
			format_string: Date format (e.g., 'dd-MM-yyyy')

		Returns:
			Formatted date string
		"""
		try:
			if isinstance(value, str):
				value = get_datetime(value)

			if format_string:
				return formatdate(value, format_string)
			else:
				return formatdate(value)
		except Exception:
			return str(value)

	def format_datetime(self, value: Any, format_string: str = None) -> str:
		"""
		Format datetime value

		Args:
			value: Datetime value
			format_string: Datetime format

		Returns:
			Formatted datetime string
		"""
		try:
			if isinstance(value, str):
				value = get_datetime(value)

			if format_string:
				return value.strftime(format_string)
			else:
				return str(value)
		except Exception:
			return str(value)

	def format_currency(self, value: Any, currency: str = None) -> str:
		"""
		Format currency value

		Args:
			value: Numeric value
			currency: Currency code (optional)

		Returns:
			Formatted currency string
		"""
		try:
			value = flt(value)
			if currency:
				return fmt_money(value, currency=currency)
			else:
				return fmt_money(value)
		except Exception:
			return str(value)

	def format_number(self, value: Any, precision: str = None) -> str:
		"""
		Format number value

		Args:
			value: Numeric value
			precision: Decimal precision

		Returns:
			Formatted number string
		"""
		try:
			precision = int(precision) if precision else 2
			value = flt(value, precision)
			return frappe.format_value(value, {'fieldtype': 'Float', 'precision': precision})
		except Exception:
			return str(value)

	def format_int(self, value: Any, args: str = None) -> str:
		"""
		Format integer value

		Args:
			value: Numeric value
			args: Not used

		Returns:
			Formatted integer string
		"""
		try:
			return str(cint(value))
		except Exception:
			return str(value)

	def format_percent(self, value: Any, precision: str = None) -> str:
		"""
		Format percentage value

		Args:
			value: Numeric value
			precision: Decimal precision

		Returns:
			Formatted percentage string
		"""
		try:
			precision = int(precision) if precision else 2
			value = flt(value, precision)
			return f"{value}%"
		except Exception:
			return str(value)

	def format_upper(self, value: Any, args: str = None) -> str:
		"""Convert to uppercase"""
		return str(value).upper()

	def format_lower(self, value: Any, args: str = None) -> str:
		"""Convert to lowercase"""
		return str(value).lower()

	def format_title(self, value: Any, args: str = None) -> str:
		"""Convert to title case"""
		return str(value).title()

	def format_round(self, value: Any, precision: str = None) -> str:
		"""
		Round number value

		Args:
			value: Numeric value
			precision: Decimal places (default 0)

		Returns:
			Rounded value as string
		"""
		try:
			precision = int(precision) if precision else 0
			value = flt(value, precision)
			return str(value)
		except Exception:
			return str(value)

	def format_default(self, value: Any, default_value: str) -> str:
		"""
		Return default value if empty

		Args:
			value: Original value
			default_value: Default value to use if empty

		Returns:
			Value or default
		"""
		if value is None or value == "":
			return default_value
		return str(value)
