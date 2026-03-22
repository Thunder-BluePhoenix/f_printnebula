frappe.pages['printnebula_batch'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'PrintNebula Batch Generator',
		single_column: true
	});

	page.set_secondary_action('Refresh', () => render_ui(page), 'refresh');

	render_ui(page);
}

function render_ui(page) {
	$(page.body).empty();

	let container = $(`
		<div class="printnebula-batch-app" style="margin: 20px;">
			<div class="row">
				<div class="col-md-4">
					<div class="form-group">
						<label>1. Select Doctype</label>
						<select id="pn-doctype-select" class="form-control"></select>
					</div>
				</div>
				<div class="col-md-4">
					<div class="form-group">
						<label>2. Select Template</label>
						<select id="pn-template-select" class="form-control" disabled></select>
					</div>
				</div>
				<div class="col-md-4">
					<div class="form-group">
						<label>&nbsp;</label>
						<br>
						<button id="pn-fetch-docs" class="btn btn-primary" disabled>Fetch Documents</button>
					</div>
				</div>
			</div>
			
			<div id="pn-progress-container" style="display: none; margin-top: 20px;">
				<h5>Generation Progress</h5>
				<div class="progress">
				  <div id="pn-progress-bar" class="progress-bar progress-bar-striped active" role="progressbar" style="width: 0%">
				    0%
				  </div>
				</div>
				<p id="pn-progress-text" class="text-muted mt-2">Initializing...</p>
			</div>

			<div id="pn-docs-container" style="margin-top: 30px;">
				<table class="table table-bordered">
					<thead>
						<tr>
							<th style="width: 50px;"><input type="checkbox" id="pn-select-all"></th>
							<th>Document Name</th>
							<th>Status</th>
						</tr>
					</thead>
					<tbody id="pn-docs-body">
						<tr><td colspan="3" class="text-center text-muted">Select a Doctype and click Fetch</td></tr>
					</tbody>
				</table>
			</div>
			
			<div style="margin-top: 20px;">
				<button id="pn-generate-batch" class="btn btn-success" disabled>Generate PDFs</button>
			</div>
		</div>
	`).appendTo(page.body);

	// Load Doctypes with templates
	frappe.call({
		method: 'frappe.client.get_list',
		args: {
			doctype: 'PrintNebula Template',
			fields: ['doctype_link'],
			limit: 0
		},
		callback: function(r) {
			if (r.message) {
				let doctypes = [...new Set(r.message.map(d => d.doctype_link))];
				let html = '<option value="">-- Select Doctype --</option>';
				doctypes.forEach(d => { html += `<option value="${d}">${d}</option>`; });
				$('#pn-doctype-select').html(html);
			}
		}
	});

	$('#pn-doctype-select').on('change', function() {
		let doctype = $(this).val();
		if (!doctype) {
			$('#pn-template-select').prop('disabled', true).html('');
			$('#pn-fetch-docs').prop('disabled', true);
			return;
		}

		frappe.call({
			method: 'f_printnebula.f_printnebula.api.template_api.get_templates_for_doctype',
			args: { doctype: doctype },
			callback: function(r) {
				if (r.message) {
					let html = '<option value="">-- Select Template --</option>';
					r.message.forEach(t => { html += `<option value="${t.name}">${t.template_name}</option>`; });
					$('#pn-template-select').html(html).prop('disabled', false);
					$('#pn-fetch-docs').prop('disabled', false);
				}
			}
		});
	});

	$('#pn-fetch-docs').on('click', function() {
		let doctype = $('#pn-doctype-select').val();
		if (!doctype) return;
		
		$('#pn-docs-body').html('<tr><td colspan="3" class="text-center">Loading...</td></tr>');
		
		frappe.call({
			method: 'frappe.client.get_list',
			args: {
				doctype: doctype,
				fields: ['name'],
				limit: 50,
				order_by: 'creation desc'
			},
			callback: function(r) {
				if (r.message && r.message.length > 0) {
					let html = '';
					r.message.forEach(d => {
						html += `
							<tr>
								<td><input type="checkbox" class="pn-doc-row" value="${d.name}"></td>
								<td>${d.name}</td>
								<td class="pn-status">Pending</td>
							</tr>
						`;
					});
					$('#pn-docs-body').html(html);
					$('#pn-generate-batch').prop('disabled', false);
				} else {
					$('#pn-docs-body').html('<tr><td colspan="3" class="text-center">No documents found.</td></tr>');
					$('#pn-generate-batch').prop('disabled', true);
				}
			}
		});
	});

	$('#pn-select-all').on('change', function() {
		$('.pn-doc-row').prop('checked', $(this).prop('checked'));
	});

	$('#pn-generate-batch').on('click', function() {
		let selected = [];
		$('.pn-doc-row:checked').each(function() { selected.push($(this).val()); });
		
		let template = $('#pn-template-select').val();
		let doctype = $('#pn-doctype-select').val();

		if (selected.length === 0) {
			frappe.msgprint("Please select at least one document.");
			return;
		}
		if (!template) {
			frappe.msgprint("Please select a template.");
			return;
		}

		$('#pn-progress-container').show();
		$('#pn-generate-batch').prop('disabled', true);
		
		frappe.call({
			method: 'f_printnebula.f_printnebula.api.batch_api.generate_batch',
			args: {
				template_name: template,
				doctype: doctype,
				docnames: JSON.stringify(selected)
			},
			callback: function(r) {
				if (r.message && r.message.job_id) {
					monitor_job(r.message.job_id);
				} else {
					frappe.msgprint("Failed to start batch job.");
					$('#pn-generate-batch').prop('disabled', false);
				}
			}
		});
	});
	
	function monitor_job(job_id) {
		let interval = setInterval(() => {
			frappe.call({
				method: 'f_printnebula.f_printnebula.api.batch_api.get_job_status',
				args: { job_id: job_id },
				callback: function(r) {
					if (r.message) {
						let progress = r.message.progress;
						$('#pn-progress-bar').css('width', progress + '%').text(Math.round(progress) + '%');
						$('#pn-progress-text').text(r.message.status_message);
						
						if (r.message.status === 'Completed') {
							clearInterval(interval);
							frappe.msgprint(`Batch Generation Complete. <a href="${r.message.file_url}" target="_blank">Download ZIP</a>`);
							$('#pn-generate-batch').prop('disabled', false);
						} else if (r.message.status === 'Failed') {
							clearInterval(interval);
							frappe.msgprint("Batch Generation Failed.");
							$('#pn-generate-batch').prop('disabled', false);
						}
					}
				}
			});
		}, 3000);
	}
}
