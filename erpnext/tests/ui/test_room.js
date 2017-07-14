// Testing Setup Module in Schools
QUnit.module('setup');

// Testing setting Room
QUnit.test('test room', function(assert){
	assert.expect(3);
	let done = assert.async();
	frappe.run_serially([
		// () => frappe.timeout(2),
		() => {
			return frappe.tests.make('Room', [
				{room_name: 'Room 1'},
				{room_number: '1'},
				{seating_capacity: '60'},
			]);
		},
		() => {
			assert.ok(cur_frm.doc.room_name == 'Room 1');
			assert.ok(cur_frm.doc.room_number = '1');
			assert.ok(cur_frm.doc.seating_capacity = '60');
		},
		() => done()
	]);
});