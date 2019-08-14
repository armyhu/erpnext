# coding: utf-8
"""
Provide a report and downloadable CSV according to the German DATEV format.

- Query report showing only the columns that contain data, formatted nicely for
  dispay to the user.
- CSV download functionality `download_datev_csv` that provides a CSV file with
  all required columns. Used to import the data into the DATEV Software.
"""
from __future__ import unicode_literals
import datetime
import json
import StringIO
import zipfile
from six import string_types
import frappe
from frappe import _
import pandas as pd
from datev_constants import DataCategory
from datev_constants import Transactions
from datev_constants import DebtorsCreditors
from datev_constants import AccountNames
from datev_constants import QUERY_REPORT_COLUMNS


def execute(filters=None):
	"""Entry point for frappe."""
	validate(filters)
	result = get_transactions(filters, as_dict=0)
	columns = QUERY_REPORT_COLUMNS

	return columns, result


def validate(filters):
	"""Make sure all mandatory filters and settings are present."""
	if not filters.get('company'):
		frappe.throw(_('<b>Company</b> is a mandatory filter.'))

	if not filters.get('from_date'):
		frappe.throw(_('<b>From Date</b> is a mandatory filter.'))

	if not filters.get('to_date'):
		frappe.throw(_('<b>To Date</b> is a mandatory filter.'))

	try:
		frappe.get_doc('DATEV Settings', filters.get('company'))
	except frappe.DoesNotExistError:
		frappe.throw(_('Please create <b>DATEV Settings</b> for Company <b>{}</b>.').format(filters.get('company')))


def get_transactions(filters, as_dict):
	"""
	Get a list of accounting entries.

	Select GL Entries joined with Account and Party Account in order to get the
	account numbers. Returns a list of accounting entries.

	Arguments:
	filters -- dict of filters to be passed to the sql query
	as_dict -- return as list of dicts [0,1]
	"""
	gl_entries = frappe.db.sql("""
		select

			/* either debit or credit amount; always positive */
			case gl.debit when 0 then gl.credit else gl.debit end as 'Umsatz (ohne Soll/Haben-Kz)',

			/* 'H' when credit, 'S' when debit */
			case gl.debit when 0 then 'H' else 'S' end as 'Soll/Haben-Kennzeichen',

			/* account number or, if empty, party account number */
			coalesce(acc.account_number, acc_pa.account_number) as 'Kontonummer',

			/* against number or, if empty, party against number */
			coalesce(acc_against.account_number, acc_against_pa.account_number) as 'Gegenkonto (ohne BU-Schlüssel)',
			
			gl.posting_date as 'Belegdatum',
			gl.remarks as 'Buchungstext',
			gl.voucher_type as 'Beleginfo - Art 1',
			gl.voucher_no as 'Beleginfo - Inhalt 1',
			gl.against_voucher_type as 'Beleginfo - Art 2',
			gl.against_voucher as 'Beleginfo - Inhalt 2'

		from `tabGL Entry` gl

			/* Statistisches Konto (Debitoren/Kreditoren) */
			left join `tabParty Account` pa
			on gl.against = pa.parent
			and gl.company = pa.company

			/* Kontonummer */
			left join `tabAccount` acc 
			on gl.account = acc.name

			/* Gegenkonto-Nummer */
			left join `tabAccount` acc_against 
			on gl.against = acc_against.name

			/* Statistische Kontonummer */
			left join `tabAccount` acc_pa
			on pa.account = acc_pa.name

			/* Statistische Gegenkonto-Nummer */
			left join `tabAccount` acc_against_pa 
			on pa.account = acc_against_pa.name

		where gl.company = %(company)s 
		and DATE(gl.posting_date) >= %(from_date)s
		and DATE(gl.posting_date) <= %(to_date)s
		order by 'Belegdatum', gl.voucher_no""", filters, as_dict=as_dict)

	return gl_entries


def get_customers(filters, as_dict):
	"""
	Get a list of Debtors and Creditors.

	Arguments:
	filters -- dict of filters to be passed to the sql query
	as_dict -- return as list of dicts [0,1]
	"""
	# TODO: map to DebtorCreditor.COLUMNS
	return frappe.db.sql("""select * from tabCustomer""", filters, as_dict=as_dict)


def get_suppliers(filters, as_dict):
	"""
	Get a list of Debtors and Creditors.

	Arguments:
	filters -- dict of filters to be passed to the sql query
	as_dict -- return as list of dicts [0,1]
	"""
	# TODO: map to DebtorCreditor.COLUMNS
	return frappe.db.sql("""select * from tabSupplier""", filters, as_dict=as_dict)


def get_account_names(filters):
	return frappe.get_list("Account", 
		fields=["account_number", "name"], 
		filters={"company": filters.get("company")})


