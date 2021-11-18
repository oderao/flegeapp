// Copyright (c) 2021, Flege and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pflege Carebox', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on('Carebox Items',{
	item:function(frm,cdt,cdn){
		//get item size
		var doc = locals[cdt][cdn];
		var size = ''
		frappe.call({
			method:'flegeapp.utils.get_size',
			args:{
				'item':doc.item
			},
			callback:function(r){
				if (r.message){
					
					frappe.model.set_value(cdt,cdn,'size',r.message)
					cur_frm.refresh_field('size')
					cur_frm.refresh_fields()															
				} else {
					frappe.model.set_value(cdt,cdn,'size',"")
					cur_frm.refresh_field('size')
					cur_frm.refresh_fields()	
				}
			}
		})
		
		
	}
});
