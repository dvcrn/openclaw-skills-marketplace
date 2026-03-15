#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmlrpc.client
import ssl
import time
import os
import subprocess
import shlex
import logging
import re

# ==========================================
# LOGGING CONFIGURATION
# ==========================================
logging.basicConfig(
    level=logging.INFO,
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
BOT_PARTNER_ID = int(os.getenv('ODOO_BOT_ID', '0'))

if not all([URL, DB, USER, PASS, BOT_PARTNER_ID]):
    raise ValueError("❌ Missing Environment Variables. Please configure ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD, and ODOO_BOT_ID in your .env file.")

def connect():
    """Secure SSL connection with Odoo"""
    context = ssl.create_default_context()
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common', context=context)
        uid = common.authenticate(DB, USER, PASS, {})
        models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object', context=context)
        return uid, models
    except Exception as e:
        logger.error(f"❌ Error connecting to Odoo: {e}")
        return None, None

def run_manager_tool(command_args):
    """Executes the odoo_manager.py script and returns the result."""
    start_time = time.time()
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, 'odoo_manager.py')
        
        cmd = ["python3", script_path] + shlex.split(command_args)
        logger.debug(f"⚙️ Executing: {' '.join(cmd)}")
        
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=30)
        output = result.decode('utf-8')
        
        return output
        
    except subprocess.TimeoutExpired:
        return "⚠️ Error: The command took too long to execute."
    except Exception as e:
        return f"⚠️ Unexpected Error: {str(e)}"

def format_response_html(text):
    """Adapts markdown text to Odoo Discuss HTML formats"""
    # Odoo 18 recognizes markdown with double new lines
    md = text.replace('\n', '\n\n')
    return f"🤖 *OpenClaw Assistant:*\n\n{md}"

def listen_loop():
    logger.info(f"🎧 OpenClaw listening on {URL} (Partner ID: {BOT_PARTNER_ID})...")
    uid, models = connect()
    
    if not uid:
        logger.error("❌ Could not connect. Check credentials.")
        return

    last_processed_id = 0
    try:
        initial_search = models.execute_kw(DB, uid, PASS, 'mail.message', 'search', 
            [[]], {'limit': 1, 'order': 'id desc'})
        if initial_search:
            last_processed_id = initial_search[0]
            logger.info(f"🔄 Starting from message ID: {last_processed_id}")
    except Exception as e:
        logger.warning(f"Could not fetch last message ID: {e}")

    while True:
        try:
            domain = [
                ['id', '>', last_processed_id],
                ['message_type', '=', 'comment'],
                ['author_id', '!=', BOT_PARTNER_ID]
            ]
            
            msg_ids = models.execute_kw(DB, uid, PASS, 'mail.message', 'search', 
                [domain], {'order': 'id asc', 'limit': 10})
            
            if msg_ids:
                messages = models.execute_kw(DB, uid, PASS, 'mail.message', 'read', [msg_ids], 
                    {'fields': ['body', 'author_id', 'res_id', 'model', 'partner_ids', 'message_type']})
                
                for msg in messages:
                    current_id = msg['id']
                    last_processed_id = max(last_processed_id, current_id)
                    
                    author_name = msg['author_id'][1] if msg['author_id'] else "System"
                    model = msg.get('model', '')
                    
                    is_direct_mention = BOT_PARTNER_ID in msg.get('partner_ids', [])
                    is_channel_chat = model == 'discuss.channel'
                    
                    if not (is_direct_mention or is_channel_chat):
                        continue
                    
                    raw_text = msg['body'] or ""
                    text_no_br = raw_text.replace('<br>', ' ').replace('<br/>', ' ').replace('</p>', ' ').replace('</div>', ' ')
                    clean_text = re.sub(r'<[^>]+>', '', text_no_br).strip()
                    clean_text = re.sub(r'\s+', ' ', clean_text)
                    clean_text_lower = clean_text.lower()
                    
                    response_text = ""
                    keywords_found = False
                    
                    # 1: CHECK SALES
                    if any(x in clean_text_lower for x in ['sales', 'revenue', 'caja', 'ventas']):
                        response_text = run_manager_tool("check_sales")
                        keywords_found = True
                    
                    # 2: UPDATE STOCK
                    stock_match = re.search(r"(?:update|set|ajusta)\s+stock\s+(?:for|of|de)?\s*(?P<ref>.+?)\s+(?:to|a)\s+(?P<qty>\d+)", clean_text, re.IGNORECASE)
                    if stock_match and not keywords_found:
                        ref = stock_match.group('ref').strip()
                        qty = stock_match.group('qty')
                        cmd = f"update_stock --ref {shlex.quote(ref)} --qty {qty}"
                        response_text = run_manager_tool(cmd)
                        keywords_found = True

                    # 3: CHECK STOCK
                    stock_check_match = re.search(r"(?:do we have|check stock of|tienes|busca)\s+(?P<query>.+?)\??$", clean_text, re.IGNORECASE)
                    if stock_check_match and not keywords_found:
                        query = stock_check_match.group('query').strip()
                        if len(query) > 2:
                            cmd = f"check_stock --query {shlex.quote(query)}"
                            response_text = run_manager_tool(cmd)
                            keywords_found = True

                    if not keywords_found and is_direct_mention:
                        response_text = f"Hello {author_name}, I am your connected OpenClaw Manager. How can I help you today?"

                    # ACTION
                    if response_text:
                        body_html = format_response_html(response_text)
                        target_model = msg['model']
                        target_id = msg['res_id']
                        
                        if target_model and target_id:
                            models.execute_kw(DB, uid, PASS, target_model, 'message_post', [target_id], {
                                'body': body_html,
                                'message_type': 'comment',
                                'subtype_xmlid': 'mail.mt_comment',
                                'author_id': BOT_PARTNER_ID
                            })
                            logger.info(f"✅ Replied to {author_name}.")
            
            time.sleep(3)

        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping listener...")
            break
        except Exception as e:
            logger.error(f"⚠️ Loop Error: {e}")
            time.sleep(5)
            uid, models = connect()

if __name__ == "__main__":
    listen_loop()
