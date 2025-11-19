# 🧪 PrintNebula Testing Guide

## Overview

This guide explains how to test PrintNebula features in a Frappe environment.

---

## Prerequisites

```bash
# Install the app
cd /path/to/bench
bench get-app /path/to/f_printnebula
bench --site YOUR_SITE install-app f_printnebula
bench migrate
```

---

## Quick Test Checklist

### ✅ 1. Basic Variable Parsing Test

**Create a test template:**

```python
# In Frappe console: bench console
import frappe
from f_printnebula.engine.parser import VariableParser

# Test data
doc = {
    "name": "TEST-001",
    "customer_name": "John Doe",
    "grand_total": 1234.56
}

# Create parser
parser = VariableParser(doc)

# Test simple variables
template = "Invoice: {name}, Customer: {customer_name}, Total: {grand_total}"
result = parser.parse(template)
print(result)
# Expected: "Invoice: TEST-001, Customer: John Doe, Total: 1234.56"
```

**✅ Pass if:** All variables are replaced correctly

---

### ✅ 2. Conditional Rendering Test

```python
# Test conditional
doc = {
    "status": "Submitted",
    "is_paid": 1,
    "discount_amount": 100
}

parser = VariableParser(doc)

# Test true condition
template1 = "{?is_paid}PAID{/is_paid}"
print(parser.parse(template1))  # Should print: "PAID"

# Test false condition
template2 = "{?is_draft}DRAFT{/is_draft}"
print(parser.parse(template2))  # Should print: ""

# Test comparison
template3 = "{?status=Submitted}Approved{/status}"
print(parser.parse(template3))  # Should print: "Approved"

# Test numeric comparison
template4 = "{?discount_amount>50}Big Discount{/discount_amount}"
print(parser.parse(template4))  # Should print: "Big Discount"
```

**✅ Pass if:** All conditionals evaluate correctly

---

### ✅ 3. Formatter Engine Test

```python
from f_printnebula.engine.formatter import FormatterEngine

formatter = FormatterEngine()

# Test formatters
print(formatter.format(1234.56, "currency"))      # Should format as currency
print(formatter.format("hello", "upper"))         # Should print: "HELLO"
print(formatter.format(15.5, "percent:1"))        # Should print: "15.5%"
print(formatter.format(None, "default:N/A"))      # Should print: "N/A"
```

**✅ Pass if:** All formatters work correctly

---

### ✅ 4. Field Mapping Test

```python
# Test field aliases
doc = {
    "name": "SI-00001",
    "customer_name": "Jane Doe"
}

mappings = {
    "invoice_no": "name",
    "customer": "customer_name"
}

parser = VariableParser(doc, mappings)

template = "Invoice: {invoice_no}, Customer: {customer}"
print(parser.parse(template))
# Expected: "Invoice: SI-00001, Customer: Jane Doe"
```

**✅ Pass if:** Aliases work correctly

---

### ✅ 5. Complete Template Rendering Test

```python
from f_printnebula.engine.renderer import TemplateRenderer

# First, create a template via UI or:
template = frappe.get_doc({
    "doctype": "PrintNebula Template",
    "template_name": "Test Invoice Template",
    "doctype_link": "Sales Invoice",
    "is_active": 1,
    "header": "<h2>Invoice</h2>",
    "body": "<p>Customer: {customer_name}</p><p>Total: {grand_total}</p>",
    "footer": "<p>Thank you!</p>"
})
template.insert()

# Test rendering
renderer = TemplateRenderer("Test Invoice Template")
html = renderer.render("SI-00001")  # Use actual Sales Invoice name
print(html)
```

**✅ Pass if:** HTML is generated without errors

---

### ✅ 6. PDF Generation Test

```python
from f_printnebula.api.template_api import generate_pdf

# Generate PDF for a document
result = generate_pdf(
    template="Test Invoice Template",
    doctype="Sales Invoice",
    docname="SI-00001",
    output_format="pdf"
)

print(result)
# Should return: {'success': True, 'file_url': '...', 'file_size': ..., 'generation_time': ...}
```

**✅ Pass if:** PDF is generated and file_url is returned

---

### ✅ 7. Validator Test

```python
from f_printnebula.engine.validator import TemplateValidator

template_doc = frappe.get_doc("PrintNebula Template", "Test Invoice Template")
validator = TemplateValidator(template_doc)

result = validator.validate()
print(result)
# Should return: {'valid': True/False, 'errors': [], 'warnings': []}
```

