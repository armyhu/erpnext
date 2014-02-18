// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

var display_activity_log = function(msg) {
	if(!pscript.ss_html)
		pscript.ss_html = $a(cur_frm.fields_dict['activity_log'].wrapper,'div');
	pscript.ss_html.innerHTML = '<div class="panel"><div class="panel-heading">' + frappe._("Activity Log:") + 
		'</div>' + msg + '</div>';
}

cur_frm.cscript.refresh = function() {
	cur_frm.set_intro(frappe._("Generate, submit & mail multiple salary slips based on selected criteria for employee."));
}

cur_frm.cscript.create_salary_slip = function(doc, cdt, cdn) {
	var callback = function(r, rt) {
		if (r.message)
			display_activity_log(r.message);
	}
	return $c('runserverobj', args={'method': 'create_sal_slip', 'docs': frappe.model.compress(make_doclist (cdt, cdn))}, callback);
}

cur_frm.cscript.submit_salary_slip = function(doc, cdt, cdn) {
	var check = confirm(frappe._("Do you really want to Submit all Salary Slip for month : ") + doc.month + frappe._(" and fiscal year : ") + doc.fiscal_year);
	if(check) {
		var callback = function(r, rt) {
			if (r.message)
				display_activity_log(r.message);
		}
		return $c('runserverobj', args={'method': 'submit_salary_slip', 'docs': frappe.model.compress(make_doclist (cdt, cdn))}, callback);
	}
}

cur_frm.cscript.make_bank_voucher = function(doc, cdt, cdn) {
	if(doc.company && doc.month && doc.from_date && doc.from_date)
		cur_frm.cscript.make_jv(doc, cdt, cdn);
	else
		msgprint(frappe._("Company, Month, From Date & To Date is mandatory"));
}

cur_frm.cscript.make_jv = function(doc, dt, dn) {
	var call_back = function(r, rt) {
		var jv = frappe.model.make_new_doc_and_get_name('Journal Voucher');
		jv = locals['Journal Voucher'][jv];
		jv.voucher_type = 'Bank Voucher';
		jv.user_remark = frappe._('Payment of salary for the month: ') + doc.month + 
			frappe._(' and fiscal year: ') + doc.fiscal_year;
		jv.fiscal_year = doc.fiscal_year;
		jv.company = doc.company;
		jv.posting_date = dateutil.obj_to_str(new Date());

		// credit to bank
		var d1 = frappe.model.add_child(jv, 'Journal Voucher Detail', 'entries');
		d1.account = r.message['default_bank_account'];
		d1.credit = r.message['amount']

		// debit to salary account
		var d2 = frappe.model.add_child(jv, 'Journal Voucher Detail', 'entries');
		d2.debit = r.message['amount']

		loaddoc('Journal Voucher', jv.name);
	}
	return $c_obj(make_doclist(dt, dn), 'get_acc_details', '', call_back);
}
