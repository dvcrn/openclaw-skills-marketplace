#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmlrpc.client
import ssl
import argparse
import os
import logging
import base64
import urllib.request
from datetime import date, timedelta

# ==========================================
# LOGGING CONFIGURATION
# ==========================================
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==========================================
# ODOO CONNECTION SETTINGS (ENV VARIABLES)
# ==========================================
URL = os.getenv('ODOO_URL')
DB = os.getenv('ODOO_DB')
USER = os.getenv('ODOO_USER')
PASS = os.getenv('ODOO_PASSWORD') 

if __name__ == '__main__':
    if not all([URL, DB, USER, PASS]):
        print("❌ Missing Odoo Environment Variables. Please configure ODOO_URL, ODOO_DB, ODOO_USER, and ODOO_PASSWORD in your .env file.")
        exit(1)

# ==========================================
# BUSINESS SPECIFIC CONSTANTS
# ==========================================
# Note: You might need to adjust these IDs to match your Odoo database setup.
TAX_ID = int(os.getenv('ODOO_DEFAULT_TAX_ID', '1'))  # Default Tax ID 
LOCATION_ID = int(os.getenv('ODOO_LOCATION_ID', '8')) # Default Stock Location ID
DEFAULT_CATEGORY = int(os.getenv('ODOO_DEFAULT_CATEGORY', '1')) # Default Product Category ID

# ==========================================
# ODOO CLIENT LOGIC
# ==========================================

def connect():
    """Establish a secure SSL connection with Odoo via XML-RPC"""
    context = ssl.create_default_context()
    
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', context=context)
        uid = common.authenticate(DB, USER, PASS, {})
        if not uid:
            raise Exception("Authentication failed. Please check your credentials.")
        
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', context=context)
        logger.info(f"✅ Connected to {URL} as {USER}")
        return uid, models
    except Exception as e:
        logger.error(f"Connection Error: {str(e)}")
        exit(1)

def check_sales():
    """Query today's POS sales and pending Web orders"""
    uid, models = connect()
    today = str(date.today())
    
    # 1. POS (Point of Sale) - Today's Sales
    pos_domain = [
        ['date_order', '>=', today + ' 00:00:00'],
        ['date_order', '<=', today + ' 23:59:59'],
        ['state', 'in', ['paid', 'done', 'invoiced']]
    ]
    
    try:
        pos_data = models.execute_kw(DB, uid, PASS, 'pos.order', 'read_group', 
            [pos_domain, ['amount_total'], []])
        
        pos_total = pos_data[0]['amount_total'] if pos_data else 0.0
        pos_count = models.execute_kw(DB, uid, PASS, 'pos.order', 'search_count', [pos_domain])
    except Exception as e:
        logger.warning(f"Failed to query POS (Point of Sale module might not be installed): {e}")
        pos_total = 0.0
        pos_count = 0

    # 2. WEB - Pending Orders
    web_domain = [
        ['state', '=', 'sale'],              
        ['website_id', '!=', False],         
        ['picking_ids.state', 'not in', ['done', 'cancel']]  
    ]
    
    try:
        web_ids = models.execute_kw(DB, uid, PASS, 'sale.order', 'search', [web_domain])
    except Exception as e:
        logger.warning(f"Failed to query Sales Orders: {e}")
        web_ids = []
    
    # GENERATE REPORT
    report = f"📊 **DAILY STORE REPORT ({today})**\n"
    report += f"💰 **POS Revenue:** {pos_total:.2f} (from {pos_count} tickets)\n"
    
    if not web_ids:
        report += "✅ All clear. No pending web orders to ship."
    else:
        report += f"📦 **{len(web_ids)} PENDING WEB ORDERS:**\n"
        orders = models.execute_kw(DB, uid, PASS, 'sale.order', 'read', [web_ids], 
            {'fields': ['name', 'partner_id', 'amount_total', 'partner_shipping_id', 'order_line']})
        
        for o in orders:
            try:
                shipping_data = models.execute_kw(DB, uid, PASS, 'res.partner', 'read', 
                    [o['partner_shipping_id'][0]], {'fields': ['city', 'zip']})
                shipping = shipping_data[0] if shipping_data else {}
                city = shipping.get('city', 'Unknown City')
            except:
                city = 'Unknown Location'
                
            report += f"\n🔸 **{o['name']}** | {o['partner_id'][1]} ({city})\n"
            
            lines = models.execute_kw(DB, uid, PASS, 'sale.order.line', 'read', [o['order_line']], {'fields': ['name', 'product_uom_qty']})
            for l in lines:
                prod_name = l['name'].split(']')[1].strip() if ']' in l['name'] else l['name']
                report += f"   - {int(l['product_uom_qty'])}x {prod_name[:40]}...\n"

    return report

