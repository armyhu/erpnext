QUnit.module('hr');

QUnit.test("Test: Employee [HR]", function (assert) {
	assert.expect(4);
	let done = assert.async();
	// let today_date = frappe.datetime.nowdate();
	let employee_creation = (name,joining_date,birth_date) => {
		frappe.run_serially([
		// test employee creation
			() => {
				frappe.tests.make('Employee', [
					{ employee_name: name},
					{ salutation: 'Mr'},
					{ company: 'Test Company'},
					{ date_of_joining: joining_date},
					{ date_of_birth: birth_date},
					{ employment_type: 'Test Employment Type'},
					{ holiday_list: 'Test Holiday List'},
					{ branch: 'Test Branch'},
					{ department: 'Test Department'},
					{ designation: 'Test Designation'}
				]);

				/* assert.ok(gender=='Male',
					'Gender Correctly Set');
				assert.ok(date_of_joining==joining_date,
					'Joining date Correctly Set');*/
			},
			() => frappe.timeout(2),
			() => {
				assert.ok(cur_frm.get_field('employee_name').value==name,
					'Name of an Employee is correctly set');
				assert.ok(cur_frm.get_field('gender').value=='Male',
					'Gender of an Employee is correctly set');
			},
		]);
	};
	frappe.run_serially([
		// Creating Timesheet with different tasks
		() => employee_creation('Test Employee 1','2017-04-01','1992-02-02'),
		() => frappe.timeout(6),
		() => employee_creation('Test Employee 2','2017-04-01','1992-02-02'),
		() => frappe.timeout(4),
		() => done()
	]);
});