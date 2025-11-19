# 🌌 PRD — PrintNebula

**Custom Template & Print Format Engine for Frappe**
Version: 2.0
Owner: Thunder BluePhoenix
Status: Ready for Development
App Name: **printnebula**

---

## 1. Product Overview

### 1.1 Summary

**PrintNebula** is a comprehensive Frappe-based print template engine that empowers users to design fully custom, Word-like print formats using:

- **Multi-Section Editors**: Header / Body / Footer with rich text support
- **Curly-Brace Placeholders**: Simple `{field_key}` syntax for dynamic data
- **Child Table Loops**: Automatic iteration through child records
- **Field Mapping System**: Define custom aliases and transformations
- **Dynamic PDF Generation**: Server-side rendering with customization
- **Multi-Language Support**: Internationalization ready
- **Template Library**: Reusable, shareable templates
- **Preview & Testing**: Real-time preview with sample data
- **Version Control**: Track template changes over time
- **Access Control**: Role-based template management

The goal is to allow **non-developers and business users** to create expressive, professional print formats without touching HTML/Jinja, while providing **advanced features** for power users.

---

## 2. Goals & Objectives

### ✅ Primary Goals

1. **User Empowerment**: Enable non-technical users to create professional print templates
2. **Flexibility**: Support any Frappe doctype with dynamic field mapping
3. **Simplicity**: Provide intuitive curly-brace syntax for field insertion
4. **Power**: Support complex child table loops and nested data structures
5. **Quality**: Generate high-quality PDFs with custom styling
6. **Reusability**: Allow templates to be shared, cloned, and versioned
7. **Performance**: Fast rendering and PDF generation (<3 seconds)
8. **Scalability**: Handle large documents and complex templates

### ✅ Secondary Goals

1. Template marketplace/library for common formats
2. Multi-format export (PDF, DOCX, HTML)
3. Conditional rendering and business logic
4. Image/logo embedding and management
5. QR code and barcode generation
6. Digital signature integration
7. Email integration with templates
8. Batch printing capabilities

---

## 3. Target Users

| User Type | Use Case |
|-----------|----------|
| **ERPNext/Frappe Implementers** | Create custom formats for clients |
| **Business Users** | Design invoices, reports, certificates |
| **Developers** | Build complex templates with logic |
| **Document Designers** | Create branded, professional layouts |
| **QA/Test Teams** | Generate formatted test outputs |
| **Administrators** | Manage template library and access |
| **End Users** | Generate PDFs from documents |

---

## 4. Product Scope

### 4.1 ✅ Core Features (ALL IN SCOPE)

#### A. **PrintNebula Template** Doctype

**Master template definition with comprehensive fields:**

| Field Name | Type | Description |
|------------|------|-------------|
| `template_name` | Data | Unique template identifier |
| `doctype_link` | Link (DocType) | Target doctype for this template |
| `is_default` | Check | Set as default template for doctype |
| `is_active` | Check | Enable/disable template |
| `description` | Small Text | Template purpose and notes |
| **--- EDITOR SECTIONS ---** | | |
| `header` | HTML Editor | Header section (repeats on all pages) |
| `body` | HTML Editor | Main body content |
| `footer` | HTML Editor | Footer section (repeats on all pages) |
| **--- VARIABLE MAPPING ---** | | |
| `field_mappings` | Code (JSON) | Custom field aliases and transformations |
| `child_table_config` | Code (JSON) | Child table field definitions |
| `loop_templates` | Code (Text) | Loop syntax for child tables |
| **--- STYLING ---** | | |
| `custom_css` | Code (CSS) | Custom CSS styling |
| `page_size` | Select | A4, Letter, Legal, A5, Custom |
| `page_orientation` | Select | Portrait, Landscape |
| `margin_top` | Data | Top margin (mm) |
| `margin_bottom` | Data | Bottom margin (mm) |
| `margin_left` | Data | Left margin (mm) |
| `margin_right` | Data | Right margin (mm) |
| **--- ADVANCED ---** | | |
| `enable_watermark` | Check | Add watermark to PDF |
| `watermark_text` | Data | Watermark text |
| `watermark_image` | Attach Image | Watermark image |
| `enable_header_footer` | Check | Show header/footer on all pages |
| `page_numbering` | Check | Enable page numbers |
| `page_number_format` | Data | Format: "Page {page} of {total}" |
| **--- CONDITIONAL LOGIC ---** | | |
| `conditions` | Code (JSON) | Show/hide sections based on conditions |
| `computed_fields` | Code (Python) | Calculate custom values |
| **--- LOCALIZATION ---** | | |
| `language` | Link (Language) | Template language |
| `date_format` | Data | Custom date format |
| `number_format` | Data | Custom number format |
| `currency_format` | Data | Custom currency format |
| **--- VERSION CONTROL ---** | | |
| `version` | Data | Template version number |
| `parent_template` | Link (PrintNebula Template) | Cloned from |
| `change_log` | Text | Version change history |
| **--- ACCESS CONTROL ---** | | |
| `allowed_roles` | Table | Roles that can use this template |
| `is_public` | Check | Available to all users |
| **--- METADATA ---** | | |
| `usage_count` | Int | Times template used |
| `last_used` | Datetime | Last usage timestamp |
| `created_by` | Link (User) | Template creator |
| `tags` | Data | Searchable tags |

#### B. **Curly-Brace Field Replacement Engine**

**Smart field resolution with advanced features:**

```
Basic Syntax:
{name} → doc.name
{customer_name} → doc.customer_name
{grand_total} → doc.grand_total

Nested Fields:
{customer.customer_name} → doc.customer's customer_name
{territory.region} → doc.territory's region

Formatting:
{posting_date|date:dd-mm-yyyy} → Formatted date
{grand_total|currency} → Formatted currency
{qty|int} → Integer formatting
{description|upper} → Uppercase text

Conditional Display:
{?is_paid}PAID{/is_paid} → Show only if is_paid is true
{?status=Submitted}Approved{/status} → Conditional content

Default Values:
{custom_field|default:"N/A"} → Show "N/A" if empty

Calculations:
{=grand_total - total_taxes} → Simple math
{=qty * rate} → Computed values
```

**Features:**
- Automatic field type detection
- Safe null handling (no errors on missing fields)
- Recursive field resolution
- Custom formatter functions
- Locale-aware formatting

#### C. **Child Table Loop Engine**

**Powerful iteration with nested support:**

```jinja
Basic Loop:
{% for row in items %}
  {row.idx}. {row.item_name} - {row.qty} x {row.rate} = {row.amount}
{% endfor %}

Loop with Conditions:
{% for row in items %}
  {% if row.qty > 10 %}
    <strong>{row.item_name}</strong> - BULK ORDER
  {% else %}
    {row.item_name}
  {% endif %}
{% endfor %}

Nested Loops:
{% for tax in taxes %}
  Tax: {tax.description}
  {% for item in items %}
    {item.item_name}: {item.tax_amount}
  {% endfor %}
{% endfor %}

Loop Counters:
{% for row in items %}
  Row {loop.index} of {loop.length}
  First: {loop.first}, Last: {loop.last}
{% endfor %}

Calculations in Loops:
{% for row in items %}
  Total: {=row.qty * row.rate}
  Discount: {=row.amount * row.discount_percentage / 100}
{% endfor %}
```