def check_stock(query):
    """Search products by name or barcode and return Quick Info"""
    uid, models = connect()
    
    domain = ['|', ['barcode', '=', query], ['name', 'ilike', query]]
    p_ids = models.execute_kw(DB, uid, PASS, 'product.product', 'search', [domain], {'limit': 20})
    
    if not p_ids:
        return f"❌ Couldn't find anything matching '{query}'."
    
    products = models.execute_kw(DB, uid, PASS, 'product.product', 'read', [p_ids], 
        {'fields': ['name', 'list_price', 'qty_available', 'virtual_available']})
        
    msg = ""
    if len(products) == 1:
        p = products[0]
        msg = (
            f"✅ **{p['name']}**\n"
            f"💰 Price: {p['list_price']}\n"
            f"📦 Physical Stock: {int(p['qty_available'])}\n"
            f"📅 Forecasted: {int(p['virtual_available'])}"
        )
    else:
        msg = f"🔎 **Found {len(products)} matches:**\n"
        for p in products:
            msg += f"- **{p['name']}**: {int(p['qty_available'])} units ({p['list_price']})\n"
            
    return msg

def update_stock(ref, quantity):
    """Updates physical stock quantity"""
    uid, models = connect()
    quantity = float(quantity)

    domain = ['|', ['barcode', '=', ref], ['name', 'ilike', ref]]
    p_ids = models.execute_kw(DB, uid, PASS, 'product.product', 'search', [domain])
    
    if not p_ids:
        return f"❌ Cannot find product '{ref}'."
    
    product_id = p_ids[0]
    product = models.execute_kw(DB, uid, PASS, 'product.product', 'read', [product_id], {'fields': ['name', 'type', 'is_storable']})[0]
    name = product['name']

    quant_domain = [['product_id', '=', product_id], ['location_id', '=', LOCATION_ID]]
    quant_ids = models.execute_kw(DB, uid, PASS, 'stock.quant', 'search', [quant_domain])
    
    try:
        if quant_ids:
            models.execute_kw(DB, uid, PASS, 'stock.quant', 'write', [quant_ids, {'inventory_quantity': quantity}])
            try:
                models.execute_kw(DB, uid, PASS, 'stock.quant', 'action_apply_inventory', [quant_ids])
            except Exception as e:
                if "cannot marshal None" not in str(e): raise e

        else:
            models.execute_kw(DB, uid, PASS, 'stock.quant', 'create', [{
                'product_id': product_id,
                'location_id': LOCATION_ID,
                'inventory_quantity': quantity
            }])
            quant_ids = models.execute_kw(DB, uid, PASS, 'stock.quant', 'search', [quant_domain])
            if quant_ids:
                try:
                    models.execute_kw(DB, uid, PASS, 'stock.quant', 'action_apply_inventory', [quant_ids])
                except Exception as e:
                    if "cannot marshal None" not in str(e): raise e
                
        return f"✅ Stock for **{name}** updated to **{int(quantity)}** units."
        
    except Exception as e:
        logger.error(f"Error updating stock: {e}")
        return f"❌ Odoo Error trying to update stock: {e}"

# ==========================================
# CLI ARGUMENT HANDLING
# ==========================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Odoo Store CLI interface for OpenClaw")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: check_sales
    subparsers.add_parser('check_sales', help="Check today's POS sales and pending web orders")

    # Command: check_stock
    sp_search = subparsers.add_parser('check_stock', help="Search for a product's stock")
    sp_search.add_argument('--query', '--name', required=True, help="Product Name or Barcode to search")

    # Command: update_stock
    sp_update = subparsers.add_parser('update_stock', help="Update product's stock quantity")
    sp_update.add_argument('--ref', '--barcode', '--name', required=True, help="Product Reference (Name or Barcode)")
    sp_update.add_argument('--qty', required=True, type=float, help="New absolute quantity")

    # Command: top_sales
    sp_top = subparsers.add_parser('top_sales', help="Check top sales for a period (e.g., month, year)")
    sp_top.add_argument('--period', default='mes', help="Period word (year, month, week)")

    # Command: add_product
    sp_add = subparsers.add_parser('add_product', help="Add or update a stock product")
    sp_add.add_argument('--name', required=True)
    sp_add.add_argument('--price', required=True)
    sp_add.add_argument('--qty', required=True)
    sp_add.add_argument('--barcode', default="")
    sp_add.add_argument('--category', default="")
    sp_add.add_argument('--min_age', default="0")
    sp_add.add_argument('--players', default="")
    sp_add.add_argument('--time', default="")
    sp_add.add_argument('--description', default="None")

    args = parser.parse_args()

    if args.command == 'check_sales':
        print(check_sales())
    elif args.command == 'check_stock':
        print(check_stock(args.query))
    elif args.command == 'update_stock':
        print(update_stock(args.ref, args.qty))
    elif args.command == 'top_sales':
        print(get_top_sales(args.period))
    elif args.command == 'add_product':
        print(add_product(
            args.name, args.price, args.qty, args.barcode, args.category, 
            args.min_age, args.players, args.time, args.description
        ))
    else:
        parser.print_help()

def parse_price(price_input):
    """Safely converts price input to float"""
    if isinstance(price_input, (float, int)):
        return float(price_input)
    if isinstance(price_input, str):
        clean_price = price_input.replace(',', '.')
        if clean_price.count('.') > 1:
            clean_price = clean_price.replace('.', '', clean_price.count('.') - 1)
        return float(clean_price)
    return 0.0

