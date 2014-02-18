# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, cint
import calendar

def execute(filters=None):
	# key yyyy-mm
	new_customers_in = {}
	repeat_customers_in = {}
	customers = []
	company_condition = ""

	if filters.get("company"):
		company_condition = ' and company=%(company)s'

	for si in frappe.conn.sql("""select posting_date, customer, grand_total from `tabSales Invoice`
		where docstatus=1 and posting_date <= %(to_date)s 
		{company_condition} order by posting_date""".format(company_condition=company_condition), 
		filters, as_dict=1):
				
		key = si.posting_date[:7]
		if not si.customer in customers:
			new_customers_in.setdefault(key, [0, 0.0])
			new_customers_in[key][0] += 1
			new_customers_in[key][1] += si.grand_total
			customers.append(si.customer)
		else:
			repeat_customers_in.setdefault(key, [0, 0.0])
			repeat_customers_in[key][0] += 1
			repeat_customers_in[key][1] += si.grand_total
			
	# time series
	from_year, from_month, temp = filters.get("from_date").split("-")
	to_year, to_month, temp = filters.get("to_date").split("-")
	
	from_year, from_month, to_year, to_month = \
		cint(from_year), cint(from_month), cint(to_year), cint(to_month)
	
	out = []
	for year in xrange(from_year, to_year+1):
		for month in xrange(from_month if year==from_year else 1, (to_month+1) if year==to_year else 13):
			key = "{year}-{month:02d}".format(year=year, month=month)

			new = new_customers_in.get(key, [0,0.0])
			repeat = repeat_customers_in.get(key, [0,0.0])

			out.append([year, calendar.month_name[month], 
				new[0], repeat[0], new[0] + repeat[0],
				new[1], repeat[1], new[1] + repeat[1]])
					
	return [
		"Year", "Month", 
		"New Customers:Int", 
		"Repeat Customers:Int", 
		"Total:Int",
		"New Customer Revenue:Currency:150", 
		"Repeat Customer Revenue:Currency:150", 
		"Total Revenue:Currency:150"
	], out
		
		
		