**Features:**
- Full Jinja2 syntax support
- Loop variables (index, first, last, length)
- Nested loop support
- Conditional rendering within loops
- Aggregate functions (sum, avg, count)

#### D. **Multi-Section Print Format Engine**

**Intelligent section management:**

```
Structure:
┌─────────────────────────┐
│       HEADER            │  ← Repeats on every page
│  (Logo, Company Info)   │
├─────────────────────────┤
│                         │
│         BODY            │  ← Main content
│   (Dynamic content)     │
│                         │
├─────────────────────────┤
│       FOOTER            │  ← Repeats on every page
│  (Terms, Page Numbers)  │
└─────────────────────────┘
```

**Features:**
- Independent section editing
- Section-level visibility rules
- Page break control
- Running headers/footers
- First-page-different header option
- Last-page-different footer option

#### E. **Variable Mapping & Transformation System**

**Flexible field aliasing and data transformation:**

```json
{
  "field_mappings": {
    "inv_no": "name",
    "inv_date": "posting_date",
    "cust": "customer_name",
    "total": "grand_total",
    "status_badge": {
      "field": "status",
      "transform": "status_to_badge",
      "params": {
        "Submitted": "✅ Approved",
        "Draft": "📝 Draft",
        "Cancelled": "❌ Cancelled"
      }
    },
    "due_in_days": {
      "type": "computed",
      "expression": "(due_date - posting_date).days"
    }
  },
  "child_table_mappings": {
    "items": {
      "code": "item_code",
      "name": "item_name",
      "qty": "qty",
      "price": "rate",
      "total": "amount",
      "tax_rate": {
        "field": "item_tax_template",
        "transform": "get_tax_rate"
      }
    }
  }
}
```

**Transformation Functions:**
- `upper`, `lower`, `title` - Text case
- `date`, `datetime`, `time` - Date formatting
- `currency`, `number`, `percent` - Number formatting
- `round`, `ceil`, `floor` - Math operations
- `replace`, `regex` - String operations
- Custom Python functions via hooks

#### F. **PDF Generation Engine**

**High-quality PDF output with advanced options:**

**Features:**
- **Multiple Engines**: wkhtmltopdf, WeasyPrint, Playwright
- **Quality Settings**: DPI, compression, image quality
- **Security**: Password protection, permissions
- **Metadata**: Title, author, subject, keywords
- **Watermarks**: Text or image based
- **Headers/Footers**: Dynamic page numbering
- **TOC Generation**: Automatic table of contents
- **Bookmarks**: PDF navigation structure
- **Attachments**: Embed files in PDF
- **Digital Signatures**: Sign PDFs automatically
- **Batch Generation**: Multiple documents at once
- **Background Jobs**: Queue long-running renders
- **Caching**: Smart template caching

**Configuration:**
```json
{
  "pdf_engine": "wkhtmltopdf",
  "quality": "high",
  "dpi": 300,
  "compression": "medium",
  "password": null,
  "permissions": {
    "print": true,
    "modify": false,
    "copy": true
  },
  "metadata": {
    "title": "{name}",
    "author": "{company}",
    "subject": "Invoice",
    "keywords": "invoice, sales"
  }
}
```

#### G. **Template Preview System**

**Real-time preview with multiple modes:**

**Preview Modes:**
1. **Live Preview**: Real-time rendering as you type
2. **Sample Data Preview**: Preview with mock data
3. **Document Preview**: Select actual document to preview
4. **Mobile Preview**: Responsive preview
5. **Print Preview**: See exactly how PDF will look
6. **Diff Preview**: Compare template versions

**Features:**
- Side-by-side editor and preview
- Syntax highlighting in code fields
- Error highlighting and validation
- Variable autocomplete
- Field suggestions from doctype
- Undo/redo functionality
- Auto-save drafts

#### H. **Template Library & Management**

**Centralized template repository:**

**Features:**
- **Template Categories**: Invoice, Report, Certificate, Label, etc.
- **Template Tags**: Searchable, filterable tags
- **Template Ratings**: User ratings and reviews
- **Template Cloning**: One-click duplicate
- **Template Import/Export**: JSON/ZIP format
- **Template Sharing**: Share with other sites
- **Template Marketplace**: Public template repository
- **Template Versioning**: Track all changes
- **Template Comparison**: Diff between versions
- **Template Backup**: Automatic backups
- **Template Restore**: Rollback to previous version

#### I. **Conditional Rendering & Business Logic**

**Advanced template logic:**

```json
{
  "conditions": [
    {
      "section": "discount_section",
      "show_if": "discount_amount > 0"
    },
    {
      "section": "tax_details",
      "show_if": "country == 'India'"
    },
    {
      "field": "gst_number",
      "show_if": "is_gst_applicable == 1"
    }
  ],
  "computed_fields": {
    "days_overdue": "(nowdate() - due_date).days if status == 'Overdue' else 0",
    "payment_status_color": "'red' if outstanding_amount > 0 else 'green'",
    "discount_percentage": "(discount_amount / total) * 100"
  }
}
```

**Supported Operators:**
- Comparison: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Logical: `and`, `or`, `not`
- Membership: `in`, `not in`
- Pattern: `contains`, `startswith`, `endswith`
- Null check: `is_set`, `is_not_set`

#### J. **Image & Asset Management**

**Comprehensive media handling:**

**Features:**
- **Logo Management**: Multiple logos per template
- **Image Placeholders**: `{image:company_logo}`
- **Dynamic Images**: Load from document fields
- **Image Transformations**: Resize, crop, filters
- **QR Code Generation**: `{qrcode:invoice_url}`
- **Barcode Generation**: `{barcode:item_code}`
- **Chart Embedding**: Embed Frappe charts
- **Signature Fields**: Digital signature support
- **Image Caching**: CDN integration
- **Image Optimization**: Auto-compress for PDF

**Syntax:**
```
{image:logo|width:200|align:center}
{qrcode:https://example.com/invoice/{name}|size:100}
{barcode:item_code|format:CODE128}
{signature:authorized_signatory|height:50}
{chart:sales_trend|width:400|height:200}
```

#### K. **Multi-Language & Localization**

**Complete i18n support:**

**Features:**
- **Translation System**: Integrate with Frappe translations
- **Language-Specific Templates**: One template per language
- **Auto-Translation**: Translate field labels
- **RTL Support**: Right-to-left languages
- **Currency Formatting**: Locale-aware currency
- **Date Formatting**: Regional date formats
- **Number Formatting**: Regional number formats
- **Custom Dictionaries**: Template-specific translations

**Example:**
```json
{
  "translations": {
    "en": {
      "invoice_title": "Tax Invoice",
      "customer_label": "Customer"
    },
    "hi": {
      "invoice_title": "कर चालान",
      "customer_label": "ग्राहक"
    },
    "es": {
      "invoice_title": "Factura Fiscal",
      "customer_label": "Cliente"
    }
  }
}
```

#### L. **Access Control & Security**

**Role-based template management:**

**Features:**
- **Role Permissions**: Who can create/edit/use templates
- **Template Ownership**: Creator has special rights
- **Public/Private Templates**: Visibility control
- **Template Approval Workflow**: Review before use
- **Audit Trail**: Track all template changes
- **Template Locking**: Prevent accidental edits
- **Secure Field Masking**: Hide sensitive data
- **Watermark for Drafts**: Mark non-final documents
- **PDF Permissions**: Control print/copy/modify