def add_product(name, price, qty, barcode, category_hint, min_age, players, time, description):
    """Creates a new Consumable/Storable product with basic website info"""
    uid, models = connect()
    
    try:
        final_price = parse_price(price)
    except ValueError:
        return f"❌ Error: Invalid price '{price}'."
        
    product_id = False
    if barcode and barcode not in ["None", "Unknown", ""]:
        ids = models.execute_kw(DB, uid, PASS, 'product.template', 'search', [[['barcode', '=', barcode]]])
        if ids: product_id = ids[0]
        
    if not product_id:
        ids = models.execute_kw(DB, uid, PASS, 'product.template', 'search', [[['name', '=', name]]])
        if ids: product_id = ids[0]

    web_html = f"""
    <div class="product-description-wrapper">
        <div class="product-intro">{description}</div>
        <hr/>
        <div class="product-specs">
            <h3>📋 Specs</h3>
            <ul>
                <li><strong>👥 Players:</strong> {players}</li>
                <li><strong>⏳ Time:</strong> {time} min</li>
                <li><strong>👶 Min. Age:</strong> {min_age}+</li>
            </ul>
        </div>
    </div>
    """

    if product_id:
        vals = {
            'list_price': final_price,
            'taxes_id': [(6, 0, [TAX_ID])]
        }
        models.execute_kw(DB, uid, PASS, 'product.template', 'write', [[product_id], vals])
        stock_msg = update_stock(name, qty)
        return f"🔄 **UPDATED:** {name}\n- Price: {final_price}\n- {stock_msg}"
        
    else:
        vals = {
            'name': name,
            'list_price': final_price,
            'type': 'consu', # Default to consumable to avoid complex stock tracking initially
            'is_storable': True, 
            'barcode': barcode if barcode not in ["None", ""] else False,
            'default_code': barcode if barcode not in ["None", ""] else False,
            'categ_id': DEFAULT_CATEGORY,
            'taxes_id': [(6, 0, [TAX_ID])],
            'description_ecommerce': web_html,
            'website_published': True,
            'available_in_pos': True,
        }
        try:
            new_id = models.execute_kw(DB, uid, PASS, 'product.template', 'create', [vals])
            stock_msg = update_stock(name, qty)
            return f"✅ **CREATED:** {name} (ID: {new_id})\n- Price: {price}\n- {stock_msg}"
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            return f"❌ Critical Odoo Error: {str(e)}"

def get_top_sales(period):
    """Fetches top selling products for the given period"""
    uid, models = connect()
    today = date.today()
    
    if 'year' in period or 'año' in period:
        days = 365
        label = "Last Year"
    elif '2' in period:
        days = 60
        label = "Last 2 Months"
    elif 'week' in period or 'semana' in period:
        days = 7
        label = "Last Week"
    else:
        days = 30
        label = "Last Month"
        
    start_date = str(today - timedelta(days=days))
    product_sales = {} 

    try:
        # 1. POS SALES
        try:
            pos_domain = [['order_id.date_order', '>=', start_date], ['order_id.state', 'in', ['paid', 'done', 'invoiced']]]
            pos_groups = models.execute_kw(DB, uid, PASS, 'pos.order.line', 'read_group', [pos_domain, ['qty'], ['product_id']], {'lazy': False})
            for g in pos_groups:
                if not g.get('product_id'): continue
                pid, name = g['product_id'][0], g['product_id'][1]
                qty = g['qty']
                if pid not in product_sales: product_sales[pid] = {'name': name, 'qty': 0}
                product_sales[pid]['qty'] += qty
        except Exception as e:
            logger.warning(f"Could not read POS sales: {e}")

        # 2. WEB/BACKEND SALES
        try:
            sale_domain = [['state', 'in', ['sale', 'done']], ['order_id.date_order', '>=', start_date]]
            sale_groups = models.execute_kw(DB, uid, PASS, 'sale.order.line', 'read_group', [sale_domain, ['product_uom_qty'], ['product_id']], {'lazy': False})
            for g in sale_groups:
                if not g.get('product_id'): continue
                pid, name = g['product_id'][0], g['product_id'][1]
                qty = g.get('product_uom_qty', 0)
                if pid not in product_sales: product_sales[pid] = {'name': name, 'qty': 0}
                product_sales[pid]['qty'] += qty
        except Exception as e:
            logger.warning(f"Could not read Web sales: {e}")

        # Sort and Format
        sorted_products = sorted(product_sales.values(), key=lambda x: x['qty'], reverse=True)[:50]

        if not sorted_products:
            return f"📉 No sales recorded in: {label}"
            
        report = f"📊 **TOP SALES ({label})**\n\n"
        for idx, p in enumerate(sorted_products):
            report += f"{idx+1}. **{int(p['qty'])}**x {p['name']}\n"
            
        return report

    except Exception as e:
        logger.error(f"Error getting top sales: {e}")
        return f"❌ Error querying sales: {e}"
