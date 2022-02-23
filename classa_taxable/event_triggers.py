from __future__ import unicode_literals
import frappe
from frappe import auth
import datetime
import json, ast


################ Quotation

@frappe.whitelist()
def quot_onload(doc, method=None):
    pass
@frappe.whitelist()
def quot_before_validate(doc, method=None):

    ## Make Customer Address 2 Field Mandatory If Customer Group Is Chain
    parent_group = frappe.db.get_value("Customer Group", doc.customer_group, "parent_customer_group")
    if (doc.customer_group == "مجموعة السلاسل" or parent_group == "مجموعة السلاسل") and not doc.customer_address_2:
        frappe.throw("Please Select The Customer's Address")
    if (doc.customer_group == "مجموعة السلاسل" or parent_group == "مجموعة السلاسل"):
        doc.customer_address = doc.customer_address_2
    if (doc.customer_group == "مجموعة التجزئة" or parent_group == "مجموعة التجزئة"):
        doc.customer_address_2 = doc.customer_address

    ## Fetch Branch From Territory
    doc.branch = frappe.db.get_value("Territory", doc.territory, "branch")

    ## Fetch Department From Session User
    user = frappe.session.user
    doc.department = frappe.db.get_value("Employee", {'user_id': user}, "department")

    ## Fetch Cost Center From Customer Group
    doc.cost_center = frappe.db.get_value("Customer Group", doc.customer_group, "cost_center")

    ## Fetch Accounting Dimensions In Taxes Table
    for y in doc.taxes:
        y.territory = doc.territory
        y.branch = doc.branch
        y.department = doc.department
        y.cost_center = doc.cost_center

    ## Fetch Price List Rate In Items Table
    for x in doc.items:
        x.price_list_rate = frappe.db.get_value("Item Price", {'price_list': doc.selling_price_list, 'item_code': x.item_code}, "price_list_rate")



@frappe.whitelist()
def quot_validate(doc, method=None):
    pass


@frappe.whitelist()
def quot_on_submit(doc, method=None):
    pass
       

@frappe.whitelist()
def quot_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def quot_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def quot_before_save(doc, method=None):
    pass
@frappe.whitelist()
def quot_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def quot_on_update(doc, method=None):
    pass


################ Sales Order


@frappe.whitelist()
def so_onload(doc, method=None):
    pass
@frappe.whitelist()
def so_before_validate(doc, method=None):
    pass

@frappe.whitelist()
def so_validate(doc, method=None):
    pass

@frappe.whitelist()
def so_on_submit(doc, method=None):
    ## Auto Create Draft Stock Entry On Submit
    new_doc = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": "Material Transfer",
        "purpose": "Material Transfer",
        "posting_date": doc.transaction_date,
        "sales_order": doc.name,
        "customer": doc.customer,
        "customer_address": doc.customer_address,
        "from_warehouse": doc.set_warehouse,
        "to_warehouse": doc.vehicle_warehouse,
        "vehicle": doc.vehicle,
        "territory": doc.territory,

    })
    so_items = frappe.db.sql(""" select a.idx, a.name, a.item_code, a.item_name, a.description, a.qty, a.stock_qty, a.uom, a.stock_uom, a.conversion_factor
                                                           from `tabSales Order Item` a join `tabSales Order` b
                                                           on a.parent = b.name
                                                           where b.name = '{name}'
                                                       """.format(name=doc.name), as_dict=1)

    for c in so_items:
        items = new_doc.append("items", {})
        items.idx = c.idx
        items.item_code = c.item_code
        items.item_name = c.item_name
        items.description = c.description
        items.t_warehouse = doc.vehicle_warehouse
        items.qty = c.qty
        items.transfer_qty = c.transfer_qty
        items.uom = c.uom
        items.stock_uom = c.stock_uom
        items.conversion_factor = c.conversion_factor
        items.so_item = c.name
        items.so = doc.name

    new_doc.insert()
    frappe.msgprint(new_doc.name + " تم إنشاء حركة مخزنية بحالة مسودة رقم ")


@frappe.whitelist()
def so_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def so_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def so_before_save(doc, method=None):
    pass
@frappe.whitelist()
def so_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def so_on_update(doc, method=None):
    pass


################ Delivery Note

@frappe.whitelist()
def dn_onload(doc, method=None):
    pass