**Role Configuration:**
```json
{
  "allowed_roles": [
    {
      "role": "Accounts Manager",
      "permissions": ["read", "write", "create", "delete"]
    },
    {
      "role": "Accounts User",
      "permissions": ["read", "use"]
    }
  ]
}
```

#### M. **Batch Operations & Automation**

**Bulk processing capabilities:**

**Features:**
- **Bulk PDF Generation**: Generate PDFs for multiple documents
- **Scheduled Generation**: Cron-based PDF generation
- **Email Integration**: Auto-email generated PDFs
- **Print Queue**: Queue management for large batches
- **Background Jobs**: Non-blocking generation
- **Progress Tracking**: Real-time progress updates
- **Error Handling**: Retry failed generations
- **Export Logs**: Track all generations
- **Template Performance Metrics**: Usage analytics

**Batch API:**
```python
printnebula.generate_bulk(
    template="invoice_template_v2",
    doctype="Sales Invoice",
    filters={"status": "Submitted"},
    email=True,
    background=True
)
```

#### N. **Export Formats**

**Multi-format output:**

**Supported Formats:**
1. **PDF** - Primary format
2. **HTML** - Web preview
3. **DOCX** - Microsoft Word (via pandoc)
4. **ODT** - OpenOffice
5. **PNG/JPG** - Image export
6. **Email HTML** - Email-optimized HTML
7. **Print HTML** - Browser print-optimized

**Format-Specific Options:**
```json
{
  "pdf": {
    "encryption": true,
    "compression": "high"
  },
  "docx": {
    "include_images": true,
    "styles": "modern"
  },
  "html": {
    "inline_css": true,
    "responsive": true
  }
}
```

#### O. **Testing & Validation**

**Built-in quality assurance:**

**Features:**
- **Template Validator**: Check syntax errors
- **Field Validator**: Verify all fields exist
- **Loop Validator**: Check child table references
- **Preview with Test Data**: Mock data testing
- **Compare Output**: Before/after comparison
- **Performance Testing**: Render time metrics
- **Error Reporting**: Detailed error messages
- **Linting**: Template code quality checks
- **Accessibility Check**: PDF/UA compliance

#### P. **Integration & Extensions**

**Extensibility system:**

**Features:**
- **Hooks System**: Pre/post render hooks
- **Custom Formatters**: Register custom functions
- **External Data Sources**: Fetch data from APIs
- **Webhook Integration**: Trigger external systems
- **API Access**: REST API for template operations
- **JavaScript API**: Client-side customization
- **Plugin System**: Third-party extensions
- **Template Inheritance**: Extend base templates

**Hook Example:**
```python
# hooks.py
doc_events = {
    "Sales Invoice": {
        "before_print": "printnebula.custom.add_qr_code",
        "after_print": "printnebula.custom.log_print_event"
    }
}
```

---

## 5. User Stories

### Core Functionality
1. **US-1**: As a user, I want to design print formats using rich text editors, not HTML code
2. **US-2**: As an implementer, I want to add `{field_key}` to automatically fetch values from documents
3. **US-3**: As a developer, I want to define child table loops to show repetitive rows
4. **US-4**: As an accountant, I want consistent headers and footers across all pages
5. **US-5**: As a user, I want one-click PDF generation from any document

### Advanced Features
6. **US-6**: As a designer, I want to control page size, margins, and orientation
7. **US-7**: As a business user, I want to add my company logo to all templates
8. **US-8**: As an admin, I want to set default templates for each doctype
9. **US-9**: As a user, I want to preview templates before generating PDFs
10. **US-10**: As a developer, I want to add conditional sections that show based on data

### Multi-Language & Localization
11. **US-11**: As a global company, I want templates in multiple languages
12. **US-12**: As a user, I want dates and currencies formatted per my locale

### Template Management
13. **US-13**: As a power user, I want to clone existing templates and modify them
14. **US-14**: As an admin, I want to track who created and modified templates
15. **US-15**: As a team lead, I want to restrict template access by role

### Integration & Automation
16. **US-16**: As an accountant, I want to bulk-generate invoices for all submitted orders
17. **US-17**: As a user, I want PDFs automatically emailed to customers
18. **US-18**: As a warehouse manager, I want to print shipping labels in batches

### Quality & Testing
19. **US-19**: As a developer, I want to test templates with sample data before going live
20. **US-20**: As a quality analyst, I want to validate templates for errors

### Advanced Customization
21. **US-21**: As a developer, I want to add custom Python code for computed fields
22. **US-22**: As a designer, I want to add QR codes and barcodes to templates
23. **US-23**: As a compliance officer, I want to add watermarks to draft documents
24. **US-24**: As a legal team, I want to add digital signatures to PDFs

---

## 6. Functional Requirements

### Core Requirements

**FR-1: Template Selection**
- User must select a target Doctype
- Support all Frappe doctypes (Core + Custom)
- One template can support one doctype
- Multiple templates can exist per doctype

**FR-2: Multi-Section Editor**
- Three independent sections: Header, Body, Footer
- HTML Editor with rich text formatting
- Syntax highlighting for variables and loops
- Auto-save functionality
- Undo/redo support

**FR-3: Placeholder System**
- Support `{fieldname}` syntax
- Support nested fields `{table.field}`
- Support formatted output `{field|format}`
- Support conditional display `{?condition}...{/condition}`
- Auto-complete field names from doctype
- Validate field existence

**FR-4: Loop System**
- Support Jinja2 loop syntax
- Support nested loops
- Support loop variables (index, first, last)
- Support filters within loops
- Support calculations within loops
- Validate child table references

**FR-5: Variable Mapping Engine**
- JSON-based field aliasing
- Support computed fields
- Support transformation functions
- Support default values
- Validate mappings on save

**FR-6: Template Rendering**
- **Rendering Pipeline**:
  1. Load template sections
  2. Fetch document data
  3. Apply variable mappings
  4. Parse placeholders
  5. Execute loops
  6. Apply conditional logic
  7. Inject computed fields
  8. Apply formatting
  9. Combine sections
  10. Generate final HTML

**FR-7: PDF Generation**
- Convert HTML to PDF
- Support custom page sizes
- Support margins and orientation
- Support headers/footers on all pages
- Support page numbering
- Support watermarks
- Support encryption
- Download as attachment

**FR-8: Preview Mode**
- Live preview while editing
- Preview with selected document
- Preview with sample data
- Side-by-side comparison
- Error highlighting
- Performance metrics

**FR-9: Multi-Template Support**
- Multiple templates per doctype
- Template selection dropdown on print page
- Default template setting
- Template cloning
- Template versioning

**FR-10: Template Access Control**
- Role-based permissions
- Public/private templates
- Template ownership
- Approval workflows

### Advanced Requirements

**FR-11: Styling & Layout**
- Custom CSS support
- Page size configuration
- Margin configuration
- Font selection
- Color schemes
- Responsive design for screen preview

**FR-12: Asset Management**
- Image upload and storage
- Logo management
- Dynamic image loading
- QR code generation
- Barcode generation
- Chart embedding

**FR-13: Localization**
- Multi-language support
- Locale-based formatting
- Translation management
- RTL support
- Currency conversion

**FR-14: Batch Operations**
- Bulk PDF generation
- Background job processing
- Progress tracking
- Email integration
- Export to file system
- Scheduled generation

