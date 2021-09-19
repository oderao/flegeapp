# Copyright (c) 2021, Flege and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PflegeSubscription(Document):
	
	def on_submit(self):
		#set next_subscription date
		self.add_date()
		
	def add_date(self):
		if self.subscription_interval == 'Monthly':
			date = frappe.utils.add_to_date(self.subscription_start_date,months=1)
		if self.subscription_interval == 'Yearly':
			date = frappe.utils.add_to_date(self.subscription_start_date,years=1)
		if self.subscription_interval == 'Daily':
			date = frappe.utils.add_to_date(self.subscription_start_date,days=1)
		if self.subscription_interval == 'Quarterly':
			date = frappe.utils.add_to_date(self.subscription_start_date,months=3)
		self.next_subscription_date = date