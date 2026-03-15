import sys
try:
    import src.odoo_manager as core
    print("Syntax ok!")
except Exception as e:
    print("FAILED TO LOAD:", e)