@frappe.whitelist()
def dn_before_validate(doc, method=None):
    ## Fetch Driver Name and Transporter Name
    doc.driver_name = frappe.db.get_value("Driver", doc.driver, "full_name")
    doc.transporter_name = frappe.db.get_value("Supplier", doc.transporter, "name")

    ## Fetch Vehicle From Target Warehouse
    doc.vehicle = frappe.db.get_value("Warehouse", doc.set_warehouse, "vehicle")

    ## Fetch Branch From Territory
    doc.branch = frappe.db.get_value("Territory", doc.territory, "branch")

    ## Fetch Department From Session User
    user = frappe.session.user
    doc.department = frappe.db.get_value("Employee", {'user_id': user}, "department")

    ## Fetch Cost Center From Customer Group
    customer_group = frappe.db.get_value("Customer", doc.customer, "customer_group")
    doc.cost_center = frappe.db.get_value("Customer Group", customer_group, "cost_center")

    ## Fetch Accounting Dimensions In Items Table
    for x in doc.items:
        x.vehicle = doc.vehicle
        x.territory = doc.territory
        x.branch = doc.branch
        x.department = doc.department
        x.cost_center = doc.cost_center

    ## Fetch Accounting Dimensions In Taxes Table
    for y in doc.taxes:
        y.vehicle = doc.vehicle
        y.territory = doc.territory
        y.branch = doc.branch
        y.department = doc.department
        y.cost_center = doc.cost_center


@frappe.whitelist()
def dn_validate(doc, method=None):
    # fetch_tax_type_from_customer
    default_tax_type = frappe.db.get_value("Customer", doc.customer, "tax_type")
    if not doc.tax_type:
        doc.tax_type = default_tax_type

    else:
        pass
@frappe.whitelist()
def dn_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def dn_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def dn_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def dn_before_save(doc, method=None):
    pass
@frappe.whitelist()
def dn_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def dn_on_update(doc, method=None):
    pass

################ Sales Invoice


@frappe.whitelist()
def siv_onload(doc, method=None):
    pass
@frappe.whitelist()
def siv_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def siv_validate(doc, method=None):
    pass
@frappe.whitelist()
def siv_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def siv_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def siv_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def siv_before_save(doc, method=None):
    pass
@frappe.whitelist()
def siv_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def siv_on_update(doc, method=None):
    pass


################ Payment Entry

@frappe.whitelist()
def pe_onload(doc, method=None):
    pass
@frappe.whitelist()
def pe_before_validate(doc, method=None):
    ## Fetch Sales Persons
    if doc.party_type == "Customer":
        user = frappe.session.user
        employee = frappe.db.get_value("Employee", {'user_id': user}, "name")
        customer_group = frappe.db.get_value("Customer", doc.party, "customer_group")
        doc.sales_person = frappe.db.get_value("Sales Person", {'employee': employee}, "name")
        doc.sales_supervisor = frappe.db.get_value("Sales Person", doc.sales_person, "parent_sales_person")
        doc.territory_manager = frappe.db.get_value("Customer", doc.party, "sales_person")
        doc.sales_manager = frappe.db.get_value("Customer Group", customer_group, "sales_person")

    ## Fetch Territory From Customer
    doc.territory = frappe.db.get_value("Customer", doc.party, "territory")

    ## Fetch Branch From Territory
    doc.branch = frappe.db.get_value("Territory", doc.territory, "branch")

    ## Fetch Department From Session User
    user = frappe.session.user
    doc.department = frappe.db.get_value("Employee", {'user_id': user}, "department")

    ## Fetch Cost Center From Customer Group
    customer_group = frappe.db.get_value("Customer", doc.party, "customer_group")
    doc.cost_center = frappe.db.get_value("Customer Group", customer_group, "cost_center")

    ## Fetch Accounting Dimensions In Taxes Table
    for x in doc.taxes:
        x.cost_center = doc.cost_center

    ## Fetch Accounting Dimensions In Taxes Table
    for y in doc.deductions:
        y.territory = doc.territory
        y.branch = doc.branch
        y.department = doc.department
        y.cost_center = doc.cost_center

@frappe.whitelist()
def pe_validate(doc, method=None):
    customer_tax_type = frappe.db.get_value("Customer", doc.party, "tax_type")
    supplier_tax_type = frappe.db.get_value("Supplier", doc.party, "tax_type")
    if not doc.tax_type and doc.party_type == "Customer":
        doc.tax_type = customer_tax_type

    if not doc.tax_type and doc.party_type == "Supplier":
        doc.tax_type = supplier_tax_type

    else:
        pass


@frappe.whitelist()
def pe_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def pe_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def pe_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def pe_before_save(doc, method=None):
    pass
@frappe.whitelist()
def pe_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def pe_on_update(doc, method=None):
    pass

################ Material Request

@frappe.whitelist()
def mr_onload(doc, method=None):
    pass
@frappe.whitelist()
def mr_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def mr_validate(doc, method=None):
    pass
@frappe.whitelist()
def mr_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def mr_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def mr_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def mr_before_save(doc, method=None):
    pass
@frappe.whitelist()
def mr_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def mr_on_update(doc, method=None):
    pass