**FR-15: Export Formats**
- PDF (primary)
- HTML
- DOCX
- PNG/JPG
- Email-optimized HTML

**FR-16: Testing & Validation**
- Template syntax validation
- Field existence checking
- Loop validation
- Preview with test data
- Performance profiling
- Error reporting

**FR-17: Analytics & Reporting**
- Usage tracking
- Performance metrics
- Error logs
- Popular templates
- User activity

**FR-18: Integration**
- REST API
- Webhooks
- Custom hooks
- External data sources
- Plugin system

---

## 7. Non-Functional Requirements

### Performance
**NFR-1: Rendering Speed**
- Template rendering must complete in < 1 second for simple templates
- Template rendering must complete in < 3 seconds for complex templates
- PDF generation must complete in < 5 seconds for standard documents
- Support documents up to 100 pages
- Support child tables up to 1000 rows

**NFR-2: Scalability**
- Support 1000+ concurrent template renders
- Support 10,000+ stored templates
- Handle 100+ parallel PDF generations
- Efficient caching mechanisms

### Usability
**NFR-3: User Experience**
- Zero HTML/Jinja knowledge required for basic usage
- Intuitive drag-and-drop (future)
- Clear error messages
- Comprehensive documentation
- Video tutorials
- Interactive template wizard

**NFR-4: Accessibility**
- Keyboard navigation support
- Screen reader compatible
- WCAG 2.1 Level AA compliance
- Generated PDFs meet PDF/UA standards

### Reliability
**NFR-5: Robustness**
- Loop parsing must not crash on invalid syntax
- Field resolution must handle missing fields gracefully
- PDF generation must have retry mechanism
- Auto-save to prevent data loss
- Template validation before save

**NFR-6: Data Integrity**
- Version control for all templates
- Audit trail for changes
- Backup and restore capability
- Prevent accidental deletions

### Security
**NFR-7: Security**
- Sanitize user input to prevent XSS
- Validate Python code in computed fields
- Prevent code injection in templates
- Secure file storage
- Encrypted PDF support
- Access control enforcement
- Audit logging

**NFR-8: Privacy**
- Data isolation between tenants (if multi-tenant)
- Secure API authentication
- Permission-based data access

### Maintainability
**NFR-9: Code Quality**
- Modular architecture
- Comprehensive unit tests (>80% coverage)
- Integration tests for key workflows
- API documentation
- Code comments and docstrings

**NFR-10: Extensibility**
- Plugin architecture
- Hook system for customization
- Clear extension points
- Backward compatibility

### Compatibility
**NFR-11: Platform Support**
- Frappe v14+ compatibility
- ERPNext v14+ compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile responsive design
- Cross-platform PDF rendering

---

## 8. Architecture Design

### 8.1 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
├─────────────────────────────────────────────────────────┤
│  Template Editor  │  Preview Pane  │  Template Library  │
│  ────────────────────────────────────────────────────── │
│  Rich Text Editor │  Live Preview  │  Search & Filter   │
│  Code Editor      │  Error Display │  Clone & Import    │
│  Field Browser    │  PDF Viewer    │  Version History   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    API Layer                             │
├─────────────────────────────────────────────────────────┤
│  /api/template/create                                    │
│  /api/template/preview                                   │
│  /api/template/generate_pdf                              │
│  /api/template/validate                                  │
│  /api/batch/generate                                     │
│  /api/export/{format}                                    │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Business Logic Layer                    │
├─────────────────────────────────────────────────────────┤
│  Template Manager    │  Rendering Engine                 │
│  ──────────────────────────────────────────────────────  │
│  - CRUD Operations   │  - Variable Parser                │
│  - Validation        │  - Loop Processor                 │
│  - Version Control   │  - Conditional Logic              │
│  - Access Control    │  - Field Resolver                 │
│                      │  - Formatter Engine               │
├─────────────────────────────────────────────────────────┤
│  PDF Generator       │  Asset Manager                    │
│  ──────────────────────────────────────────────────────  │
│  - HTML to PDF       │  - Image Processing               │
│  - Quality Control   │  - QR/Barcode Gen                 │
│  - Encryption        │  - Logo Management                │
│  - Digital Signature │  - Chart Embedding                │
├─────────────────────────────────────────────────────────┤
│  Batch Processor     │  Integration Hub                  │
│  ──────────────────────────────────────────────────────  │
│  - Job Queue         │  - Webhooks                       │
│  - Progress Tracking │  - External APIs                  │
│  - Error Handling    │  - Email Service                  │
│  - Scheduling        │  - Plugin Loader                  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Data Layer                            │
├─────────────────────────────────────────────────────────┤
│  Frappe ORM  │  File Storage  │  Cache Layer            │
│  ────────────────────────────────────────────────────── │
│  Templates   │  Generated PDFs│  Redis Cache            │
│  Metadata    │  Images/Assets │  Template Cache         │
│  Audit Logs  │  Backups       │  Rendered HTML Cache    │
└─────────────────────────────────────────────────────────┘
```

### 8.2 Template Rendering Flow

```
┌──────────────────────┐
│   User Request       │
│   (Generate PDF)     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────┐
│  1. Fetch Template & Document    │
│  - Load template from DB         │
│  - Fetch document data           │
│  - Check permissions             │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  2. Pre-Processing               │
│  - Apply variable mappings       │
│  - Compute calculated fields     │
│  - Fetch related documents       │
│  - Load child tables             │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  3. Template Parsing             │
│  ┌─────────────────────────────┐ │
│  │ Header Section              │ │
│  │ - Parse variables           │ │
│  │ - Apply formatting          │ │
│  └─────────────────────────────┘ │
│  ┌─────────────────────────────┐ │
│  │ Body Section                │ │
│  │ - Parse variables           │ │
│  │ - Process loops             │ │
│  │ - Apply conditions          │ │
│  └─────────────────────────────┘ │
│  ┌─────────────────────────────┐ │
│  │ Footer Section              │ │
│  │ - Parse variables           │ │
│  │ - Add page numbers          │ │
│  └─────────────────────────────┘ │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  4. HTML Generation              │
│  - Combine sections              │
│  - Apply CSS styling             │
│  - Inject custom CSS             │
│  - Add watermarks                │
│  - Embed images                  │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  5. PDF Generation               │
│  - Convert HTML to PDF           │
│  - Apply page settings           │
│  - Add headers/footers           │
│  - Apply security settings       │
│  - Optimize file size            │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  6. Post-Processing              │
│  - Save to file system           │
│  - Update usage counter          │
│  - Log generation event          │
│  - Trigger webhooks              │
│  - Send email (if configured)    │
└──────────┬───────────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  7. Response                     │
│  - Return PDF file               │
│  - Return metadata               │
│  - Return generation stats       │
└──────────────────────────────────┘
```

### 8.3 Component Architecture

**Core Components:**

1. **TemplateManager**
   - Template CRUD operations
   - Validation and versioning
   - Access control enforcement

2. **VariableParser**
   - Parse `{field}` placeholders
   - Resolve nested fields
   - Apply formatters
   - Handle conditionals

3. **LoopProcessor**
   - Parse Jinja2 loops
   - Iterate child tables
   - Support nested loops
   - Apply loop filters

4. **FieldResolver**
   - Fetch field values from documents
   - Handle missing fields
   - Apply transformations
   - Cache field metadata

5. **FormatterEngine**
   - Date/time formatting
   - Number formatting
   - Currency formatting
   - Custom formatters

6. **PDFGenerator**
   - HTML to PDF conversion
   - Page layout management
   - Header/footer injection
   - Watermark application
   - Encryption and security

7. **AssetManager**
   - Image storage and retrieval
   - QR/Barcode generation
   - Chart rendering
   - Logo management

8. **CacheManager**
   - Template caching
   - Rendered HTML caching
   - Field metadata caching
   - Invalidation strategies

---

## 9. Database Schema

### 9.1 PrintNebula Template

```sql
CREATE TABLE `tabPrintNebula Template` (
    `name` varchar(140) PRIMARY KEY,
    `template_name` varchar(140) UNIQUE,
    `doctype_link` varchar(140),
    `is_default` tinyint(1) DEFAULT 0,
    `is_active` tinyint(1) DEFAULT 1,
    `is_public` tinyint(1) DEFAULT 0,
    `description` text,

    -- Editor sections
    `header` longtext,
    `body` longtext,
    `footer` longtext,

    -- Mappings
    `field_mappings` longtext,
    `child_table_config` longtext,
    `loop_templates` longtext,

    -- Styling
    `custom_css` longtext,
    `page_size` varchar(20) DEFAULT 'A4',
    `page_orientation` varchar(20) DEFAULT 'Portrait',
    `margin_top` varchar(10) DEFAULT '15',
    `margin_bottom` varchar(10) DEFAULT '15',
    `margin_left` varchar(10) DEFAULT '15',
    `margin_right` varchar(10) DEFAULT '15',

    -- Advanced
    `enable_watermark` tinyint(1) DEFAULT 0,
    `watermark_text` varchar(140),
    `watermark_image` text,
    `enable_header_footer` tinyint(1) DEFAULT 1,
    `page_numbering` tinyint(1) DEFAULT 1,
    `page_number_format` varchar(100),

    -- Logic
    `conditions` longtext,
    `computed_fields` longtext,

    -- Localization
    `language` varchar(140),
    `date_format` varchar(50),
    `number_format` varchar(50),
    `currency_format` varchar(50),

    -- Version control
    `version` varchar(20),
    `parent_template` varchar(140),
    `change_log` longtext,

    -- Metadata
    `usage_count` int(11) DEFAULT 0,
    `last_used` datetime,
    `created_by` varchar(140),
    `tags` varchar(255),

    -- Standard Frappe fields
    `creation` datetime,
    `modified` datetime,
    `modified_by` varchar(140),
    `owner` varchar(140),
    `docstatus` int(1) DEFAULT 0,
    `idx` int(8) DEFAULT 0
);
```

### 9.2 PrintNebula Template Role (Child Table)

```sql
CREATE TABLE `tabPrintNebula Template Role` (
    `name` varchar(140) PRIMARY KEY,
    `parent` varchar(140),
    `parentfield` varchar(140),
    `parenttype` varchar(140),
    `role` varchar(140),
    `can_create` tinyint(1) DEFAULT 0,
    `can_edit` tinyint(1) DEFAULT 0,
    `can_delete` tinyint(1) DEFAULT 0,
    `can_use` tinyint(1) DEFAULT 1,
    `idx` int(8)
);
```

### 9.3 PrintNebula Generation Log

```sql
CREATE TABLE `tabPrintNebula Generation Log` (
    `name` varchar(140) PRIMARY KEY,
    `template` varchar(140),
    `doctype` varchar(140),
    `document_name` varchar(140),
    `generated_by` varchar(140),
    `generation_time` float,
    `file_size` int(11),
    `format` varchar(20),
    `status` varchar(20),
    `error_message` text,
    `timestamp` datetime,
    `idx` int(8)
);
```

### 9.4 PrintNebula Template Version

```sql
CREATE TABLE `tabPrintNebula Template Version` (
    `name` varchar(140) PRIMARY KEY,
    `template` varchar(140),
    `version_number` varchar(20),
    `change_summary` text,
    `template_data` longtext,
    `created_by` varchar(140),
    `creation` datetime,
    `idx` int(8)
);
```

---

## 10. API Specification

### 10.1 REST API Endpoints

#### **Template Management**

**Create Template**
```
POST /api/resource/PrintNebula Template
Content-Type: application/json

