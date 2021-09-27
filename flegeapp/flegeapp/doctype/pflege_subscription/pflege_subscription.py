# Copyright (c) 2021, Flege and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PflegeSubscription(Document):
	

	def on_update_after_submit(self):
		self.reorder_delivery_note_table()

	def before_submit(self):
		#set next_subscription date
		self.add_date()
		
	def add_date(self):
		date_to_update = self.subscription_start_date
		if self.next_subscription_date:
			date_to_update = self.next_subscription_date
		if self.subscription_interval == 'Monthly':
			date = frappe.utils.add_to_date(date_to_update,months=1)
		if self.subscription_interval == 'Yearly':
			date = frappe.utils.add_to_date(date_to_update,years=1)
		if self.subscription_interval == 'Daily':
			date = frappe.utils.add_to_date(date_to_update,days=1)
		if self.subscription_interval == 'Quarterly':
			date = frappe.utils.add_to_date(date_to_update,months=3)
		self.next_subscription_date = date
	
	def reorder_delivery_note_table(self):
		from operator import attrgetter
		count = 0
		self.delivery.sort(key = attrgetter('delivery_note'),reverse=True)
		for delivery in self.delivery:
			count += 1
			delivery.idx = count
