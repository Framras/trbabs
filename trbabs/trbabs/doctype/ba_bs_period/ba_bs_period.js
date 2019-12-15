// Copyright (c) 2019, Framras AS-Izmir and contributors
// For license information, please see license.txt

frappe.ui.form.on('BA BS Period', {
	// refresh: function(frm) {
	create_babs_forms: function(frm){
        frappe.call({
            method: "trbabs.api.create_babs_forms",
            args:{
                babsmonth: parseInt(frm.doc.month),
                babsyear: parseInt(frm.doc.year),
                babslimit: parseInt(frm.doc.babs_limit)
            },
            callback: function(r){
                frm.set_value("last_created", r.message);
                frm.save();
            }
        })
	}

	// }
});