{
    "template_name": "Invoice Template v1",
    "doctype_link": "Sales Invoice",
    "header": "<div>...</div>",
    "body": "<div>...</div>",
    "footer": "<div>...</div>",
    ...
}
```

**Get Template**
```
GET /api/resource/PrintNebula Template/{template_name}
```

**Update Template**
```
PUT /api/resource/PrintNebula Template/{template_name}
```

**Delete Template**
```
DELETE /api/resource/PrintNebula Template/{template_name}
```

**List Templates**
```
GET /api/resource/PrintNebula Template?fields=["name","template_name","doctype_link"]&filters=[["is_active","=",1]]
```

#### **Template Operations**

**Validate Template**
```
POST /api/method/printnebula.api.validate_template
{
    "template": "template_name"
}

Response:
{
    "valid": true,
    "errors": [],
    "warnings": ["Field 'custom_field' not found in doctype"]
}
```

**Preview Template**
```
POST /api/method/printnebula.api.preview_template
{
    "template": "template_name",
    "doctype": "Sales Invoice",
    "docname": "SI-00001"
}

Response:
{
    "html": "<html>...</html>",
    "render_time": 0.45
}
```

**Generate PDF**
```
POST /api/method/printnebula.api.generate_pdf
{
    "template": "template_name",
    "doctype": "Sales Invoice",
    "docname": "SI-00001",
    "options": {
        "format": "pdf",
        "quality": "high"
    }
}

Response:
{
    "file_url": "/private/files/SI-00001.pdf",
    "file_size": 245678,
    "generation_time": 1.23
}
```

**Clone Template**
```
POST /api/method/printnebula.api.clone_template
{
    "template": "template_name",
    "new_name": "Cloned Template"
}
```

**Export Template**
```
GET /api/method/printnebula.api.export_template?template=template_name&format=json

Response: (JSON file download)
{
    "template_data": {...},
    "metadata": {...}
}
```

**Import Template**
```
POST /api/method/printnebula.api.import_template
Content-Type: multipart/form-data

file: template.json
```

#### **Batch Operations**

**Bulk Generate PDFs**
```
POST /api/method/printnebula.api.bulk_generate
{
    "template": "template_name",
    "doctype": "Sales Invoice",
    "filters": {"status": "Submitted"},
    "email": true,
    "background": true
}

Response:
{
    "job_id": "batch-job-123",
    "total_documents": 50,
    "status": "queued"
}
```

**Check Batch Status**
```
GET /api/method/printnebula.api.batch_status?job_id=batch-job-123

Response:
{
    "job_id": "batch-job-123",
    "status": "running",
    "progress": 30,
    "total": 50,
    "completed": 15,
    "failed": 0
}
```

#### **Analytics**

**Template Usage Stats**
```
GET /api/method/printnebula.api.template_stats?template=template_name

Response:
{
    "usage_count": 1234,
    "last_used": "2025-11-18 10:30:00",
    "avg_generation_time": 1.45,
    "total_file_size": 52345678,
    "usage_by_user": {...}
}
```

### 10.2 Python API

```python
import printnebula

