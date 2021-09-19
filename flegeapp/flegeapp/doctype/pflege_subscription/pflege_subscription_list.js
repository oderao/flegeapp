frappe.listview_settings['Pflege Subscription'] = {
	add_fields: ["status" ],
	get_indicator: function (doc) {
		if (doc.status === "Active") {
			// Active
			return [__("Active"), "green", "status,=,Active"];
		} else if (doc.status === "Cancelled") {
			// on hold
			return [__("Cancelled"), "red", "status,=,Cancelled"];
		} else if (doc.status === "On Hold") {
			return [__("On Hold"), "orange", "status,=,On Hold"];
		}
	},
}