################ Purchase Order

@frappe.whitelist()
def po_onload(doc, method=None):
    pass
@frappe.whitelist()
def po_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def po_validate(doc, method=None):
    pass
@frappe.whitelist()
def po_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def po_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def po_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def po_before_save(doc, method=None):
    pass
@frappe.whitelist()
def po_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def po_on_update(doc, method=None):
    pass

################ Purchase Receipt

@frappe.whitelist()
def pr_onload(doc, method=None):
    pass
@frappe.whitelist()
def pr_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def pr_validate(doc, method=None):
    ##fetch_tax_type_from_Supplier
    default_tax_type = frappe.db.get_value("Supplier", doc.supplier, "tax_type")
    if not doc.tax_type:
        doc.tax_type = default_tax_type

    else:
        pass
@frappe.whitelist()
def pr_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def pr_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def pr_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def pr_before_save(doc, method=None):
    pass
@frappe.whitelist()
def pr_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def pr_on_update(doc, method=None):
    pass


################ Purchase Invoice

@frappe.whitelist()
def piv_onload(doc, method=None):
    pass
@frappe.whitelist()
def piv_before_validate(doc, method=None):
    ##Calculate Item Rate If Supplier Tax Type Is Taxable
    if doc.tax_type == "Commercial":
        doc.set("taxes", [])
        for d in doc.items:
            item_tax_rate = frappe.db.get_value("Item Tax Template Detail", {'parent': d.item_tax_template}, "tax_rate")
            if item_tax_rate > 0 and d.rate <= d.price_list_rate:
                new_rate = d.rate + (item_tax_rate * d.rate / 100)
                d.rate = new_rate

            else:
                pass

    else:
        pass

@frappe.whitelist()
def piv_validate(doc, method=None):
    ##fetch_tax_type_from_Supplier
    default_tax_type = frappe.db.get_value("Supplier", doc.supplier, "tax_type")
    if not doc.tax_type:
        doc.tax_type = default_tax_type

    else:
        pass

@frappe.whitelist()
def piv_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def piv_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def piv_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def piv_before_save(doc, method=None):
    pass

@frappe.whitelist()
def piv_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def piv_on_update(doc, method=None):
    pass

################ Employee Advance

@frappe.whitelist()
def emad_onload(doc, method=None):
    pass
@frappe.whitelist()
def emad_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def emad_validate(doc, method=None):
    pass
@frappe.whitelist()
def emad_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def emad_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def emad_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def emad_before_save(doc, method=None):
    pass
@frappe.whitelist()
def emad_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def emad_on_update(doc, method=None):
    pass

################ Expense Claim

@frappe.whitelist()
def excl_onload(doc, method=None):
    pass
@frappe.whitelist()
def excl_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def excl_validate(doc, method=None):
    pass
@frappe.whitelist()
def excl_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def excl_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def excl_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def excl_before_save(doc, method=None):
    pass
@frappe.whitelist()
def excl_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def excl_on_update(doc, method=None):
    pass

################ Stock Entry

@frappe.whitelist()
def ste_onload(doc, method=None):
    pass
@frappe.whitelist()
def ste_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def ste_validate(doc, method=None):
    pass