# Generate PDF
pdf_file = printnebula.generate(
    template="invoice_template_v1",
    doctype="Sales Invoice",
    docname="SI-00001",
    options={
        "format": "pdf",
        "quality": "high",
        "encrypt": True,
        "password": "secret"
    }
)

# Bulk generate
job = printnebula.bulk_generate(
    template="invoice_template_v1",
    doctype="Sales Invoice",
    filters={"status": "Submitted"},
    background=True,
    email=True
)

# Validate template
result = printnebula.validate_template("invoice_template_v1")

# Clone template
new_template = printnebula.clone_template(
    "invoice_template_v1",
    "invoice_template_v2"
)

# Get template stats
stats = printnebula.get_stats("invoice_template_v1")
```

### 10.3 JavaScript API

```javascript
// Generate PDF
frappe.call({
    method: 'printnebula.api.generate_pdf',
    args: {
        template: 'invoice_template_v1',
        doctype: 'Sales Invoice',
        docname: 'SI-00001'
    },
    callback: function(r) {
        window.open(r.message.file_url);
    }
});

// Preview template
printnebula.preview('invoice_template_v1', 'Sales Invoice', 'SI-00001');

// Validate template
printnebula.validate('invoice_template_v1').then(result => {
    console.log(result.valid);
});
```

---

## 11. UI/UX Design

### 11.1 Template Editor Screen

```
┌────────────────────────────────────────────────────────────────────┐
│  PrintNebula Template Editor                          [ Save ] [×] │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Template Name: [Invoice Template v1            ]                  │
│  Doctype:       [Sales Invoice ▼]                                  │
│  Status:        [✓] Active  [✓] Default  [ ] Public                │
│                                                                     │
├────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────┬──────────────────────────────────────┐ │
│  │ Editor (60%)          │ Preview (40%)                        │ │
│  ├───────────────────────┼──────────────────────────────────────┤ │
│  │                       │                                      │ │
│  │ 📋 Sections           │  [Refresh] [Test Data ▼] [PDF View] │ │
│  │ ├─ 📄 Header         │                                      │ │
│  │ ├─ 📝 Body           │  ┌────────────────────────────────┐ │ │
│  │ └─ 📃 Footer         │  │                                │ │ │
│  │                       │  │   Live Preview Pane            │ │ │
│  │ ⚙️  Configuration     │  │                                │ │ │
│  │ ├─ 🔤 Field Mappings │  │   [Rendered content here]      │ │ │
│  │ ├─ 🔁 Loop Config    │  │                                │ │ │
│  │ ├─ 🎨 Custom CSS     │  │                                │ │ │
│  │ └─ 📐 Page Setup     │  │                                │ │ │
│  │                       │  │                                │ │ │
│  │ ─────────────────────│  └────────────────────────────┘ │ │
│  │ Header Editor:        │                                      │ │
│  │ ┌───────────────────┐│                                      │ │
│  │ │[B][I][U] {x} img  ││  Variables Available:                │ │
│  │ ├───────────────────┤│  ┌────────────────────────────────┐ │ │
│  │ │                   ││  │ {name}                         │ │ │
│  │ │  <div>            ││  │ {customer_name}                │ │ │
│  │ │    {company_logo} ││  │ {posting_date}                 │ │ │
│  │ │    {company}      ││  │ {grand_total}                  │ │ │
│  │ │  </div>           ││  │ {status}                       │ │ │
│  │ │                   ││  │ [See all fields ▼]             │ │ │
│  │ └───────────────────┘│  └────────────────────────────────┘ │ │
│  │                       │                                      │ │
│  └───────────────────────┴──────────────────────────────────────┘ │
│                                                                     │
│  [ Preview with Document ] [ Validate ] [ Generate PDF ] [ Save ]  │
└────────────────────────────────────────────────────────────────────┘
```

### 11.2 Template Library Screen

```
┌────────────────────────────────────────────────────────────────────┐
│  PrintNebula Templates                      [+ New Template]       │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Search: [________________]  Doctype: [All ▼]  Status: [Active ▼] │
│                                                                     │
├─────────────────┬──────────────────────────────────────────────────┤
│ 📁 Categories   │  Templates (24)                                  │
│                 │                                                  │
│ ▼ Invoice (8)   │  ┌──────────────────────────────────────────┐  │
│ ▼ Report (6)    │  │ 📄 Invoice Template v1         [Edit][⋮] │  │
│ ▼ Certificate(3)│  │ Sales Invoice • Default • 1,234 uses     │  │
│ ▼ Label (4)     │  │ Last modified: 2 days ago                │  │
│ ▼ Other (3)     │  │ [Preview] [Clone] [Download]             │  │
│                 │  └──────────────────────────────────────────┘  │
│ 🏷️ Tags         │                                                  │
│ • Accounting    │  ┌──────────────────────────────────────────┐  │
│ • Sales         │  │ 📄 Purchase Order Template    [Edit][⋮] │  │
│ • Purchase      │  │ Purchase Order • Active • 456 uses       │  │
│ • HR            │  │ Last modified: 1 week ago                │  │
│ • Custom        │  │ [Preview] [Clone] [Download]             │  │
│                 │  └──────────────────────────────────────────┘  │
│                 │                                                  │
│                 │  ┌──────────────────────────────────────────┐  │
│                 │  │ 📊 Sales Report Template      [Edit][⋮] │  │
│                 │  │ Sales Report • Active • 789 uses         │  │
│                 │  │ Last modified: 3 days ago                │  │
│                 │  │ [Preview] [Clone] [Download]             │  │
│                 │  └──────────────────────────────────────────┘  │
│                 │                                                  │
└─────────────────┴──────────────────────────────────────────────────┘
```

### 11.3 Print Dialog (Enhanced)

```
┌────────────────────────────────────────────────────────────────────┐
│  Print: Sales Invoice SI-00001                             [×]     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Template: [Invoice Template v1 ▼]           [Preview] [Settings] │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                                                              │ │
│  │                     Preview Pane                             │ │
│  │                                                              │ │
│  │              [Rendered PDF preview here]                     │ │
│  │                                                              │ │
│  │                                                              │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  Format:   [● PDF  ○ HTML  ○ DOCX]                                │
│  Quality:  [High ▼]                                                │
│  Email to: [customer@example.com            ] [+]                  │
│                                                                     │
│  Advanced Options:                                                 │
│  [ ] Add watermark     [ ] Encrypt PDF     [ ] Digital signature   │
│                                                                     │
│            [Download PDF]  [Email]  [Print]  [Cancel]              │
└────────────────────────────────────────────────────────────────────┘
```

### 11.4 Batch Generate Dialog

```
┌────────────────────────────────────────────────────────────────────┐
│  Bulk PDF Generation                                       [×]     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Template:    [Invoice Template v1 ▼]                              │
│  Doctype:     [Sales Invoice ▼]                                    │
│                                                                     │
│  Filters:                                                          │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ Status      [Equals ▼]     [Submitted]                       │ │
│  │ Posting Date[Between▼]     [2025-01-01] to [2025-11-18]      │ │
│  │                                                 [+ Add Filter]│ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  Documents matched: 47                                             │
│                                                                     │
│  Options:                                                          │
│  [✓] Generate in background                                        │
│  [✓] Email to customers                                            │
│  [ ] Save to folder: [/Private/Files/Invoices/    ]               │
│                                                                     │
│  Email Template: [Invoice Email ▼]                                │
│                                                                     │
│                    [Start Generation]  [Cancel]                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 12. Milestones & Development Phases

