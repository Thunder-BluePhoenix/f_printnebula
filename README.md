# 🌌 PrintNebula

**Custom Template & Print Format Engine for Frappe/ERPNext**

A powerful, user-friendly template engine that enables non-technical users to create professional print formats using simple curly-brace syntax, loops, and dynamic PDF generation—without writing HTML or Jinja code.

---

## ✨ Features

### 🎨 Core Features
- **Word-like Template Editor**: Rich text editor for creating templates without coding
- **Native Word Documents (`.docx`)**: Upload Microsoft Word documents directly and inject Frappe data right into them!
- **Native Print Integration**: Custom templates appear automatically in the default Frappe "Print" buttons!
- **Curly-Brace Variables**: Simple `{field_name}` syntax for dynamic data insertion
- **Child Table Loops**: Automatic iteration through child records with `{% for row in items %}...{% endfor %}`
- **Field Mapping**: Create custom field aliases and transformations
- **Dynamic File Generation**: High-quality PDF and DOCX output with customizable options

### 🚀 Advanced Features
- **Mathematical Expressions**: Add calculations inline `{=qty * rate}` or arrays `{=sum(items.qty)}`
- **Chained Formatting**: Stack commands indefinitely `{posting_date|date:yyyy|upper}`
- **QR Codes & Barcodes**: Instantly inject inline base64 graphics via `{qrcode:url}`
- **Automated Mailer**: Trigger background jobs on-submit to email generated PDFs automatically
- **Batch Generation Engine**: Beautiful built-in Frappe desk UI for multi-selecting records and exporting zipped PDFs
- **Conditional Rendering**: Show/hide sections based on field values
- **Template Versioning**: Track all template changes over time
- **Multi-Format Export**: PDF, HTML, DOCX support

### 🌍 Additional Features
- **Multi-Language Support**: i18n ready with translation support
- **Custom CSS**: Style templates with custom CSS
- **Page Configuration**: Control page size, orientation, margins
- **Watermarks**: Add text or image watermarks
- **Usage Analytics**: Track template usage and performance
- **Template Library**: Searchable, categorizable template repository

---

## 📋 Requirements

- Frappe Framework v14+
- ERPNext v14+ (optional)
- wkhtmltopdf (for PDF generation)

---

## 🔧 Installation

### Method 1: Using Bench CLI (Recommended)

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/Thunder-BluePhoenix/f_printnebula
bench --site YOUR_SITE install-app f_printnebula
```

### Method 2: Manual Installation

```bash
cd apps
git clone https://github.com/Thunder-BluePhoenix/f_printnebula
cd ../sites/YOUR_SITE
bench install-app f_printnebula
bench migrate
```

---

## 🚀 Quick Start

### 1. Create Your First Template

1. Navigate to **PrintNebula Template** doctype
2. Click **New**
3. Fill in basic information:
   - **Template Name**: My Invoice Template
   - **Doctype**: Sales Invoice
   - **Is Active**: ✓
   - **Is Default**: ✓

### 2. Design Template Sections

**Header Section:**
```html
<div style="text-align: center;">
    <img src="{company_logo}" width="200" />
    <h2>{company}</h2>
    <p>{company_address}</p>
</div>
```

**Body Section:**
```html
<h1>Tax Invoice</h1>

<table>
    <tr>
        <td><strong>Invoice No:</strong> {name}</td>
        <td><strong>Date:</strong> {posting_date|date:dd-MM-yyyy}</td>
    </tr>
    <tr>
        <td><strong>Customer:</strong> {customer_name}</td>
        <td><strong>Status:</strong> {status}</td>
    </tr>
</table>

<h3>Items</h3>
<table border="1" cellpadding="5">
    <thead>
        <tr>
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
            <td>{row.rate|currency}</td>
            <td>{row.amount|currency}</td>
        </tr>
        {% endfor %}
    </tbody>
    <tfoot>
        <tr>
            <td colspan="4"><strong>Grand Total</strong></td>
            <td><strong>{grand_total|currency}</strong></td>
        </tr>
    </tfoot>
</table>
```

**Footer Section:**
```html
<div style="text-align: center; font-size: 10px;">
    <p>Thank you for your business!</p>
    <p>{terms_and_conditions}</p>
</div>
```

### 3. Generate PDF

#### Via UI:
1. Open any Sales Invoice
2. Click **Print** → Select "My Invoice Template"
3. Click **Download PDF**

#### Via API:
```python
import frappe
from f_printnebula.api import generate_pdf

result = generate_pdf(
    template="My Invoice Template",
    doctype="Sales Invoice",
    docname="SI-00001",
    output_format="pdf"
)

