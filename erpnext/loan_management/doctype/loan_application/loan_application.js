// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

{% include 'erpnext/loan_management/loan_common.js' %};

frappe.ui.form.on('Loan Application', {
	refresh: function(frm) {
		frm.trigger("toggle_fields");
		frm.trigger("add_toolbar_buttons");

		frm.set_query('loan_security', 'loan_security_pledges', function(doc, cdt, cdn) {
			return {
				filters: {
					applicant: frm.doc.applicant,
					is_pledged: 0
				}
			};
		});
	},
	repayment_method: function(frm) {
		frm.doc.repayment_amount = frm.doc.repayment_periods = ""
		frm.trigger("toggle_fields")
		frm.trigger("toggle_required")
	},
	toggle_fields: function(frm) {
		frm.toggle_enable("repayment_amount", frm.doc.repayment_method=="Repay Fixed Amount per Period")
		frm.toggle_enable("repayment_periods", frm.doc.repayment_method=="Repay Over Number of Periods")
	},
	toggle_required: function(frm){
		frm.toggle_reqd("repayment_amount", cint(frm.doc.repayment_method=='Repay Fixed Amount per Period'))
		frm.toggle_reqd("repayment_periods", cint(frm.doc.repayment_method=='Repay Over Number of Periods'))
	},
	add_toolbar_buttons: function(frm) {
		if (frm.doc.status == "Approved") {
			frm.add_custom_button(__('Create Loan'), function() {
				frappe.call({
					method: "erpnext.hr.doctype.loan_application.loan_application.make_loan",
					args: {
						"source_name": frm.doc.name
					},
					callback: function(r) {
						if(!r.exc) {
							var doc = frappe.model.sync(r.message);
							frappe.set_route("Form", r.message.doctype, r.message.name);
						}
					}
				});
			}).addClass("btn-primary");
		}
	},

	is_secured_loan(frm) {
		frm.set_df_property('loan_amount', 'read_only', 1);
		frm.set_df_property('loan_amount', 'reqd', 0);
		frm.set_df_property('loan_security_pledges', 'reqd', 1);
	}
});