### **Phase 1: Foundation (Week 1-2)** ✅ ALL IN SCOPE

**Milestone 1.1: App Setup**
- Create Frappe app structure
- Set up git repository
- Configure app hooks
- Basic documentation

**Milestone 1.2: Core Doctype**
- Create PrintNebula Template doctype
- Add all fields (header, body, footer, mappings, etc.)
- Set up permissions
- Create child table for roles

**Milestone 1.3: Basic Editor**
- HTML editor integration
- Code editor for mappings
- Basic field browser
- Save/load functionality

---

### **Phase 2: Rendering Engine (Week 3-4)** ✅ ALL IN SCOPE

**Milestone 2.1: Variable Parser**
- Implement `{field}` parser
- Nested field resolution
- Field formatters (date, currency, etc.)
- Error handling for missing fields

**Milestone 2.2: Loop Processor**
- Jinja2 loop parsing
- Child table iteration
- Nested loop support
- Loop variables (index, first, last)

**Milestone 2.3: Conditional Logic**
- Implement conditional rendering
- Support for `{?condition}...{/condition}`
- Boolean operators
- Field comparisons

**Milestone 2.4: Computed Fields**
- Python expression evaluation
- Safe execution sandbox
- Custom function support
- Formula validation

---

### **Phase 3: PDF Generation (Week 5-6)** ✅ ALL IN SCOPE

**Milestone 3.1: Basic PDF**
- HTML to PDF conversion (wkhtmltopdf)
- Page size and orientation
- Basic margins
- Single-page documents

**Milestone 3.2: Advanced PDF**
- Multi-page support
- Headers/footers on all pages
- Page numbering
- Watermarks
- PDF encryption

**Milestone 3.3: Quality & Performance**
- DPI and quality settings
- File size optimization
- Caching mechanism
- Performance profiling

---

### **Phase 4: Template Management (Week 7-8)** ✅ ALL IN SCOPE

**Milestone 4.1: Template Library**
- Template listing page
- Search and filter
- Categories and tags
- Template preview

**Milestone 4.2: Template Operations**
- Clone template
- Import/export templates
- Version control
- Change tracking

**Milestone 4.3: Access Control**
- Role-based permissions
- Public/private templates
- Template ownership
- Approval workflow

---

### **Phase 5: Advanced Features (Week 9-10)** ✅ ALL IN SCOPE

**Milestone 5.1: Asset Management**
- Image upload and storage
- Logo management
- QR code generation
- Barcode generation
- Chart embedding

**Milestone 5.2: Styling & Layout**
- Custom CSS support
- Page setup (A4, Letter, etc.)
- Margin configuration
- Font selection
- Responsive preview

**Milestone 5.3: Preview System**
- Live preview
- Side-by-side editor
- Preview with sample data
- Preview with real documents
- Error highlighting

---

### **Phase 6: Batch & Integration (Week 11-12)** ✅ ALL IN SCOPE

**Milestone 6.1: Batch Processing**
- Bulk PDF generation
- Background job queue
- Progress tracking
- Error handling and retry

**Milestone 6.2: Email Integration**
- Email generated PDFs
- Email template integration
- Batch emailing
- Email tracking

**Milestone 6.3: API Development**
- REST API endpoints
- Python API
- JavaScript API
- Webhook support

---

### **Phase 7: Localization & Multi-Format (Week 13-14)** ✅ ALL IN SCOPE

**Milestone 7.1: Localization**
- Multi-language support
- Translation system
- Locale-based formatting
- RTL support

**Milestone 7.2: Multi-Format Export**
- HTML export
- DOCX export (via pandoc)
- PNG/JPG export
- Email-optimized HTML

**Milestone 7.3: Date/Number Formatting**
- Custom date formats
- Custom number formats
- Currency conversion
- Regional settings

---

### **Phase 8: Testing & Quality (Week 15-16)** ✅ ALL IN SCOPE

**Milestone 8.1: Template Validation**
- Syntax validator
- Field existence checker
- Loop validator
- Error reporting

**Milestone 8.2: Testing Framework**
- Unit tests (>80% coverage)
- Integration tests
- Performance tests
- Load testing

**Milestone 8.3: Documentation**
- User guide
- Developer documentation
- API documentation
- Video tutorials
- Sample templates

---

### **Phase 9: Analytics & Monitoring (Week 17)** ✅ ALL IN SCOPE

**Milestone 9.1: Usage Analytics**
- Template usage tracking
- Performance metrics
- Error logging
- User activity tracking

**Milestone 9.2: Admin Dashboard**
- Usage statistics
- Popular templates
- Error reports
- Performance graphs

---

### **Phase 10: Polish & Launch (Week 18)** ✅ ALL IN SCOPE

**Milestone 10.1: UI/UX Polish**
- Responsive design
- Accessibility improvements
- Error message improvements
- User onboarding

**Milestone 10.2: Performance Optimization**
- Query optimization
- Caching strategies
- Asset optimization
- Load time improvements

**Milestone 10.3: Security Audit**
- XSS prevention
- Code injection prevention
- Permission enforcement
- Security documentation

**Milestone 10.4: Launch Preparation**
- Final testing
- Bug fixes
- Release notes
- Marketing materials

---

## 13. Future Enhancements (Post-Launch Roadmap)

### **Enhancement 1: Visual Template Builder** 🚀
- Drag-and-drop interface
- WYSIWYG editor
- Visual field placement
- Template blocks/widgets
- **Timeline**: 2-3 months post-launch

### **Enhancement 2: Template Marketplace** 🏪
- Public template repository
- Template ratings and reviews
- Template monetization
- Community contributions
- **Timeline**: 3-4 months post-launch

### **Enhancement 3: AI-Powered Features** 🤖
- Auto-generate templates from samples
- Smart field suggestions
- Template optimization recommendations
- Natural language template creation
- **Timeline**: 4-6 months post-launch

### **Enhancement 4: Advanced Charting** 📊
- Embedded Chart.js/D3.js charts
- Dynamic data visualization
- Chart templates
- Real-time data charts
- **Timeline**: 2-3 months post-launch

### **Enhancement 5: Mobile App** 📱
- iOS/Android apps
- Mobile template editor
- On-the-go PDF generation
- Offline capability
- **Timeline**: 6-8 months post-launch

### **Enhancement 6: Collaborative Editing** 👥
- Real-time collaboration
- Template comments
- Change suggestions
- Team templates
- **Timeline**: 4-5 months post-launch

### **Enhancement 7: Advanced Workflows** 🔄
- Approval workflows for templates
- Scheduled PDF generation
- Conditional email triggers
- Multi-step processing
- **Timeline**: 3-4 months post-launch

### **Enhancement 8: Integration Hub** 🔌
- Zapier integration
- Google Drive export
- Dropbox sync
- OneDrive integration
- AWS S3 storage
- **Timeline**: 2-3 months post-launch

### **Enhancement 9: Advanced Typography** ✍️
- Custom font upload
- Google Fonts integration
- Advanced text styling
- Text effects
- **Timeline**: 1-2 months post-launch

### **Enhancement 10: Template Analytics** 📈
- Render time analytics
- Error rate tracking
- User engagement metrics
- A/B testing for templates
- **Timeline**: 2-3 months post-launch

