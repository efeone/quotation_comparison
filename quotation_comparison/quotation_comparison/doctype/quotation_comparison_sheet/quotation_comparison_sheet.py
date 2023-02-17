# Copyright (c) 2023, efeone and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import *
from frappe.model.mapper import get_mapped_doc
from frappe.model.document import Document

class QuotationComparisonSheet(Document):
	def validate(self):
		self.prepared_by = frappe.session.user
		grand_total = 0
		if self.items:
			for item in self.items:
				grand_total += item.amount
		self.grand_total = grand_total

	def on_submit(self):
		if not self.items:
			frappe.throw("To submit the comparison sheet - Please fill the result to the items table")

	@frappe.whitelist()
	def order_items_by_filter(self, type):
		if self.quotation_items:
			if type == 'best_price_same_supplier':
				best_price_same_supplier(self)
			if type == 'best_price_many_supplier':
				best_price_many_supplier(self)

	@frappe.whitelist()
	def create_purchase_orders(self):
		'''Method to Create Purchase Order against filtered quotations'''
		if self.items:
			suppliers = []
			for item in self.items:
				if item.supplier not in suppliers:
					suppliers.append(item.supplier)
			if suppliers:
				for supplier in suppliers:
					po_doc = frappe.new_doc('Purchase Order')
					po_doc.supplier = supplier
					for item in self.items:
						if supplier == item.supplier:
							po_doc.transaction_date = item.date
							po_item = po_doc.append('items')
							po_item.item_code = item.item_code
							po_item.qty = item.qty
							po_item.rate = item.rate
							po_item.uom = item.uom
							po_item.amount = item.amount
							po_item.supplier_quotation = item.quotation
							po_item.warehouse = item.warehouse
							po_item.schedule_date = item.date
							po_item.expected_delivery_date = item.delivery_date
					po_doc.save()
					po_link = get_url_to_form('Purchase Order', po_doc.name)
					frappe.msgprint(_("Purchase Order Created.<a href='{0}'>Click here</a>".format(po_link)), alert=True, indicator='green')
			frappe.db.set_value(self.doctype, self.name, 'po_created', 1)
			frappe.db.commit()

@frappe.whitelist()
def get_quotation_against_rfq(rfq):
	'''Mthod to make a list of quotations against rfq'''
	quotation_list = []
	query = '''
		SELECT DISTINCT
			sq.name
		FROM
			`tabSupplier Quotation` as sq,
			`tabSupplier Quotation Item` as sqi
		WHERE
			sqi.request_for_quotation = %(request_for_quotation)s
			AND sqi.parent = sq.name
	'''
	quotations = frappe.db.sql(query.format(), { 'request_for_quotation':rfq }, as_dict = True)
	for quotation in quotations:
		quotation_list.append(frappe.get_doc('Supplier Quotation', quotation.name))
	return quotation_list

@frappe.whitelist()
def best_price_same_supplier(self):
	'''Method to filter items with best price from Single Supplier'''
	quotation_id = 0
	if self.quotations:
		lowest_price = self.quotations[0].grand_total
		for quotation in self.quotations:
			if lowest_price >= quotation.grand_total:
				lowest_price = quotation.grand_total
				quotation_id = quotation.quotation
	if quotation_id:
		quotation_doc = frappe.get_doc('Supplier Quotation', quotation_id)
		if quotation_doc.items:
			self.compare_quotation_by = 'Whole Quotation'
			self.items = []
			for item in quotation_doc.items:
				best_price_item = self.append('items')
				best_price_item.quotation = quotation_doc.name
				best_price_item.supplier = quotation_doc.supplier
				best_price_item.date = quotation_doc.transaction_date
				best_price_item.item_code = item.item_code
				best_price_item.delivery_date = item.expected_delivery_date
				best_price_item.warehouse = item.warehouse
				best_price_item.qty = item.qty
				best_price_item.uom = item.uom
				best_price_item.rate = item.rate
				best_price_item.amount = item.amount
			self.save()
			frappe.msgprint(_('Ordered based on Best Price from one Suppliers'), alert=True, indicator='green')

@frappe.whitelist()
def best_price_many_supplier(self):
	'''Method to filter items with best price from Multiple Supplier'''
	all_items=[]
	lowest_price_items = []
	if self.quotation_items:
		for item in self.quotation_items:
			if item.item_code not in all_items:
				all_items.append(item.item_code)
	if all_items:
		for item in all_items:
			lowest_price_items.append(find_item_details_with_lowest_price(self, item))
	if lowest_price_items:
		self.compare_quotation_by = 'Item Wise'
		self.items = []
		for item in lowest_price_items:
			best_price_item = self.append('items')
			best_price_item.quotation = item.quotation
			best_price_item.supplier = item.supplier
			best_price_item.date = ('Supplier Quotation', item.quotation, 'transaction_date')
			best_price_item.item_code = item.item_code
			best_price_item.delivery_date = item.delivery_date
			best_price_item.warehouse = item.warehouse
			best_price_item.qty = item.qty
			best_price_item.uom = item.uom
			best_price_item.rate = item.rate
			best_price_item.amount = item.amount
		self.save()
		frappe.msgprint(_('Ordered based on Best Price from many Suppliers'), alert=True, indicator='green')

@frappe.whitelist()
def find_item_details_with_lowest_price(self, item_code):
	'''Method to get item_detaills of a particular item with minimal rate from all Suppliers'''
	item_price = 0
	item_detaills = []
	if self.quotation_items and item_code:
		for item in self.quotation_items:
			if item.item_code == item_code:
				if not item_price:
					item_price = item.rate
					item_detaills = item
				elif item.rate < item_price:
					item_price = item.rate
					item_detaills = item
	return item_detaills.as_dict()

@frappe.whitelist()
def create_comparison_sheet(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.request_for_quotation = source.name
	doclist = get_mapped_doc("Request for Quotation", source_name,{
		"Request for Quotation": {
			"doctype": "Quotation Comparison Sheet"
		},
	}, target_doc, set_missing_values)
	doclist.save()
	return doclist
