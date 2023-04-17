# this script pulls a "Received Invoices" report and outputs a .CSV file into local folder

import requests
import json
import csv


def find_invoice_status(code):

    """
    from 
    https://2ndsiteinc.atlassian.net/wiki/spaces/Development/pages/5612829/Invoice+Estimate+Status

    0: Disputed
    1: Draft
    2: Sent
    3: Viewed
    4: Paid
    5: Autopaid
    6: Retry
    7: Failed
    "8": "Partial"
    "1000": "Defunct"
    Overdue - no constant exists for this, it is calculated as part of the v3_status in evolve.
    !: "declined" -- by looking in the gateway_order table
    !: "pending" -- by looking in the gateway_order table 
    """

    match code:
        case 0:
            return "Disputed"
        case 1:
            return "Draft"
        case 2:
            return "Sent"
        case 3:
            return "Viewed"
        case 4:
            return "Paid"
        case 5:
            return "Autopaid"
        case 6:
            return "Retry"
        case 7:
            return "Failed"
        case 8:
            return "Partially Paid"
        case 1000:
            return "Defunct, code 1000"
        case _:
            return "Unhandled case code"


def print_to_output():
        print("Invoice Num: ",invoice_number)
        print("Issue date: ",issue_date)
        print("Invoice Status code = ", invoice_status_code)
        print("Invoice Status: ", invoice_status)
        print(json.dumps([sender, amount], indent=4))
        print("amount paid: ", amount_paid)
        print("====================")
        print("")


while True:
    token = input("Account's Bearer Token: ").strip()
    businessid = input("Account's business_id: ").strip()
    accountid = input("Account's hash_id: ").strip()
    confirm = input("use the following info? y/n: ").strip()
    if confirm.strip().lower() == "y":
        break


url = f"https://api.freshbooks.com/search/account/{accountid}/received_invoices_current?businessid={businessid}&page=1&sort=-create_date&status="
headers = {'Authorization': f'Bearer {token}', 'Api-Version': 'alpha', 'Content-Type': 'application/json'}
res = requests.get(url, data=None, headers=headers)
json_data = res.json()
dumps = json.dumps(json_data,indent=4)

# print(dumps)

num_pages = int(json_data['response']['result']['pages']) #2
invoices = json_data['response']['result']['invoices']

with open(f'{accountid}_received_invoices.csv', 'w', newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Invoice Number", "Issue Date", "Status", "Sender Org", "Sender Name", "Currency", "Amount", "Amount Paid"])

    for i in range (1, num_pages + 1):
        page_url = f"https://api.freshbooks.com/search/account/{accountid}/received_invoices_current?businessid={businessid}&page={i}&sort=-create_date&status="

        for invoice in invoices:

            invoice_number = invoice['invoice_number']
            issue_date = invoice['fulfillment_date']
            invoice_status_code = invoice['status']
            invoice_status = find_invoice_status(invoice_status_code)
            amount_paid = invoice['net_paid_amount']['amount']
            sender = {
                'name' : invoice['owner']['fname'] + " " + invoice['owner']['lname'],
                'organization' : invoice['owner']['organization']
            }
            amount = {
                'amount' : invoice['amount']['amount'],
                'currency' : invoice['amount']['code']
            }

            writer.writerow(
                [invoice_number,
                 issue_date,
                 invoice_status,
                 sender['organization'],
                 sender['name'],
                 amount['currency'],
                 amount['amount'],
                 amount_paid]
                 )


            # print("Invoice Num: ",invoice_number)
            # print("Issue date: ",issue_date)
            # print("Invoice Status code = ", invoice_status_code)
            # print("Invoice Status: ", invoice_status)
            # print(json.dumps([sender, amount], indent=4))
            # print("amount paid: ", amount_paid)
            # print("====================")
            # print("")

print("*** PROGRAM COMPLETE:  Check the folder that this program exists in for the CSV file ***")

    
