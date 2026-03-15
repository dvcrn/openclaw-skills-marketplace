#!/usr/bin/env python3
import json, sys, time, datetime, urllib.request, csv
from pathlib import Path

DATA_DIR = Path("./data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_URL = "https://online-price-watch.consumer.org.hk/opw/opendata/pricewatch_en.csv"
TODAY = datetime.date.today()
MAX_QUERY_LENGTH = 200

def detect_language(text):
    if any('\u4e00' <= c <= '\u9fff' for c in text):
        return 'zh-HK'
    return 'en'

LOCALE = {
    'en': {
        'not_found': "Sorry, I couldn't find any products matching '{query}'.",
        'overall_cheapest': "Overall cheapest: {supermarket} - {product} (${price:.2f})",
        'budget_calc': "With $100 you can buy {qty} items (remaining ${remain:.2f})",
        'no_price': "No price data available."
    },
    'zh-HK': {
        'not_found': "抱歉，找不到與'{query}'相關的產品。",
        'overall_cheapest': "整體最平：{supermarket} - {product} (${price:.2f})",
        'budget_calc': "用 $100 可以買 {qty} 件（剩餘 ${remain:.2f}）",
        'no_price': "沒有價格資料。"
    }
}

def log(msg):
    print(f"[{datetime.datetime.now().isoformat()}] {msg}", file=sys.stderr)

def download_pricewatch():
    for attempt in range(1, 3):
        try:
            log("Downloading pricewatch...")
            req = urllib.request.Request(
                DATA_URL,
                headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'text/csv'}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read().decode('utf-8')
            if not content.strip():
                raise Exception("empty response")
            return content
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
            return None

def ensure_data():
    today_file = DATA_DIR / f"pricewatch_en_{TODAY.strftime('%Y-%m-%d')}.csv"
    if today_file.exists() and today_file.stat().st_size > 1000:
        return str(today_file)
    content = download_pricewatch()
    if content:
        with open(today_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(today_file)
    cands = sorted(DATA_DIR.glob("pricewatch_en_*.csv"),
                   key=lambda p: p.stat().st_mtime,
                   reverse=True)
    return str(cands[0]) if cands else None

def housekeep():
    try:
        cutoff = TODAY - datetime.timedelta(days=1)
        for fp in DATA_DIR.glob("pricewatch_en_*.csv"):
            try:
                dt = datetime.datetime.strptime(
                    fp.stem.replace('pricewatch_en_', ''), "%Y-%m-%d"
                ).date()
                if dt < cutoff:
                    fp.unlink()
            except:
                pass
    except:
        pass

def load_csv(path):
    data = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                data.append(row)
        return data
    except:
        return []

def search_items(data, q):
    q = q.lower()
    res = []
    for it in data:
        name = it.get('Product Name', '').lower()
        brand = it.get('Brand', '').lower()
        cat1 = it.get('Category 1', '').lower()
        if q in name or q in brand or q in cat1:
            try:
                price = float(it.get('Price', '').replace('$', '').strip())
            except:
                price = None
            res.append({
                'name': it.get('Product Name', '').strip(),
                'supermarket': it.get('Supermarket Code', '').strip(),
                'price': price
            })
    return res

def overall_cheapest(results):
    valid = [r for r in results if r['price'] is not None]
    return min(valid, key=lambda x: x['price']) if valid else None

def format_answer(query, results, lang):
    loc = LOCALE[lang]
    if not results:
        return loc['not_found'].format(query=query)
    cheapest = overall_cheapest(results)
    if not cheapest:
        return loc['no_price']
    qty = int(100 // cheapest['price']) if cheapest['price'] > 0 else 0
    if qty > 0:
        return f"{loc['overall_cheapest'].format(supermarket=cheapest['supermarket'], product=cheapest['name'], price=cheapest['price'])}. {loc['budget_calc'].format(qty=qty, remain=100 - qty*cheapest['price'])}"
    else:
        return loc['overall_cheapest'].format(supermarket=cheapest['supermarket'], product=cheapest['name'], price=cheapest['price']) + "."

def answer(query):
    if not query or len(query) > MAX_QUERY_LENGTH:
        return "Invalid query."
    p = ensure_data()
    if not p:
        return "Unable to retrieve data."
    housekeep()
    data = load_csv(p)
    if not data:
        return "Data load failed."
    results = search_items(data, query)
    lang = detect_language(query)
    return format_answer(query, results, lang)

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing query"}))
        sys.exit(1)
    try:
        print(json.dumps({
            "query": sys.argv[1],
            "answer": answer(sys.argv[1])
        }, ensure_ascii=False))
    except:
        print(json.dumps({"error": "Internal error"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
