// Copyright (c) 2021, Flege and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pflege Delivery Note', {
	refresh: function(frm) {
		frm.set_query('patient_id',function() {
			return {
				query:'flegeapp.utils.get_patient_query',
			}
		})
	
		if(frm.doc.docstatus===1){
			frm.add_custom_button(__('Create Shipment'), function(){
				if(frm.doc.shipment_created){
					frappe.msgprint('Shipment Already Created for delivery note')
					return false
				}
				frappe.call({
					'method':'flegeapp.utils.create_shipment',
					'args':{
						'service':'standard',
						'delivery_note':cur_frm.doc
					},
					freeze:true,
					callback:function(r){
						if (!r.message){
							frappe.msgprint('Creat Shipment Failed Please Check Error Logs')
							return false;
							
						}else {
							frappe.msgprint('Shipment created successfully')
						}

						cur_frm.refresh_field('shipment_created')
						cur_frm.refresh_fields()
						cur_frm.reload_doc()
						
					}
									
				})
			  },);
			cur_frm.refresh_fields()
			//cur_frm.reload_doc()
			frm.add_custom_button(__('Return Shipment'), function(){
				if(frm.doc.shipment_returned){
					frappe.msgprint('Return Shipment Already Created for delivery note')
					return false
				}
				frappe.call({
					'method':'flegeapp.utils.create_shipment',
					'args':{
						'service':'returns',
						'delivery_note':cur_frm.doc
					},
					freeze:true,
					callback:function(r){
						if (!r.message){
							frappe.msgprint('Create return Failed Please Check Error Logs')
							return false;
							
						}else {
							frappe.msgprint('Return Shipment created successfully')
						}

						cur_frm.refresh_field('shipment_returned')
						cur_frm.refresh_fields()
						cur_frm.reload_doc()
						
					}
									
				})
			},);
			cur_frm.refresh_fields()
		}
		
	},
	patient_id:function(frm){
		console.log('err')
		frm.set_query('patient_id',function() {
			return {
				query:'flegeapp.utils.get_patient_query',
			}
		})
	}
});
