// Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Item-wise Sales Register"] = frappe.query_reports["Sales Register"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": frappe._("From Date"),
			"fieldtype": "Date",
			"default": frappe.defaults.get_default("year_start_date"),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": frappe._("To Date"),
			"fieldtype": "Date",
			"default": get_today()
		},
		{
			"fieldname":"account",
			"label": frappe._("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"get_query": function() {
				var company = frappe.query_report.filters_by_name.company.get_value();
				return {
					"query": "accounts.utils.get_account_list", 
					"filters": {
						"is_pl_account": "No",
						"debit_or_credit": "Debit",
						"company": company,
						"master_type": "Customer"
					}
				}
			}
		},
		{
			"fieldname":"company",
			"label": frappe._("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_default("company")
		}
	]
}