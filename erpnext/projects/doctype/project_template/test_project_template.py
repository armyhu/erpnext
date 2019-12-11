# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest

class TestProjectTemplate(unittest.TestCase):
	pass

def get_project_template():
	if not frappe.db.exists('Project Template', 'Test Project Template'):
		frappe.get_doc(dict(
			doctype = 'Project Template',
			name = 'Test Project Template',
			tasks = [
				dict(subject='Task 1', description='Task 1 description',
					start=0, duration=3),
				dict(subject='Task 2', description='Task 2 description',
					start=0, duration=2),
				dict(subject='Task 3', description='Task 3 description',
					start=2, duration=4),
				dict(subject='Task 4', description='Task 4 description',
					start=3, duration=2),
			]
		)).insert()

	return frappe.get_doc('Project Template', 'Test Project Template')

def get_project_template_for_skipping_weekends():
	if not frappe.db.exists('Project Template', 'Test Project Template Skip Days'):
		frappe.get_doc(dict(
			doctype = 'Project Template',
			name = 'Test Project Template',
			tasks = [
				dict(subject='Task 1', description='Task 1 description',
					start=0, duration=1),
				dict(subject='Task 2', description='Task 2 description',
					start=1, duration=1),
				dict(subject='Task 3', description='Task 3 description',
					start=1, duration=2),
				dict(subject='Task 4', description='Task 4 description',
					start=3, duration=2),
			],
			skip_weekdays = [
				dict(day="Saturday"),
				dict(day="Sunday"),
			]
		)).insert()

	return frappe.get_doc('Project Template', 'Test Project Template Skip Days')