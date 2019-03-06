// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.views.calendar["Attendance"] = {
	field_map: {
		"start": "date",
		"end": "date",
		"id": "name",
		"docstatus": 1
	},
	options: {
		header: {
			left: 'prev,next today',
			center: 'title',
			right: 'month'
		}
	},
	get_events_method: "erpnext.hr.doctype.attendance.attendance.get_events"
};

frappe.views.calendar["AttendanceGantt"] = {
    field_map: {
        "start": "attendance_date",
        "end": "attendance_date",
        "id": "name",
        "docstatus": 1
    },
    options: {
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month'
        }
    },
    get_events_method: "erpnext.hr.doctype.attendance.attendance.get_events"
};
