# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.model.document import Document

class AssetMovement(Document):
	def validate(self):
		self.validate_cost_center()
		self.validate_employee()
		self.validate_asset()
		
	def validate_asset(self):
		for d in self.assets:
			status, company = frappe.db.get_value("Asset", d.asset, ["status", "company"])
			if self.purpose == "Transfer" and status in ("Draft", "Scrapped", "Sold"):
				frappe.throw(_("{0} asset cannot be transferred").format(status))

			if company != self.company:
				frappe.throw(_("Asset {0} does not belong to company {1}").format(d.asset, self.company))

			if not (d.source_cost_center or d.target_cost_center or d.from_employee or d.to_employee):
				frappe.throw(_("Either Cost Center or employee must be required"))

	def validate_cost_center(self):
		for d in self.assets:
			if self.purpose in ["Transfer", "Issue"]:
				if not d.source_cost_center:
					d.source_cost_center = frappe.db.get_value("Asset", d.asset, "cost_center")

				if not d.source_cost_center:
					frappe.throw(_("Source Cost Center is required for the Asset {0}").format(d.asset))

				if d.source_cost_center:
					current_cost_center = frappe.db.get_value("Asset", d.asset, "cost_center")

					if current_cost_center != d.source_cost_center:
						frappe.throw(
							_("Asset {0} does not belongs to the Cost Center {1}").format(d.asset, d.source_cost_center)
						)

			if self.purpose == "Issue":
				if d.target_cost_center:
					frappe.throw(
						_(
							"Issuing cannot be done to a Cost Center. Please enter employee who has issued Asset {0}"
						).format(d.asset),
						title=_("Incorrect Movement Purpose"),
					)
				if not d.to_employee:
					frappe.throw(_("Employee is required while issuing Asset {0}").format(d.asset))

			if self.purpose == "Transfer":
				# if d.to_employee:
				# 	frappe.throw(
				# 		_(
				# 			"Transferring cannot be done to an Employee. Please enter cost center where Asset {0} has to be transferred"
				# 		).format(d.asset),
				# 		title=_("Incorrect Movement Purpose"),
				# 	)
				if not d.target_cost_center and self.transfer_type == 'Cost Center To Cost Center':
					frappe.throw(_("Target Cost Center is required while transferring Asset {0}").format(d.asset))
				if d.source_cost_center == d.target_cost_center:
					frappe.throw(_("Source and Target Cost Center cannot be same"))

			if self.purpose == "Receipt":
				# only when asset is bought and first entry is made
				if not d.source_cost_center and not (d.target_cost_center or d.to_employee):
					frappe.throw(
						_("Target Cost Center or To Employee is required while receiving Asset {0}").format(d.asset)
					)
				elif d.source_cost_center:
					# when asset is received from an employee
					if d.target_cost_center and not d.from_employee:
						frappe.throw(
							_("From employee is required while receiving Asset {0} to a Target Cost Center").format(
								d.asset
							)
						)
					if d.from_employee and not d.target_cost_center:
						frappe.throw(
							_("Target Cost Center is required while receiving Asset {0} from an employee").format(d.asset)
						)
					if d.to_employee and d.target_cost_center:
						frappe.throw(
							_(
								"Asset {0} cannot be received at a cost center and given to employee in a single movement"
							).format(d.asset)
						)

	def validate_employee(self):
		for d in self.assets:
			if d.from_employee:
				current_custodian = frappe.db.get_value("Asset", d.asset, "custodian")

				if current_custodian != d.from_employee:
					frappe.throw(
						_("Asset {0} does not belongs to the custodian {1}").format(d.asset, d.from_employee)
					)

			if d.to_employee and frappe.db.get_value("Employee", d.to_employee, "company") != self.company:
				frappe.throw(
					_("Employee {0} does not belongs to the company {1}").format(d.to_employee, self.company)
				)

	def on_submit(self):
		self.set_latest_cost_center_in_asset()

	def on_cancel(self):
		self.set_latest_cost_center_in_asset()

	def set_latest_cost_center_in_asset(self):
		current_cost_center, current_employee = "", ""
		cond = "1=1"

		for d in self.assets:
			args = {"asset": d.asset, "company": self.company}

			# latest entry corresponds to current document's Cost Center, employee when transaction date > previous dates
			# In case of cancellation it corresponds to previous latest document's Cost Center, employee
			latest_movement_entry = frappe.db.sql(
				"""
				SELECT asm_item.target_cost_center, asm_item.to_employee,to_employee_name
				FROM `tabAsset Movement Item` asm_item, `tabAsset Movement` asm
				WHERE
					asm_item.parent=asm.name and
					asm_item.asset=%(asset)s and
					asm.company=%(company)s and
					asm.docstatus=1 and {0}
				ORDER BY
					asm.transaction_date desc limit 1
				""".format(
					cond
				),
				args,
			)
			
			if latest_movement_entry:
				current_location = latest_movement_entry[0][0]
				current_employee = latest_movement_entry[0][1]

			frappe.db.set_value("Asset", d.asset, "location", current_location)
			frappe.db.set_value("Asset", d.asset, "custodian", current_employee)
			
	@frappe.whitelist()
	def get_asset_list(self):
		if not self.from_employee:
			frappe.throw("From Employee is Mandatory")
		else:
			if self.to_single:
				if not self.to_employee:
					frappe.throw("To Employee is Mandatory")
				elif self.from_employee == self.to_employee:
					frappe.throw("Select Different Employee")
			asset_list = frappe.db.sql("""
				select name
				from `tabAsset` 
				where custodian = {} 
				and docstatus = 1 
				""".format(self.from_employee),as_dict = 1)
			if asset_list:
				self.set("assets",[])
				for x in asset_list:
					row = self.append("assets",{})
					data = {"asset":x.name, 
							"from_employee":self.from_employee, 
							"to_employee":self.to_employee, 
							"source_cost_center": frappe.db.get_value("Employee",self.from_employee,"cost_center"),
							"target_cost_center": frappe.db.get_value("Employee",self.to_employee,"cost_center")
							}
					row.update(data)


			