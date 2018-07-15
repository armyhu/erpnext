# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import time_diff_in_hours, get_datetime
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document

class JobCard(Document):
	def get_required_items(self):
		if not self.get('work_order') and not self.transfer_material_against_job_card:
			return

		doc = frappe.get_doc('Work Order', self.get('work_order'))
		for d in doc.required_items:
			if not d.operation:
				frappe.throw(_("Row {0} : Operation is required against the raw material item {1}")
					.format(d.idx, d.item_code))

			if self.get('operation') == d.operation:
				child = self.append('items', d)
				child.uom = frappe.db.get_value("Item", d.item_code, 'stock_uom')

	def on_submit(self):
		self.update_work_order()

	def update_work_order(self):
		if not self.work_order:
			return

		wo = frappe.get_doc('Work Order', self.work_order)

		for data in wo.operations:
			if data.name == self.operation_id:
				data.completed_qty = self.for_quantity
				data.actual_operation_time = time_diff_in_hours(self.actual_end_date, self.actual_start_date) * 60
				data.actual_start_time = get_datetime(self.actual_start_date)
				data.actual_end_time = get_datetime(self.actual_end_date)

		wo.flags.ignore_validate_update_after_submit = True
		wo.update_operation_status()
		wo.calculate_operating_cost()
		wo.set_actual_dates()
		wo.save()

def update_job_card_reference(name, fieldname, value):
	frappe.db.set_value('Job Card', name, fieldname, value)

@frappe.whitelist()
def make_material_request(source_name, target_doc=None):
	def update_item(obj, target, source_parent):
		target.warehouse = source_parent.wip_warehouse

	def set_missing_values(source, target):
		target.material_request_type = "Material Transfer"

	doclist = get_mapped_doc("Job Card", source_name, {
		"Job Card": {
			"doctype": "Material Request",
			"validation": {
				"docstatus": ["=", 1]
			},
			"field_map": {
				"name": "job_card",
			},
		},
		"Job Card Item": {
			"doctype": "Material Request Item",
			"field_map": {
				"required_qty": "qty",
				"uom": "stock_uom"
			},
			"postprocess": update_item,
		}
	}, target_doc, set_missing_values)

	return doclist

@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
	def update_item(obj, target, source_parent):
		target.t_warehouse = source_parent.wip_warehouse

	def set_missing_values(source, target):
		target.purpose = "Material Transfer for Manufacture"
		target.from_bom = 1
		target.calculate_rate_and_amount()
		target.set_missing_values()

	doclist = get_mapped_doc("Job Card", source_name, {
		"Job Card": {
			"doctype": "Stock Entry",
			"validation": {
				"docstatus": ["=", 1]
			},
			"field_map": {
				"name": "job_card",
				"for_quantity": "fg_completed_qty"
			},
		},
		"Job Card Item": {
			"doctype": "Stock Entry Detail",
			"field_map": {
				"source_warehouse": "s_warehouse",
				"required_qty": "qty",
				"uom": "stock_uom"
			},
			"postprocess": update_item,
		}
	}, target_doc, set_missing_values)

	return doclist