@frappe.whitelist()
def ste_on_submit(doc, method=None):
    ## Auto Create Draft Sales Invoice On Submit
    if doc.sales_order:
        so = frappe.get_doc('Sales Order', doc.sales_order)
        new_doc = frappe.get_doc({
            "doctype": "Sales Invoice",
            "update_stock": 1,
            "customer": so.customer,
            "customer_group": so.customer_group,
            "territory": so.territory,
            "sales_order": so.name,
            "posting_date": so.delivery_date,
            "tax_type": so.tax_type,
            "po_no": so.po_no,
            "po_date": so.po_date,
            "customer_address": so.customer_address,
            "shipping_address_name": so.shipping_address_name,
            "dispatch_address_name": so.dispatch_address_name,
            "company_address": so.company_address,
            "contact_person": so.contact_person,
            "tax_id": so.tax_id,
            "currency": so.currency,
            "conversion_rate": so.conversion_rate,
            "selling_price_list": so.selling_price_list,
            "price_list_currency": so.price_list_currency,
            "plc_conversion_rate": so.plc_conversion_rate,
            "ignore_pricing_rule": so.ignore_pricing_rule,
            "set_warehouse": doc.to_warehouse,
            "tc_name": so.tc_name,
            "terms": so.terms,
            "apply_discount_on": so.apply_discount_on,
            "base_discount_amount": so.base_discount_amount,
            "additional_discount_percentage": so.additional_discount_percentage,
            "discount_amount": so.discount_amount,
            "driver": so.driver,
            "project": so.project,
            "vehicle": so.vehicle,
        })
        so_items = frappe.db.sql(""" select d.so_item, d.so, d.idx, d.item_code, d.item_name, d.description, d.qty, a.stock_qty, a.uom, a.stock_uom, a.conversion_factor, a.rate, a.amount,
                                               a.price_list_rate, a.base_price_list_rate, a.base_rate, a.base_amount, a.net_rate, a.net_amount, a.margin_type, a.margin_rate_or_amount, a.rate_with_margin,
                                               a.discount_percentage, a.discount_amount, a.base_rate_with_margin, a.item_tax_template
                                               from `tabStock Entry Detail` d join`tabSales Order Item` a on d.so_item = a.name 
                                               join `tabStock Entry` b on d.parent = b.name
                                               where b.name = '{name}'
                                           """.format(name=doc.name), as_dict=1)

        for c in so_items:
            items = new_doc.append("items", {})
            items.idx = c.idx
            items.item_code = c.item_code
            items.item_name = c.item_name
            items.description = c.description
            items.qty = c.qty
            items.uom = c.uom
            items.stock_uom = c.stock_uom
            items.conversion_factor = c.conversion_factor
            items.price_list_rate = c.price_list_rate
            items.base_price_list_rate = c.base_price_list_rate
            items.base_rate = c.base_rate
            items.base_amount = c.base_amount
            items.rate = c.rate
            items.net_rate = c.net_rate
            items.net_amount = c.net_amount
            items.amount = c.amount
            items.margin_type = c.margin_type
            items.margin_rate_or_amount = c.margin_rate_or_amount
            items.rate_with_margin = c.rate_with_margin
            items.discount_percentage = c.discount_percentage
            items.discount_amount = c.discount_amount
            items.base_rate_with_margin = c.base_rate_with_margin
            items.item_tax_template = c.item_tax_template
            items.sales_order = c.so
            items.so_detail = c.so_item

        so_taxes = frappe.db.sql(""" select a.charge_type, a.row_id, a.account_head, a.description, a.included_in_print_rate, a.included_in_paid_amount, a.rate, a.account_currency, a.tax_amount,
                                            a.total, a.tax_amount_after_discount_amount, a.base_tax_amount, a.base_total, a.base_tax_amount_after_discount_amount, a.item_wise_tax_detail, a.dont_recompute_tax,
                                            a.vehicle, a.department, a.cost_center, a.branch
                                           from `tabSales Taxes and Charges` a join `tabSales Order` b
                                           on a.parent = b.name
                                           where b.name = '{name}'
                                       """.format(name=doc.sales_order), as_dict=1)

        for x in so_taxes:
            taxes = new_doc.append("taxes", {})
            taxes.charge_type = x.charge_type
            taxes.row_id = x.row_id
            taxes.account_head = x.account_head
            taxes.description = x.description
            taxes.included_in_print_rate = x.included_in_print_rate
            taxes.included_in_paid_amount = x.included_in_paid_amount
            #taxes.rate = x.rate
            #taxes.account_currency = x.account_currency
            #taxes.tax_amount = x.tax_amount
            #taxes.total = x.total
            #taxes.tax_amount_after_discount_amount = x.tax_amount_after_discount_amount
            #taxes.base_tax_amount = x.base_tax_amount
            #taxes.base_total = x.base_total
            #taxes.base_tax_amount_after_discount_amount = x.base_tax_amount_after_discount_amount
            taxes.item_wise_tax_detail = x.item_wise_tax_detail
            taxes.dont_recompute_tax = x.dont_recompute_tax
            taxes.vehicle = x.vehicle
            taxes.department = x.department
            taxes.branch = x.branch
            taxes.cost_center = x.cost_center

        new_doc.insert()
        frappe.msgprint(new_doc.name + " تم إنشاء فاتورة مبيعات بحالة مسودة رقم ")
@frappe.whitelist()
def ste_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def ste_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def ste_before_save(doc, method=None):
    pass
@frappe.whitelist()
def ste_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def ste_on_update(doc, method=None):
    pass

################ Blanket Order

@frappe.whitelist()
def blank_onload(doc, method=None):
    pass
@frappe.whitelist()
def blank_before_validate(doc, method=None):
    pass
@frappe.whitelist()
def blank_validate(doc, method=None):
    pass
@frappe.whitelist()
def blank_on_submit(doc, method=None):
    pass
@frappe.whitelist()
def blank_on_cancel(doc, method=None):
    pass
@frappe.whitelist()
def blank_on_update_after_submit(doc, method=None):
    pass
@frappe.whitelist()
def blank_before_save(doc, method=None):
    pass
@frappe.whitelist()
def blank_before_cancel(doc, method=None):
    pass
@frappe.whitelist()
def blank_on_update(doc, method=None):
    pass
