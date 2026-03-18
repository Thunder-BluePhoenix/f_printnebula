# PrintNebula User Guide

Welcome to PrintNebula! This guide will walk you through the process of utilizing the powerful document engine to produce highly customized, dynamic PDFs and Word documents natively within Frappe.

---

## Table of Contents
1. [Core Syntaxes](#core-syntaxes)
2. [Formatters and Logic](#formatters-and-logic)
3. [Math & Aggregations](#math--aggregations)
4. [Media: QR Codes & Barcodes](#media-qr-codes--barcodes)
5. [Microsoft Word `.docx` Templating](#microsoft-word-docx-templating)
6. [Native Print Dialog Integration](#native-print-dialog-integration)
7. [Automated Email Deliveries](#automated-email-deliveries)
8. [Batch Bulk Generations (UI)](#batch-bulk-generations-ui)

---

## Core Syntaxes

PrintNebula substitutes curly-brace tags into physical document values.

**Standard Field Insertion:**
```html
<p>Hello {customer_name}, your balance is {outstanding_amount}.</p>
```

**Nested (Linked) Fields:**
```html
<p>Your regional representative is {territory.territory_manager_name}.</p>
```

**Child Tables (Jinja Loops):**
```html
<table>
  {% for row in items %}
  <tr>
    <td>{row.item_code}</td>
    <td>{row.qty}</td>
  </tr>
  {% endfor %}
</table>
```

## Formatters and Logic

Formatters modify the data dynamically. You can chain as many formatters as needed by separating them with a pipe `|` character.

```html
<!-- Single Formatter -->
<p>Total: {grand_total|currency}</p>

<!-- Chained Formatter (Date string -> Formatted -> Uppercase) -->
<p>Valid Until: {valid_till|date:dd-MMM-yyyy|upper}</p>

<!-- Fallback defaults -->
<p>Tax ID: {tax_id|default:"Not Provided"}</p>
```

### Conditionals
You can show or hide entire blocks of text depending on comparisons using the `{?field}...{/field}` syntax.

```html
{?status=Paid}
  <div class="stamp-paid">PAID IN FULL</div>
{/status}

{?outstanding_amount>0}
  <p>Please remit payment within 15 days.</p>
{/outstanding_amount}
```

## Math & Aggregations

Need to run dynamic equations without creating Frappe Custom Fields? Use the inline equalizer tag `{=...}`. 

```html
<!-- Standard Arithmetic -->
<p>Net Profit: {=grand_total - total_taxes_and_charges}</p>
<p>Margin: {= (net_profit / grand_total) * 100 }%</p>

<!-- Child Table Aggregations -->
<p>Total Items Ordered: {=sum(items.qty)}</p>
<p>Average Item Cost: {=avg(items.rate)}</p>
<p>Total Line Items: {=count(items)}</p>
```

## Media: QR Codes & Barcodes

Adding scannable labels to PDFs no longer requires heavy server-storage overhead. PrintNebula calculates these completely in-memory and injects them as Base64.

```html
<!-- Generates a QR Code directing to the document's URL -->
{qrcode:https://your-domain.com/orders/{name}}

<!-- Generates a scannable 1D Barcode of the item -->
{barcode:item_code}
```

## Microsoft Word `.docx` Templating

If you prefer using Microsoft Word over HTML coding, PrintNebula natively parses `.docx` attachments leveraging `docxtpl`!

1. Open MS Word.
2. Type variables directly into the document exactly as you would in HTML: `Dear {customer_name}`.
3. You can even include logic operators: `{% for row in items %}` (on one line) and `{% endfor %}` after your table row. 
4. In Frappe, go to your **PrintNebula Template**, change the `Template Type` switch to **Word Document**.
5. Upload your `.docx` file using the Attach field.
6. Print! The system will evaluate your tags and generate a finalized, populated `.docx` file for download.

## Native Print Dialog Integration

PrintNebula perfectly shadows standard Frappe features.

When you create or update a PrintNebula Template, it automatically generates a shadow **Frappe Custom Print Format** in the background. 
This means your administrative users never need to leave their standard Sales Invoice or Purchase Order screens; they just click the native Frappe `Print` button, select your template from the dropdown, and generate the PDF!

*(Note: If generating a Word Document template, the Print view will provide a fallback message advising the user to click the PrintNebula API endpoint directly to receive the DOCX file)*.

## Automated Email Deliveries

You can configure templates to automatically fire off PDF emails to designated recipients upon DocType `Submit`.

1. Go to the PrintNebula Template.
2. Expand the **Auto-Email Settings** section.
3. Check **Enable Auto-Email on Submit**.
4. Define the `Email To Field` (i.e. if the target Doctype is Sales Invoice, you could enter `contact_email` or `customer`).
5. Set your Subject and Body text. You can use standard `{variables}` inside the email body too!
6. Done! Whenever a document enters the `Submitted` state, a background Frappe Job will queue up, render the PDF, and dispatch the Email natively.

## Batch Bulk Generations (UI)

Need to export 500 invoices securely at the end of the month?

1. Search for **PrintNebula Batch Generator** using the Awesomebar.
2. Select your Target Doctype and your Template.
3. Click "Fetch Documents" to load a selectable grid.
4. Check off the documents you wish to export.
5. Click **Generate PDFs**. 
6. Watch the live progress bar handle the queue asynchronously without crashing your browser.
7. Upon completion, click the link to download the `.zip` archive containing all your processed files.
