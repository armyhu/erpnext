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
		("POL Receive") + ":Link/POL Receive:120",
		("Equipment") + ":Link/Equipment:120",
		("Equipment Type") + ":Data:120",
		("Fuelbook Branch") + ":Data:120",
		("Fuelbook") + ":Data:120",
		("Supplier") + ":Data:120",
		("Fuel Type Item Code")+ ":Data:100",
		("Item Name")+ ":Data:130",
		("Posting Date") + ":Date:120",
		("Quantity") + ":Data:100",
		("Rate Per Unit") + ":Data:100",
		("Amount") + ":Currency:120",
		("Mileage") + ":Data:100"
	]

def get_data(filters):
	conditions = get_conditions(filters)
	query = frappe.db.sql("""select distinct 
					p.name, 
					p.equipment, 
					p.equipment_type, 
					p.fuelbook_branch, 
					p.fuelbook, 
					p.supplier, 
					p.pol_type, 
					p.item_name, 
					p.posting_date, 
					p.qty,  
					p.rate, 
					ifnull(p.total_amount,0),
					p.mileage
				from 
					`tabPOL Receive` p 
				where docstatus = 1 {} """.format(conditions))
	return query

def get_conditions(filters):
	conditions = ""
	if filters.get("branch"): 
		conditions += " and p.branch = '{}'".format(filters.get("branch"))

	if filters.get("from_date") and filters.get("to_date"):
		conditions += "and p.posting_date between '{0}' and '{1}'".format(filters.get("from_date"),filters.get("to_date"))
	
	if filters.get("item_name"):
		conditions += "and p.item_name = '{}'".format(filters.get("item_name"))

	if filters.get("equipment"):
		conditions += "and p.equipment = '{}'".format(filters.get("equipment"))
		
	return conditions