print(result['file_url'])
```

#### Via JavaScript:
```javascript
frappe.call({
    method: 'f_printnebula.api.template_api.generate_pdf',
    args: {
        template: 'My Invoice Template',
        doctype: 'Sales Invoice',
        docname: 'SI-00001'
    },
    callback: function(r) {
        window.open(r.message.file_url);
    }
});
```

---

## 📖 Template Syntax Guide

### Variables

**Basic Syntax:**
```
{field_name}
```

**Nested Fields:**
```
{customer.customer_name}
{territory.region}
```

**Formatted Output:**
```
{posting_date|date:dd-MM-yyyy}  → 18-11-2025
{grand_total|currency}           → $1,234.56
{qty|int}                        → 10
{description|upper}              → UPPERCASE TEXT
```

**Conditional Display:**
```
{?is_paid}PAID{/is_paid}
{?status=Submitted}Approved{/status}
```

**Default Values:**
```
{custom_field|default:"N/A"}
```

### Loops

**Basic Loop:**
```html
{% for row in items %}
  {row.item_name} - {row.qty}
{% endfor %}
```

**Loop with Conditions:**
```html
{% for row in items %}
  {% if row.qty > 10 %}
    <strong>{row.item_name}</strong> - BULK
  {% else %}
    {row.item_name}
  {% endif %}
{% endfor %}
```

**Loop Variables:**
```html
{% for row in items %}
  Row {loop.index} of {loop.length}
  {% if loop.first %}First Item{% endif %}
  {% if loop.last %}Last Item{% endif %}
{% endfor %}
```

**Math & Aggregations:**
```
{=qty * rate}                     → 150.00
{=sum(items.amount)}              → 4500.00
{=avg(items.rate)}                → 25.50
```

**Media Injection:**
```
{qrcode:https://example.com}      → [Inline Base64 QR Image]
{barcode:123456789}               → [Inline Base64 Barcode Image]
```

### Formatters

| Formatter | Usage | Example Output |
|-----------|-------|----------------|
| `date` | `{date\|date:dd-MM-yyyy}` | 18-11-2025 |
| `currency` | `{amount\|currency}` | $1,234.56 |
| `number` | `{value\|number:2}` | 123.45 |
| `percent` | `{rate\|percent:1}` | 15.5% |
| `upper` | `{text\|upper}` | UPPERCASE |
| `lower` | `{text\|lower}` | lowercase |
| `title` | `{text\|title}` | Title Case |

*Formatters can be chained infinitely: `{value|upper|currency|default:"N/A"}`*

---

## 🎯 Use Cases

### 1. Invoice Templates
Create custom invoice formats with company branding, terms, and conditions.

### 2. Purchase Orders
Generate purchase orders with supplier-specific layouts.

### 3. Delivery Notes
Print delivery notes with item details, quantities, and barcodes.

### 4. Reports
Create formatted reports with charts, tables, and summaries.

### 5. Certificates
Generate certificates with dynamic data and signatures.

### 6. Labels
Create shipping labels, barcode labels, or product labels.

---

## 🔌 API Reference

### Generate PDF

```python
generate_pdf(
    template: str,
    doctype: str,
    docname: str,
    output_format: str = "pdf",
    save_file: bool = True
) -> Dict
```

### Preview Template

```python
preview_template(
    template: str,
    docname: str = None,
    sample_data: Dict = None
) -> Dict
```

### Validate Template

```python
validate_template(template: str) -> Dict
```

### Bulk Generate

```python
bulk_generate(
    template: str,
    doctype: str,
    filters: Dict = None,
    output_format: str = "pdf",
    background: bool = True,
    email: bool = False
) -> Dict
```

---

## 🛠️ Configuration

### Page Setup

```json
{
    "page_size": "A4",              // A4, Letter, Legal, A5, A3
    "page_orientation": "Portrait",  // Portrait, Landscape
    "margin_top": "15",             // mm
    "margin_bottom": "15",          // mm
    "margin_left": "15",            // mm
    "margin_right": "15"            // mm
}
```

### Field Mappings

```json
{
    "inv_no": "name",
    "inv_date": "posting_date",
    "cust": "customer_name",
    "total": "grand_total"
}
```

### Custom CSS

```css
body {
    font-family: 'Arial', sans-serif;
    color: #333;
}

.header {
    background-color: #f0f0f0;
    padding: 20px;
}

table {
    border-collapse: collapse;
    width: 100%;
}
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│          Frontend (Frappe UI)           │
├─────────────────────────────────────────┤
│  Template Editor | Preview | Library    │
└─────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────┐
│              API Layer                   │
├─────────────────────────────────────────┤
│  generate_pdf | preview | validate      │
└─────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────┐
│         Rendering Engine                 │
├─────────────────────────────────────────┤
│  Parser | Formatter | Resolver          │
└─────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────┐
│          PDF Generator                   │
├─────────────────────────────────────────┤
│  wkhtmltopdf | File Storage             │
└─────────────────────────────────────────┘
```

---

## 🧪 Testing

```bash
# Run tests
cd apps/f_printnebula
bench run-tests --app f_printnebula

# Run specific test
bench run-tests --app f_printnebula --module f_printnebula.tests.test_renderer
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Setup

```bash
cd apps/f_printnebula
pre-commit install
```

Pre-commit tools:
- **ruff** - Python linting
- **eslint** - JavaScript linting
- **prettier** - Code formatting
- **pyupgrade** - Python syntax upgrades

---

## 📝 Changelog

### v1.1.0 (Current)
- Added `.docx` Microsoft Word native rendering
- Integrated templates natively into the Frappe standard "Print" UI
- Introduced `{=math}`, `{qrcode:...}`, and chained formatting logic
- Added Background Batch Generator UI Page
- Implemented `on_submit` Document Auto-Mailer

### v1.0.0 (2025-11-18)
- Initial release
- Core template rendering engine
- PDF generation
- Multi-section editor
- Field mappings and formatters
- Child table loops
- Template versioning
- Access control
- Preview functionality

---

## 🐛 Known Issues

- None at this time

---

## 📚 Documentation

For detailed documentation, see:
- [PRD (Product Requirements Document)](PRD_PrintNebula.md)
- [User Guide](USER_GUIDE.md)

---

## 💬 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/Thunder-BluePhoenix/f_printnebula/issues)
- **Discussions**: [Ask questions or share ideas](https://github.com/Thunder-BluePhoenix/f_printnebula/discussions)
- **Email**: bluephoenix00995@gmail.com

---

## 📄 License

GPL-3.0

---

## 👏 Credits

Created and maintained by **Thunder BluePhoenix**

Special thanks to:
- Frappe Framework team
- ERPNext community
- All contributors

---

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐

---

**Made with ❤️ for the Frappe/ERPNext community**
