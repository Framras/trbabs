import frappe
import datetime


@frappe.whitelist()
def create_babs_forms(babsyear: int, babsmonth: int, babslimit: int):
    company = frappe.defaults.get_user_default("Company")

    start_date = datetime.date(year=int(babsyear), month=int(babsmonth), day=1)
    end_date = frappe.utils.get_last_day(start_date)

    babsmap = {}

    customers = frappe.get_all("Customer", filters={"customer_type": "Company", "tax_id": ["not in", None]},
                               fields=["tax_id", "name"])
    for customer in customers:
        sales_invoice_count_since_start = frappe.db.count("Sales Invoice",
                                                          filters={"docstatus": 1, "company": company,
                                                                   "customer": customer.name,
                                                                   "posting_date": [">=", start_date]})
        sales_invoice_count_since_end = frappe.db.count("Sales Invoice",
                                                        filters={"docstatus": 1, "company": company,
                                                                 "customer": customer.name,
                                                                 "posting_date": [">", end_date]})
        sales_invoice_count = sales_invoice_count_since_start - sales_invoice_count_since_end
        if sales_invoice_count > 0:
            customer_total_since_start = frappe.db.get_all("Sales Invoice",
                                                           filters={"docstatus": 1, "company": company,
                                                                    "customer": customer.name,
                                                                    "posting_date": [">=", start_date]},
                                                           fields=["sum(net_total) as sales_total", "customer"],
                                                           group_by="customer")
            customer_total_since_end = frappe.db.get_all("Sales Invoice",
                                                         filters={"docstatus": 1, "company": company,
                                                                  "customer": customer.name,
                                                                  "posting_date": [">", end_date]},
                                                         fields=["sum(net_total) as sales_total", "customer"],
                                                         group_by="customer")
            if len(customer_total_since_end) > 0:
                customer_total = int(
                    customer_total_since_start[0].sales_total - customer_total_since_end[0].sales_total)
            else:
                customer_total = int(customer_total_since_start[0].sales_total)

            if customer_total >= int(babslimit):
                if babsmap.get(customer.tax_id) is None:
                    babsmap[customer.tax_id] = dict(customer=customer.name,
                                                    bs_invoice_count=sales_invoice_count,
                                                    bs_total=customer_total)

    suppliers = frappe.get_all("Supplier", filters={"supplier_type": "Company", "tax_id": ["not in", None]},
                               fields=["tax_id", "name"])
    for supplier in suppliers:
        purchase_invoice_count_since_start = frappe.db.count("Purchase Invoice",
                                                             filters={"docstatus": 1, "supplier": supplier.name,
                                                                      "bill_date": [">=", start_date]})
        purchase_invoice_count_since_end = frappe.db.count("Purchase Invoice",
                                                           filters={"docstatus": 1, "supplier": supplier.name,
                                                                    "bill_date": [">", end_date]})
        purchase_invoice_count = purchase_invoice_count_since_start - purchase_invoice_count_since_end
        if purchase_invoice_count > 0:
            supplier_total_since_start = frappe.db.get_all("Purchase Invoice",
                                                           filters={"docstatus": 1, "supplier": supplier.name,
                                                                    "bill_date": [">=", start_date]},
                                                           fields=["sum(net_total) as purchase_total", "supplier"],
                                                           group_by="supplier")
            supplier_total_since_end = frappe.db.get_all("Purchase Invoice",
                                                         filters={"docstatus": 1, "supplier": supplier.name,
                                                                  "bill_date": [">", end_date]},
                                                         fields=["sum(net_total) as purchase_total", "supplier"],
                                                         group_by="supplier")
            if len(supplier_total_since_end) > 0:
                supplier_total = int(supplier_total_since_start[0].purchase_total - supplier_total_since_end[
                    0].purchase_total)
            else:
                supplier_total = int(supplier_total_since_start[0].purchase_total)

            if supplier_total >= int(babslimit):
                if babsmap.get(supplier.tax_id) is None:
                    babsmap[supplier.tax_id] = dict(supplier=supplier.name,
                                                    ba_invoice_count=purchase_invoice_count,
                                                    ba_total=supplier_total)
                else:
                    babsmap[supplier.tax_id]["supplier"] = supplier.name
                    babsmap[supplier.tax_id]["ba_invoice_count"] = purchase_invoice_count
                    babsmap[supplier.tax_id]["ba_total"] = supplier_total

    for tax_id in babsmap.keys():
        if not frappe.db.exists({
            "doctype": "BA BS Form",
            "company": company,
            "year": babsyear,
            "month": babsmonth,
            "tax_id": tax_id
        }):
            new_doc = frappe.new_doc("BA BS Form")
            new_doc.company = company
            new_doc.year = babsyear
            new_doc.month = babsmonth
            new_doc.tax_id = tax_id
            if babsmap.get(tax_id).get("supplier") is not None:
                new_doc.supplier = babsmap.get(tax_id).get("supplier")
            new_doc.ba_invoice_count = babsmap.get(tax_id).get("ba_invoice_count")
            new_doc.ba_total = babsmap.get(tax_id).get("ba_total")
            if babsmap.get(tax_id).get("customer") is not None:
                new_doc.customer = babsmap.get(tax_id).get("customer")
            new_doc.bs_invoice_count = babsmap.get(tax_id).get("bs_invoice_count")
            new_doc.bs_total = babsmap.get(tax_id).get("bs_total")
            new_doc.insert()
        else:
            frappe_doc = frappe.get_doc({
                "doctype": "BA BS Form",
                "company": company,
                "year": babsyear,
                "month": babsmonth,
                "tax_id": tax_id
            })
            if frappe_doc.form_sent == 0:
                if babsmap.get(tax_id).get("supplier") is not None:
                    frappe_doc.supplier = babsmap.get(tax_id).get("supplier")
                frappe_doc.ba_invoice_count = babsmap.get(tax_id).get("ba_invoice_count")
                frappe_doc.ba_total = babsmap.get(tax_id).get("ba_total")
                if babsmap.get(tax_id).get("customer") is not None:
                    frappe_doc.customer = babsmap.get(tax_id).get("customer")
                frappe_doc.bs_invoice_count = babsmap.get(tax_id).get("bs_invoice_count")
                frappe_doc.bs_total = babsmap.get(tax_id).get("bs_total")
                frappe_doc.save()

    return frappe.utils.now_datetime()