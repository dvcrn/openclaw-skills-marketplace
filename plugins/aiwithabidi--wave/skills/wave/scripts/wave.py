#!/usr/bin/env python3
"""Wave API CLI. Zero dependencies beyond Python stdlib."""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse


def get_token():
    token = os.environ.get("WAVE_API_TOKEN", "")
    if not token:
        env_path = os.path.join(os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("WAVE_API_TOKEN="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not token:
        print("Error: WAVE_API_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    return token


API_URL = "https://gql.waveapps.com/graphql/public"

def gql(query, variables=None):
    data = {"query": query}
    if variables: data["variables"] = variables
    body = json.dumps(data).encode()
    req = urllib.request.Request(API_URL, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {get_token()}")
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read().decode())
        if result.get("errors"): print(f"GQL Error: {result['errors']}", file=sys.stderr); sys.exit(1)
        return result.get("data", {})
    except urllib.error.HTTPError as e:
        print(f"API Error {e.code}: {e.read().decode()}", file=sys.stderr); sys.exit(1)

def cmd_businesses(a):
    d = gql("query{businesses{edges{node{id name isPersonal currency{code}}}}}")
    for e in d.get("businesses",{}).get("edges",[]): print(json.dumps(e["node"]))

def cmd_invoices(a):
    d = gql("query($bid:ID!,$page:Int,$size:Int){business(id:$bid){invoices(page:$page,pageSize:$size){edges{node{id title status total{value currency{code}}customer{name}invoiceDate dueDate}}}}}", {"bid":a.business_id,"page":a.page,"size":a.limit})
    for e in d.get("business",{}).get("invoices",{}).get("edges",[]): print(json.dumps(e["node"]))

def cmd_invoice_get(a):
    d = gql("query($bid:ID!,$iid:ID!){business(id:$bid){invoice(id:$iid){id title status total{value}customer{name}items{description quantity unitPrice{value}}invoiceDate dueDate pdfUrl}}}", {"bid":a.business_id,"iid":a.id})
    print(json.dumps(d.get("business",{}).get("invoice",{}), indent=2))

def cmd_invoice_create(a):
    items = json.loads(a.items) if a.items else [{"description":"Service","unitPrice":a.amount or "0","quantity":1}]
    d = gql("mutation($input:InvoiceCreateInput!){invoiceCreate(input:$input){invoice{id title status viewUrl}didSucceed inputErrors{path message}}}", {"input":{"businessId":a.business_id,"customerId":a.customer_id,"items":items}})
    print(json.dumps(d.get("invoiceCreate",{}), indent=2))

def cmd_invoice_send(a):
    d = gql("mutation($input:InvoiceSendInput!){invoiceSend(input:$input){didSucceed inputErrors{message}}}", {"input":{"invoiceId":a.id}})
    print(json.dumps(d.get("invoiceSend",{}), indent=2))

def cmd_invoice_delete(a):
    d = gql("mutation($input:InvoiceDeleteInput!){invoiceDelete(input:$input){didSucceed}}", {"input":{"invoiceId":a.id}})
    print(json.dumps(d.get("invoiceDelete",{})))

def cmd_customers(a):
    d = gql("query($bid:ID!,$page:Int,$size:Int){business(id:$bid){customers(page:$page,pageSize:$size){edges{node{id name email}}}}}",{"bid":a.business_id,"page":1,"size":a.limit})
    for e in d.get("business",{}).get("customers",{}).get("edges",[]): print(json.dumps(e["node"]))

def cmd_customer_create(a):
    d = gql("mutation($input:CustomerCreateInput!){customerCreate(input:$input){customer{id name email}didSucceed inputErrors{message}}}", {"input":{"businessId":a.business_id,"name":a.name,"email":a.email}})
    print(json.dumps(d.get("customerCreate",{}), indent=2))

def cmd_accounts(a):
    d = gql("query($bid:ID!){business(id:$bid){accounts{edges{node{id name type{value}subtype{value}currency{code}}}}}}",{"bid":a.business_id})
    for e in d.get("business",{}).get("accounts",{}).get("edges",[]): print(json.dumps(e["node"]))

def cmd_transactions(a):
    d = gql("query($bid:ID!,$page:Int,$size:Int){business(id:$bid){transactions(page:$page,pageSize:$size){edges{node{id description date amount{value currency{code}}account{name}}}}}}",{"bid":a.business_id,"page":a.page,"size":a.limit})
    for e in d.get("business",{}).get("transactions",{}).get("edges",[]): print(json.dumps(e["node"]))

def cmd_products(a):
    d = gql("query($bid:ID!,$page:Int,$size:Int){business(id:$bid){products(page:$page,pageSize:$size){edges{node{id name description unitPrice}}}}}",{"bid":a.business_id,"page":1,"size":a.limit})
    for e in d.get("business",{}).get("products",{}).get("edges",[]): print(json.dumps(e["node"]))

def cmd_taxes(a):
    d = gql("query($bid:ID!){business(id:$bid){salesTaxes{edges{node{id name rate}}}}}",{"bid":a.business_id})
    for e in d.get("business",{}).get("salesTaxes",{}).get("edges",[]): print(json.dumps(e["node"]))

def main():
    p = argparse.ArgumentParser(description="Wave Accounting CLI")
    s = p.add_subparsers(dest="command")
    s.add_parser("businesses")
    x = s.add_parser("invoices"); x.add_argument("business_id"); x.add_argument("--limit", type=int, default=50); x.add_argument("--page", type=int, default=1)
    x = s.add_parser("invoice"); x.add_argument("business_id"); x.add_argument("id")
    x = s.add_parser("invoice-create"); x.add_argument("business_id"); x.add_argument("customer_id"); x.add_argument("--items"); x.add_argument("--amount")
    x = s.add_parser("invoice-send"); x.add_argument("id")
    x = s.add_parser("invoice-delete"); x.add_argument("id")
    x = s.add_parser("customers"); x.add_argument("business_id"); x.add_argument("--limit", type=int, default=50)
    x = s.add_parser("customer-create"); x.add_argument("business_id"); x.add_argument("name"); x.add_argument("email")
    x = s.add_parser("accounts"); x.add_argument("business_id")
    x = s.add_parser("transactions"); x.add_argument("business_id"); x.add_argument("--limit", type=int, default=50); x.add_argument("--page", type=int, default=1)
    x = s.add_parser("products"); x.add_argument("business_id"); x.add_argument("--limit", type=int, default=50)
    x = s.add_parser("taxes"); x.add_argument("business_id")
    a = p.parse_args()
    c = {"businesses":cmd_businesses,"invoices":cmd_invoices,"invoice":cmd_invoice_get,"invoice-create":cmd_invoice_create,"invoice-send":cmd_invoice_send,"invoice-delete":cmd_invoice_delete,"customers":cmd_customers,"customer-create":cmd_customer_create,"accounts":cmd_accounts,"transactions":cmd_transactions,"products":cmd_products,"taxes":cmd_taxes}
    if a.command in c: c[a.command](a)
    else: p.print_help()

if __name__ == "__main__": main()
