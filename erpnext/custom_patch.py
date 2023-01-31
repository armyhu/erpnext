import frappe
from erpnext.setup.doctype.employee.employee import create_user
import pandas as pd

# def post_payment_je_leave_encashment():
#     le = frappe.db.sql("""
#         select expense_claim from `tabLeave Encashment` where
#         docstatus = 1
#     """,as_dict=1)
#     for a in le:
#         expense_claim = frappe.get_doc("Expense Claim", a.expense_claim)
#         if expense_claim.docstatus = 1:
#             expense_claim.post_accounts_entry()
#             print(expense_claim.name)
#     frappe.db.commit()

def assign_je_in_invoice():
    print('<------------------------------------------------------------------------------------------------>')
    for d in frappe.db.sql('''
                select reference_name, reference_type, parent from `tabJournal Entry Account` where reference_type in ('Transporter Invoice','EME Invoice')
                ''', as_dict=True):
        if d.reference_type and d.reference_name and frappe.db.exists(d.reference_type, d.reference_name):
            doc = frappe.get_doc(str(d.reference_type),str(d.reference_name))
            doc.db_set("journal_entry",d.parent)
    print('Done')
def assign_ess_role():
    users = frappe.db.sql("""
        select name from `tabUser` where name not in ('Guest', 'Administrator')
    """,as_dict=1)
    for a in users:
        user = frappe.get_doc("User", a.name)
        user.flags.ignore_permissions = True
        if "Employee Self Service" not in frappe.get_roles(a.name):
            user.add_roles("Employee Self Service")
            print("Employee Self Service role added for user {}".format(a.name))


def delete_salary_detail_salary_slip():
    ssd = frappe.db.sql("""
        select name from `tabSalary Detail` where parenttype = 'Salary Slip'
    """,as_dict=1)
    for a in ssd:
        frappe.db.sql("delete from `tabSalary Detail` where name = '{}'".format(a.name))
        print(a.name)

def create_users():
    print("here")

    employees = frappe.db.sql("""
        select name from `tabEmployee` where company_email is not NULL and user_id is NULL
    """,as_dict=1)
    if employees:
        for a in employees:
            employee = frappe.get_doc("Employee", a.name)
            if not frappe.db.exists("User",employee.company_email):
                create_user(a.name, email = employee.company_email)
                print("User created for employee {}".format(a.name))
                employee.db_set("user_id", employee.company_email)
    frappe.db.commit()

def update_employee_user_id():
    print()
    users = frappe.db.sql("""
        select name from `tabUser`
    """,as_dict=1)
    if users:
        for a in users:
            employee = frappe.db.get_value("Employee",{"company_email":a.name},"name")
            if employee:
                employee_doc = frappe.get_doc("Employee",employee)
                employee_doc.db_set("user_id",a.name)
                print("Updated email for "+str(a.name))
    frappe.db.commit()

def update_benefit_type_name():
    bt = frappe.db.sql("""
        select name, benefit_type from `tabEmployee Benefit Type`;
    """, as_dict=True)
    if bt:
        for a in bt:
            frappe.db.sql("update `tabEmployee Benefit Type` set name = '{}' where name = '{}'".format(a.benefit_type, a.name))
            print(a.name)

def update_department():
    el = frappe.db.sql("""
        select name from `tabEmployee`
        where department = 'Habrang & Tshophangma Coal Mine - SMCL'
        and status = 'Active'
    """,as_dict=1)
    if el:
        for a in el:
            frappe.db.sql("""
                update `tabEmployee` set department = 'PROJECTS & MINES DEPARTMENT - SMCL'
                where name = '{}'
            """.format(a.name))
            print(a.name)

def update_user_pwd():
    user_list = frappe.db.sql("select name from `tabUser` where name not in ('Administrator', 'Guest')", as_dict=1)
    c = 1
    non_employee = []
    for i in user_list:
        print("NAME '{}':  '{}'".format(c,str(i.name)))
        if not frappe.db.exists("Employee", {"user_id":i.name}):
            non_employee.append({"User ID":i.name, "User Name":frappe.db.get_value("User",i.name,"full_name")})
        ds = frappe.get_doc("User", i.name)
        ds.new_password = 'smcl@2022'
        ds.save(ignore_permissions=1)
        c += 1
    # df = pd.DataFrame(data = non_employee) # convert dict to dataframe
    # df.to_excel("Users Without Employee Data.xlsx", index=False)
    # print("Dictionery Converted in to Excel")

def update_ref_doc():
    for a in frappe.db.sql("""
                            select name 
                            from 
                                `tabExpense Claim` 
                            where 
                                docstatus != 2
                            """):
        print(a[0])
        reference = frappe.db.sql("""
                            select expense_type
                            from 
                                `tabExpense Claim Detail` 
                            where 
                            parent = "{}"
                            """.format(a[0]))
        print(reference[0][0])
        
        frappe.db.sql("""
            update 
                `tabExpense Claim`
            set ref_doc ="{0}"
            where name ="{1}"
        """.format(reference[0][0],a[0]))