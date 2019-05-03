# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

def execute():
	if frappe.db.exists("DocType", "Scheduling Tool"):
		frappe.db.sql("""DELETE FROM `tabDocType` where name = 'Scheduling Tool'""")

	if frappe.db.table_exists("Scheduling Tool"):
		frappe.db.sql("""DROP TABLE IF EXISTS `tabScheduling Tool`""")