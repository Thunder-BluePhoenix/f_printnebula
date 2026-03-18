// Copyright (c) 2025, BluePhoenix and contributors
// For license information, please see license.txt

frappe.ui.form.on("PrintNebula Template", {
	refresh(frm) {
		// Add Live Preview button
		frm.add_custom_button(__("Live Preview"), () => {
			let docname = frm.doc.name;
			if (!docname && frm.is_new()) {
				frappe.msgprint(__("Please save the template first before previewing."));
				return;
			}
			
			// Open a dialog or new window with preview
			let d = new frappe.ui.Dialog({
				title: __("Live Preview"),
				size: "extra-large",
				fields: [
					{
						fieldtype: "HTML",
						fieldname: "preview_html"
					}
				]
			});
			
			d.show();
			d.fields_dict.preview_html.$wrapper.html(`<div class="text-center p-5"><span class="text-muted">${__("Loading preview...")}</span></div>`);
			
			frappe.call({
				method: "f_printnebula.api.template_api.preview_template",
				args: {
					template: docname
				},
				callback: function(r) {
					if (r.message && r.message.html) {
						d.fields_dict.preview_html.$wrapper.html(`
							<div style="border: 1px solid #d1d8dd; border-radius: 4px; padding: 20px; max-height: 70vh; overflow-y: auto; background-color: #fff;">
								${r.message.html}
							</div>
						`);
					} else {
						d.fields_dict.preview_html.$wrapper.html(`<div class="text-center p-5 text-danger">${__("Failed to load preview.")}</div>`);
					}
				}
			});
		}, __("Actions"));

		// Add Field Browser button
		frm.add_custom_button(__("Field Browser"), () => {
			if (!frm.doc.doctype_link) {
				frappe.msgprint(__("Please select a Doctype first."));
				return;
			}
			
			let d = new frappe.ui.Dialog({
				title: __("Available Fields for {0}", [frm.doc.doctype_link]),
				fields: [
					{
						fieldtype: "HTML",
						fieldname: "fields_html"
					}
				]
			});
			
			d.show();
			d.fields_dict.fields_html.$wrapper.html(`<div class="text-center p-5"><span class="text-muted">${__("Loading fields...")}</span></div>`);
			
			frappe.model.with_doctype(frm.doc.doctype_link, () => {
				let meta = frappe.get_meta(frm.doc.doctype_link);
				let fields = meta.fields.filter(df => !["Section Break", "Column Break", "Tab Break", "HTML"].includes(df.fieldtype));
				
				let html = `<div class="p-3" style="max-height: 60vh; overflow-y: auto;">
					<table class="table table-bordered table-hover">
						<thead>
							<tr>
								<th>${__("Label")}</th>
								<th>${__("Variable Tag")}</th>
								<th>${__("Type")}</th>
							</tr>
						</thead>
						<tbody>`;
				
				html += `
					<tr>
						<td><strong>Name (ID)</strong></td>
						<td><code>{name}</code></td>
						<td><span class="badge badge-default">Data</span></td>
					</tr>
				`;
				
				fields.forEach(f => {
					html += `
						<tr>
							<td>${f.label || f.fieldname}</td>
							<td><code>{${f.fieldname}}</code></td>
							<td><span class="badge badge-default">${f.fieldtype}</span></td>
						</tr>
					`;
				});
				
				html += `</tbody></table></div>`;
				
				d.fields_dict.fields_html.$wrapper.html(html);
			});
		}, __("Actions"));
	},
	
	doctype_link(frm) {
		// When doctype changes, maybe clear preview
	}
});
