// Copyright (c) 2019, Framras AS-Izmir and contributors
// For license information, please see license.txt

frappe.ui.form.on('BA BS Form', {
	// refresh: function(frm) {
	send_form: function(frm){
        frm.set_value("form_sent_date", new Date().toISOString().slice(0, 10));
        frm.save();
        }
	// }
});