**✅ Pass if:** Validation runs without crashing

---

## Real-World Test Scenario

### Create a Complete Invoice Template

1. **Go to PrintNebula Template**
2. **Create New Template:**
   - Template Name: "My Test Invoice"
   - Doctype: Sales Invoice
   - Is Active: ✓

3. **Header Section:**
```html
<div style="text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px;">
    <h1>TAX INVOICE</h1>
    <p>Invoice No: {name}</p>
    <p>Date: {posting_date}</p>
</div>
```

4. **Body Section:**
```html
<div style="margin: 20px 0;">
    <h3>Bill To:</h3>
    <p><strong>{customer_name}</strong></p>
    <p>{customer_address}</p>
</div>

<h3>Items:</h3>
<table border="1" cellpadding="8" cellspacing="0" style="width: 100%; border-collapse: collapse;">
    <thead>
        <tr style="background-color: #f0f0f0;">
            <th>#</th>
            <th>Item</th>
            <th>Qty</th>
            <th>Rate</th>
            <th>Amount</th>
        </tr>
    </thead>
    <tbody>
        {% for row in items %}
        <tr>
            <td>{row.idx}</td>
            <td>{row.item_name}</td>
            <td>{row.qty}</td>
            <td>{row.rate}</td>
            <td>{row.amount}</td>
        </tr>
        {% endfor %}
    </tbody>
    <tfoot>
        <tr style="font-weight: bold;">
            <td colspan="4" style="text-align: right;">Grand Total:</td>
            <td>{grand_total}</td>
        </tr>
    </tfoot>
</table>

{?payment_terms}
<div style="margin-top: 20px;">
    <h4>Payment Terms:</h4>
    <p>{payment_terms}</p>
</div>
{/payment_terms}
```

5. **Footer Section:**
```html
<div style="margin-top: 40px; border-top: 1px solid #ccc; padding-top: 10px; text-align: center; font-size: 10px;">
    <p>Thank you for your business!</p>
    <p>{terms}</p>
</div>
```

6. **Save and Test:**
   - Open any Sales Invoice
   - Use API or create custom button to generate PDF
   - Verify PDF output

---

## Unit Tests

Run comprehensive unit tests:

```bash
cd apps/f_printnebula
bench run-tests --app f_printnebula
```

Run specific test:

```bash
bench run-tests --app f_printnebula --module f_printnebula.tests.test_parser
```

---

## Performance Test

```python
import time
from f_printnebula.utils.pdf_generator import PDFGenerator

# Measure generation time
start = time.time()
generator = PDFGenerator("Test Invoice Template")
result = generator.generate("SI-00001", "pdf")
end = time.time()

print(f"Generation time: {end - start:.2f} seconds")
print(f"File size: {result['file_size'] / 1024:.2f} KB")

# Expected: < 3 seconds for standard invoice
```

---

## Load Test

```python
# Test batch generation
from f_printnebula.api.template_api import bulk_generate

result = bulk_generate(
    template="Test Invoice Template",
    doctype="Sales Invoice",
    filters={"docstatus": 1},
    background=True
)

print(result)
# Should queue job and return job_id
```

---

## Common Issues & Fixes

### Issue 1: "Template not found"
**Fix:** Ensure template is saved and is_active is checked

### Issue 2: "Field not found" warnings
**Fix:** Check field names in validation, ensure they exist in doctype

### Issue 3: Jinja2 syntax errors
**Fix:** Validate Jinja2 syntax - ensure {% for %} has {% endfor %}

### Issue 4: PDF generation fails
**Fix:** Ensure wkhtmltopdf is installed: `sudo apt-get install wkhtmltopdf`

### Issue 5: Formatters not working
**Fix:** Check formatter syntax: `{field|formatter:args}`

---

## Test Results Template

```
Date: YYYY-MM-DD
Tester: [Name]

✅ Variable Parsing: Pass/Fail
✅ Conditionals: Pass/Fail
✅ Formatters: Pass/Fail
✅ Field Mappings: Pass/Fail
✅ Template Rendering: Pass/Fail
✅ PDF Generation: Pass/Fail
✅ Validator: Pass/Fail
✅ Performance (<3s): Pass/Fail

Notes:
[Any issues or observations]
```

---

## Automated Test Coverage

Current test files:
- `tests/test_parser.py` - Variable parsing tests
- `tests/test_formatter.py` - Formatter engine tests
- `tests/test_integration.py` - Integration tests

Target coverage: >80%

---

**Happy Testing! 🧪**