---

## 14. Technical Stack

### **Backend**
- **Framework**: Frappe Framework v14+
- **Language**: Python 3.10+
- **Database**: MariaDB 10.6+
- **Template Engine**: Jinja2
- **PDF Generation**: wkhtmltopdf, WeasyPrint (fallback)
- **Image Processing**: Pillow
- **QR/Barcode**: python-qrcode, python-barcode
- **Background Jobs**: Frappe Queue (Redis)

### **Frontend**
- **Framework**: Frappe UI (Vue.js based)
- **Editor**: Quill / Summernote (HTML editor)
- **Code Editor**: CodeMirror / Monaco Editor
- **UI Components**: Frappe UI components
- **Icons**: Feather Icons, Font Awesome

### **Storage**
- **Files**: Frappe file storage (public/private)
- **Cache**: Redis
- **Backups**: S3-compatible storage (optional)

### **External Services**
- **Email**: Frappe email queue
- **Webhooks**: Frappe webhook system
- **API**: Frappe REST API

---

## 15. Security Considerations

### **Input Validation**
- Sanitize all user HTML input (XSS prevention)
- Validate Python code in computed fields
- Escape special characters in templates
- Limit template size (prevent DoS)

### **Access Control**
- Role-based permissions
- Row-level security (user can only see their templates)
- Permission checks before PDF generation
- Audit all template modifications

### **PDF Security**
- Optional password protection
- PDF permissions (print, copy, modify)
- Watermark for confidential documents
- Digital signature support

### **Data Privacy**
- No external API calls without consent
- Secure file storage
- GDPR compliance
- Data retention policies

### **Code Execution**
- Sandboxed Python execution for computed fields
- Whitelist allowed functions
- Timeout limits for code execution
- Rate limiting on API endpoints

---

## 16. Testing Strategy

### **Unit Tests**
- Test variable parser with edge cases
- Test loop processor with nested loops
- Test formatters (date, currency, etc.)
- Test field resolver with missing fields
- Test PDF generation with various options
- **Target**: >80% code coverage

### **Integration Tests**
- End-to-end template rendering
- PDF generation workflow
- Batch processing
- Email integration
- API endpoints
- **Target**: All major workflows covered

### **Performance Tests**
- Template rendering with 1000+ child rows
- PDF generation for 100-page documents
- Batch generation of 1000 PDFs
- Concurrent user load testing
- **Target**: <3 seconds for standard invoice

### **Security Tests**
- XSS attack prevention
- Code injection prevention
- Permission bypass attempts
- SQL injection (via Frappe ORM, should be safe)
- **Target**: Zero critical vulnerabilities

### **User Acceptance Tests**
- Non-technical user template creation
- Template preview accuracy
- PDF output quality
- Error message clarity
- **Target**: 90%+ user satisfaction

---

## 17. Documentation Plan

### **User Documentation**
1. **Quick Start Guide** - 5-minute tutorial
2. **Template Creation Guide** - Step-by-step
3. **Field Reference** - All available fields
4. **Formatter Reference** - All formatters
5. **Loop Syntax Guide** - Loop examples
6. **Conditional Logic Guide** - Conditions
7. **FAQ** - Common questions
8. **Video Tutorials** - Screen recordings

### **Developer Documentation**
1. **Architecture Overview**
2. **API Reference** - REST, Python, JS
3. **Hook System** - Custom hooks
4. **Plugin Development** - Extend PrintNebula
5. **Contributing Guide** - For contributors
6. **Code Standards** - Coding guidelines

### **Administrator Documentation**
1. **Installation Guide**
2. **Configuration Guide**
3. **Performance Tuning**
4. **Security Best Practices**
5. **Backup & Restore**
6. **Troubleshooting Guide**

---

## 18. Success Metrics

### **Adoption Metrics**
- Number of templates created: Target 100+ in first month
- Number of PDFs generated: Target 1000+ in first month
- Number of active users: Target 50+ in first month

### **Performance Metrics**
- Average render time: <1 second
- Average PDF generation time: <3 seconds
- System uptime: >99.5%

### **Quality Metrics**
- User satisfaction: >90%
- Bug count: <5 critical bugs post-launch
- Code coverage: >80%

### **Engagement Metrics**
- Template reuse rate: >50%
- Template cloning rate: >30%
- Average templates per user: >3

---

## 19. Risk Analysis

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **PDF rendering performance** | High | Medium | Implement caching, background jobs, optimize HTML |
| **Complex loop parsing errors** | High | Medium | Comprehensive testing, error handling, validation |
| **XSS vulnerabilities** | High | Low | Input sanitization, CSP headers, security audit |
| **User adoption** | Medium | Medium | Good UX, documentation, tutorials |
| **Large file handling** | Medium | Medium | File size limits, streaming, compression |
| **Concurrent user load** | Medium | Low | Load testing, horizontal scaling, caching |
| **Browser compatibility** | Low | Low | Test on modern browsers, graceful degradation |

---

## 20. Support & Maintenance

### **Support Channels**
- GitHub Issues
- Community Forum (Frappe Discuss)
- Email Support (for premium users)
- Documentation Wiki

### **Maintenance Plan**
- **Weekly**: Bug fixes, minor improvements
- **Monthly**: Feature releases, performance updates
- **Quarterly**: Major version releases, security audits
- **Yearly**: Architecture review, tech debt cleanup

### **SLA Targets**
- **Critical bugs**: Fix within 24 hours
- **Major bugs**: Fix within 1 week
- **Feature requests**: Review within 2 weeks
- **Security issues**: Fix within 12 hours

---

## 21. Conclusion

**PrintNebula** is designed to be the **ultimate print template solution** for Frappe/ERPNext, combining:

✅ **Ease of use** for non-technical users
✅ **Power and flexibility** for developers
✅ **Performance and scalability** for enterprises
✅ **Extensibility** for custom requirements

With **ALL features in scope** from day one, PrintNebula will provide a comprehensive, production-ready solution that addresses every aspect of custom print format creation and management.

The modular architecture ensures that features can be developed and tested independently, while the comprehensive testing and documentation plan ensures quality and usability.

**This is not just a print template tool—it's a complete document generation platform.** 🌌

---

## Appendix A: Sample Template

### Invoice Template Example

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

{?payment_terms}
<h4>Payment Terms</h4>
<p>{payment_terms}</p>
{/payment_terms}
```

**Footer Section:**
```html
<div style="text-align: center; font-size: 10px;">
    <p>Thank you for your business!</p>
    <p>{terms_and_conditions}</p>
    <p>Page {page} of {total_pages}</p>
</div>
```

**Field Mappings:**
```json
{
    "inv_no": "name",
    "inv_date": "posting_date",
    "cust": "customer_name",
    "total": "grand_total"
}
```

---

## Appendix B: Changelog Template

```
# PrintNebula Changelog

## [v1.0.0] - 2025-12-01
### Added
- Initial release
- Core template editor
- Variable parser
- Loop processor
- PDF generation
- Template library
- Access control
- Batch processing
- Multi-language support
- QR/Barcode generation

### Fixed
- N/A (Initial release)

### Changed
- N/A (Initial release)

### Deprecated
- N/A (Initial release)
```

---

**END OF PRD**

*Version: 2.0*
*Last Updated: 2025-11-18*
*Next Review: 2025-12-18*
