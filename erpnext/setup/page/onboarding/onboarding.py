import frappe
from frappe.geo.country_info import get_country_timezone_info


@frappe.whitelist()
def get_onboarding_data():
	workspaces = frappe.get_all("Workspace", fields=["name", "title", "module", "icon"])
	regional_data = get_country_timezone_info()

	return {"workspaces": workspaces, "regional_data": regional_data}
