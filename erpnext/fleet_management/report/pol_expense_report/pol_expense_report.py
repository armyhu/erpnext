# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []
	data = get_data(filters)
	if not data:
		return columns, data
	columns = get_columns(data)
	return columns, data

def get_columns(data):
	return [
		("POL Expense") + ":Link/POL Expense:120",
		("Equipment") + ":Link/Equipment:120",
		("Fuelbook Branch") + ":Data:120",
		("Cost Center") + ":Link/Cost Center:120",
		("Entry Date") + ":Date:100",
		("Fuelbook") + ":Data:120",
		("Supplier") + ":Data:120",
		("Amount")+ ":Data:100",
		("Adjusted Amount") + ":Date:120",
		("Balance Amount") + ":Data:100",
		("Credit Account") + ":Data:120"
	]

def get_data(filters):
	conditions = get_conditions(filters)
	query = frappe.db.sql("""select distinct 
					p.name, 
					p.equipment, 
					p.fuelbook_branch, 
					p.cost_center, 
					p.entry_date,
					p.fuel_book, 
					p.party, 
					p.amount, 
					p.adjusted_amount, 
					p.balance_amount, 
					p.credit_account
				from 
					`tabPOL Expense` p 
				where docstatus = 1 {} """.format(conditions))
	return query

def get_conditions(filters):
	conditions = ""
	if filters.get("branch"): 
		conditions += " and p.fuelbook_branch = '{}'".format(filters.get("branch"))
	
	if filters.get("cost_center"):
		conditions += "and p.cost_center = '{}'".format(filters.get("cost_center"))

	if filters.get("from_date") and filters.get("to_date"):
		conditions += "and p.entry_date between '{0}' and '{1}'".format(filters.get("from_date"),filters.get("to_date"))

	if filters.get("equipment"):
		conditions += "and p.equipment = '{}'".format(filters.get("equipment"))
		
	return conditions