def get_datev_csv(data, filters, csv_class):
	"""
	Fill in missing columns and return a CSV in DATEV Format.

	For automatic processing, DATEV requires the first line of the CSV file to
	hold meta data such as the length of account numbers oder the category of
	the data.

	Arguments:
	data -- array of dictionaries
	filters -- dict
	csv_class -- defines DATA_CATEGORY, FORMAT_NAME and COLUMNS
	"""
	header = get_header(filters, csv_class)

	empty_df = pd.DataFrame(columns=csv_class.COLUMNS)
	data_df = pd.DataFrame.from_records(data)

	result = empty_df.append(data_df)

	if csv_class.DATA_CATEGORY == DataCategory.TRANSACTIONS:
		result['Belegdatum'] = pd.to_datetime(result['Belegdatum'])

	if csv_class.DATA_CATEGORY == DataCategory.ACCOUNT_NAMES:
		result['Sprach-ID'] = 'de-DE'

	header = ';'.join(header).encode('latin_1')
	data = result.to_csv(
		sep=b';',
		# European decimal seperator
		decimal=',',
		# Windows "ANSI" encoding
		encoding='latin_1',
		# format date as DDMM
		date_format='%d%m',
		# Windows line terminator
		line_terminator=b'\r\n',
		# Do not number rows
		index=False,
		# Use all columns defined above
		columns=csv_class.COLUMNS
	)

	return header + b'\r\n' + data


def get_header(filters, csv_class):
	header = [
		# A = DATEV format
		#   DTVF = created by DATEV software,
		#   EXTF = created by other software
		"EXTF",
		# B = version of the DATEV format
		#   141 = 1.41, 
		#   510 = 5.10,
		#   720 = 7.20
		"510",
		csv_class.DATA_CATEGORY,
		csv_class.FORMAT_NAME,
		# E = Format version (regarding format name)
		"",
		# F = Generated on
		datetime.datetime.now().strftime("%Y%m%d"),
		# G = Imported on -- stays empty
		"",
		# H = Origin (SV = other (?), RE = KARE)
		"SV",
		# I = Exported by
		frappe.session.user,
		# J = Imported by -- stays empty
		"",
		# K = Tax consultant number (Beraternummer)
		frappe.get_value("DATEV Settings", filters.get("company"), "consultant_number") or "",
		"",
		# L = Tax client number (Mandantennummer)
		frappe.get_value("DATEV Settings", filters.get("company"), "client_number") or "",
		"",
		# M = Start of the fiscal year (Wirtschaftsjahresbeginn)
		frappe.utils.formatdate(frappe.defaults.get_user_default("year_start_date"), "yyyyMMdd"),
		# N = Length of account numbers (Sachkontenlänge)
		"4",
		# O = Transaction batch start date (YYYYMMDD)
		frappe.utils.formatdate(filters.get('from_date'), "yyyyMMdd"),
		# P = Transaction batch end date (YYYYMMDD)
		frappe.utils.formatdate(filters.get('to_date'), "yyyyMMdd"),
		# Q = Description (for example, "January - February 2019 Transactions")
		"{} - {} {}".format(
				frappe.utils.formatdate(filters.get('from_date'), "MMMM yyyy"),
				frappe.utils.formatdate(filters.get('to_date'), "MMMM yyyy"),
				csv_class.FORMAT_NAME
		),
		# R = Diktatkürzel
		"",
		# S = Buchungstyp
		#   1 = Transaction batch (Buchungsstapel),
		#   2 = Annual financial statement (Jahresabschluss)
		"1" if csv_class.DATA_CATEGORY == DataCategory.TRANSACTIONS else "",
		# T = Rechnungslegungszweck
		"",
		# U = Festschreibung
		"",
		# V = Kontoführungs-Währungskennzeichen des Geldkontos
		frappe.get_value("Company", filters.get("company"), "default_currency")
	]
	return header


@frappe.whitelist()
def download_datev_csv(filters=None):
	"""
	Provide accounting entries for download in DATEV format.

	Validate the filters, get the data, produce the CSV file and provide it for
	download. Can be called like this:

	GET /api/method/erpnext.regional.report.datev.datev.download_datev_csv

	Arguments / Params:
	filters -- dict of filters to be passed to the sql query
	"""
	if isinstance(filters, string_types):
		filters = json.loads(filters)

	validate(filters)

	# This is where my zip will be written
	zip_buffer = StringIO.StringIO()
	# This is my zip file
	zip_archive = zipfile.ZipFile(zip_buffer, mode='w')

	transactions = get_transactions(filters, as_dict=1)
	transactions_csv = get_datev_csv(transactions, filters, csv_class=Transactions)
	zip_archive.writestr('EXTF_Buchungsstapel.csv', transactions_csv)

	account_names = get_account_names(filters)
	account_names_csv = get_datev_csv(account_names, filters, csv_class=AccountNames)
	zip_archive.writestr('EXTF_Kontenbeschriftungen.csv', account_names_csv)

	customers = get_customers(filters)
	customers_csv = get_datev_csv(customers, filters, csv_class=DebtorsCreditors)
	zip_archive.writestr('EXTF_Kunden.csv', customers_csv)

	suppliers = get_suppliers(filters)
	suppliers_csv = get_datev_csv(suppliers, filters, csv_class=DebtorsCreditors)
	zip_archive.writestr('EXTF_Lieferanten.csv', suppliers)

	frappe.response['result'] = zip_buffer.get_value()
	frappe.response['doctype'] = 'DATEV'
	frappe.response['type'] = 'zip'
