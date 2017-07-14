// Testing Setup Module in Schools
QUnit.module('setup');

// Testing setting Student Category
QUnit.test('test student category', function(assert){
	assert.expect(1);
	let done = assert.async();
	frappe.run_serially([
		// () => frappe.timeout(2),
		() => {
			return frappe.tests.make('Student Category', [
					{category: 'Reservation'}
			]);
		},
		() => cur_frm.save(),
		() => {
			assert.ok(cur_frm.doc.name=='Reservation');
		},
		() => done()
	]);
});