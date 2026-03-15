import os, json, time, base64, requests, numpy as np, math
from datetime import datetime, timezone
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as AP
from cryptography.hazmat.backends import default_backend

KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2"
KEY_ID      = "bf937112-eb74-4bdc-bcc4-fcb725ae2d41"
KEY_PATH    = "/Users/kao/.openclaw/workspace/skills/kalshi-trading/keys/private_key.pem"
TG_TOKEN    = "7956217548:AAEV9hmTe2HpK5unLKtgm6CCNwA0nAPBNz8"
TG_CHAT     = "6850287860"
OPENAI_KEY  = "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"
CB_BASE     = "https://api.coinbase.com"
STATE_FILE  = "/Users/kao/apex/state.json"
LOG_FILE    = "/Users/kao/apex/apex.log"

SERIES     = {"KXBTC15M":"BTC","KXETH15M":"ETH","KXSOL15M":"SOL","KXXRP15M":"XRP"}
TICKER_MAP = {"BTC":"BTC-USD","ETH":"ETH-USD","SOL":"SOL-USD","XRP":"XRP-USD"}

MIN_MINUTES      = 8
MAX_MINUTES      = 360
MAX_CONTRACTS    = 3
MIN_BALANCE      = 20
MAX_DAILY_TRADES = 6
MAX_OPEN         = 3

def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    try:
        with open(LOG_FILE,"a") as f: f.write(line+"\n")
    except: pass

def tg(msg):
    try: requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",json={"chat_id":TG_CHAT,"text":msg},timeout=5)
    except: pass

def load_state():
    try:
        with open(STATE_FILE) as f: return json.load(f)
    except: return {"trades":[],"daily":{}}

def save_state(s):
    with open(STATE_FILE,"w") as f: json.dump(s,f,indent=2)

def load_key():
    with open(KEY_PATH,"rb") as f:
        return serialization.load_pem_private_key(f.read(),password=None,backend=default_backend())

def sign(key, method, path, body=""):
    ts  = str(int(datetime.now(timezone.utc).timestamp()))
    msg = (ts+method+"/trade-api/v2"+path+body).encode()
    sig = key.sign(msg,AP.PSS(mgf=AP.MGF1(hashes.SHA256()),salt_length=AP.PSS.DIGEST_LENGTH),hashes.SHA256())
    return {"KALSHI-ACCESS-KEY":KEY_ID,"KALSHI-ACCESS-TIMESTAMP":ts,"KALSHI-ACCESS-SIGNATURE":base64.b64encode(sig).decode()}

def kget(key, path, params=None):
    r=requests.get(KALSHI_BASE+path,headers=sign(key,"GET",path),params=params,timeout=15)
    r.raise_for_status(); return r.json()

def kpost(key, path, body):
    b=json.dumps(body); h=sign(key,"POST",path,b); h["Content-Type"]="application/json"
    r=requests.post(KALSHI_BASE+path,headers=h,data=b.encode(),timeout=15)
    r.raise_for_status(); return r.json()

def get_balance(key):
    try: return round(float(kget(key,"/portfolio/balance").get("balance",0))/100,2)
    except: return 0.0

_cache={}; _cache_ts={}

def get_signals(asset):
    product = TICKER_MAP.get(asset)
    if not product: return None
    ck = f"c_{product}"
    if ck in _cache and time.time()-_cache_ts.get(ck,0)<60:
        candles=_cache[ck]
    else:
        try:
            end=int(time.time()); start=end-3600*48
            r=requests.get(f"{CB_BASE}/api/v3/brokerage/market/products/{product}/candles",
                params={"start":start,"end":end,"granularity":"ONE_HOUR"},timeout=10)
            r.raise_for_status()
            candles=sorted([{"t":int(c["start"]),"c":float(c["close"]),"v":float(c["volume"])} for c in r.json().get("candles",[])],key=lambda x:x["t"])
            _cache[ck]=candles; _cache_ts[ck]=time.time()
        except Exception as e:
            log(f"  Candle error {asset}: {e}"); return None
    if not candles: return None
    closes=np.array([c["c"] for c in candles])
    vols=np.array([c["v"] for c in candles])
    if len(closes)<15: return None
    deltas=np.diff(closes); gains=np.where(deltas>0,deltas,0.0); losses=np.where(deltas<0,-deltas,0.0)
    ag=np.mean(gains[:14]); al=np.mean(losses[:14])
    for i in range(14,len(gains)):
        ag=(ag*13+gains[i])/14; al=(al*13+losses[i])/14
    rsi=100.0 if al==0 else 100-(100/(1+ag/al))
    mom_1h = float((closes[-1]-closes[-2])/closes[-2]*100) if closes[-2]!=0 else 0
    mom_4h = float((closes[-1]-closes[-5])/closes[-5]*100) if len(closes)>=5 and closes[-5]!=0 else 0
    avg_vol=np.mean(vols[-14:]); vol_spike=round(float(vols[-1]/avg_vol),2) if avg_vol>0 else 1.0
    price=float(closes[-1])
    bull_signals = sum([rsi>55, mom_1h>0, mom_4h>0, vol_spike>1.2])
    bear_signals = sum([rsi<45, mom_1h<0, mom_4h<0, vol_spike>1.2 and mom_1h<0])
    if bull_signals >= 3: direction = "UP"
    elif bear_signals >= 3: direction = "DOWN"
    else: direction = "UNCLEAR"
    return {
        "asset": asset, "price": price,
        "rsi": round(float(rsi),1),
        "mom_1h": round(mom_1h,3), "mom_4h": round(mom_4h,3),
        "vol_spike": vol_spike,
        "direction": direction,
        "bull_signals": bull_signals, "bear_signals": bear_signals
    }

def ai_decide(signals, market):
    try:
        prompt = f"""You are APEX, a binary options trader on Kalshi prediction markets.

MARKET: {market["ticker"]}
This is a YES/NO market: Will {signals["asset"]} price be HIGHER in the next {round(market["mins"],0)} minutes?
- YES costs {market["yes_ask"]}c (pays $1 if price goes UP)
- NO costs {market["no_ask"]}c (pays $1 if price goes DOWN)

CURRENT SIGNALS:
- Price: ${signals["price"]:,.2f}
- RSI: {signals["rsi"]} (>55 bullish, <45 bearish)
- 1hr momentum: {signals["mom_1h"]:+.3f}%
- 4hr momentum: {signals["mom_4h"]:+.3f}%
- Volume spike: {signals["vol_spike"]}x average
- Signal vote: {signals["bull_signals"]} bullish vs {signals["bear_signals"]} bearish
- Overall direction: {signals["direction"]}

TASK: Decide whether to trade and which side.
- Only trade if you have clear conviction
- Consider: is YES or NO better value given the signals?
- Consider: is {round(market["mins"],0)} minutes enough time for the move?

Output ONLY JSON:
{{"trade": true/false, "side": "yes/no", "contracts": 1/2/3, "confidence": 0.0-1.0, "thesis": "one sentence max", "risk": "main risk"}}"""

        r=requests.post("https://api.openai.com/v1/chat/completions",
            headers={"Authorization":f"Bearer {OPENAI_KEY}"},
            json={"model":"gpt-4o-mini","messages":[{"role":"user","content":prompt}],"max_tokens":120,"temperature":0.1},
            timeout=15)
        content=r.json()["choices"][0]["message"]["content"].replace("```json","").replace("```","").strip()
        return json.loads(content)
    except Exception as e:
        log(f"  AI error: {e}"); return {"trade":False,"side":"no","contracts":1,"confidence":0,"thesis":"AI unavailable","risk":"unknown"}

def judge_trades(key, state):
    updated=False
    for t in state["trades"]:
        if t.get("outcome"): continue
        try:
            mk=kget(key,f"/markets/{t['ticker']}").get("market",{})
            result=mk.get("result","")
            if result in ("yes","no"):
                won=t["side"]==result
                cost=t["entry_cost"]/100; n=t["contracts"]
                t["outcome"]="win" if won else "loss"
                t["pnl"]=round((1-cost)*n if won else -cost*n,2)
                dk=t["ts"][:10]
                if dk not in state["daily"]: state["daily"][dk]={"trades":0,"pnl":0}
                state["daily"][dk]["pnl"]=round(state["daily"][dk].get("pnl",0)+t["pnl"],2)
                emoji="✅" if won else "❌"
                msg=f"{emoji} APEX {t['coin']} {t['side'].upper()} {t['outcome'].upper()} P&L:${t['pnl']:+.2f}\n{t['ticker']}"
                log(msg); tg(msg); updated=True
        except Exception as e: log(f"  Judge error: {e}")
    if updated: save_state(state)

def run():
    log(f"APEX v3.1 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    key=load_key(); bal=get_balance(key); state=load_state()
    closed=[t for t in state["trades"] if t.get("outcome")]
    open_t=[t for t in state["trades"] if not t.get("outcome")]
    wins=sum(1 for t in closed if t["outcome"]=="win")
    losses=sum(1 for t in closed if t["outcome"]=="loss")
    pnl=round(sum(t.get("pnl",0) for t in closed),2)
    wr=int(wins/max(wins+losses,1)*100)
    dk=datetime.now().strftime("%Y-%m-%d")
    daily=state["daily"].get(dk,{"trades":0,"pnl":0})
    log(f"Balance:${bal} | P&L:${pnl} | {wins}W/{losses}L {wr}%WR | Today:{daily['trades']}t ${daily.get('pnl',0)}")
    if open_t:
        for t in open_t: log(f"  OPEN: {t['coin']} {t['side'].upper()} @{t['entry_cost']}c x{t['contracts']}")

    judge_trades(key, state)

    if bal < MIN_BALANCE: log(f"  Balance too low — stop"); save_state(state); return
    if len(open_t) >= MAX_OPEN: log(f"  Max open positions"); save_state(state); return
    if daily["trades"] >= MAX_DAILY_TRADES: log(f"  Max daily trades"); save_state(state); return
    if daily.get("pnl",0) < -10: log(f"  Daily loss limit hit"); save_state(state); return

    signals_cache={}
    candidates=[]

    for series,asset in SERIES.items():
        try: markets=kget(key,"/markets",{"limit":2,"status":"open","series_ticker":series}).get("markets",[])
        except Exception as e: log(f"  {series} error: {e}"); continue
        for m in markets:
            try:
                expiry=datetime.fromisoformat(m["close_time"].replace("Z","+00:00"))
                mins=(expiry-datetime.now(timezone.utc)).total_seconds()/60
                if not (MIN_MINUTES<=mins<=MAX_MINUTES): continue
                yes_ask=float(m.get("yes_ask_dollars") or 0)
                no_ask=float(m.get("no_ask_dollars") or 0)
                if yes_ask<=0 or no_ask<=0: continue
                if asset not in signals_cache: signals_cache[asset]=get_signals(asset)
                signals=signals_cache[asset]
                if not signals: continue
                log(f"  {asset} {m['ticker'][-12:]} {round(mins,1)}min | RSI={signals['rsi']} mom1h={signals['mom_1h']:+.2f}% vol={signals['vol_spike']}x | {signals['direction']} YES:{yes_ask}c NO:{no_ask}c")
                if signals["direction"]=="UNCLEAR": continue
                candidates.append({"asset":asset,"ticker":m["ticker"],"yes_ask":yes_ask,"no_ask":no_ask,"mins":mins,"signals":signals})
            except Exception as e: log(f"  Market error: {e}")

    if not candidates:
        log("  No clear directional signals — standing by"); save_state(state); return

    for c in candidates:
        log(f"  Asking AI about {c['asset']} {c['ticker'][-12:]}...")
        ai=ai_decide(c["signals"],c)
        log(f"  AI: trade={ai['trade']} side={ai.get('side','?')} contracts={ai.get('contracts',1)} conf={ai.get('confidence',0):.0%} | {ai.get('thesis','')}")

        if not ai["trade"]: continue

        side=ai["side"]; n=min(int(ai.get("contracts",1)),MAX_CONTRACTS)
        entry=c["yes_ask"] if side=="yes" else c["no_ask"]
        entry_cents=round(entry)
        cost=round(entry_cents*n/100,2)

        if entry_cents>80: log(f"  Entry {entry_cents}c too expensive"); continue
        if cost>bal*0.15: n=max(1,int(bal*0.15*100/entry_cents)); cost=round(entry_cents*n/100,2)

        log(f"  PLACING {side.upper()} x{n} @{entry_cents}c on {c['ticker']} cost=${cost}")
        price_key="yes_price" if side=="yes" else "no_price"
        body={"ticker":c["ticker"],"action":"buy","side":side,"type":"limit","count":n,price_key:entry_cents}
        try:
            resp=kpost(key,"/portfolio/orders",body)
            order=resp.get("order",resp); oid=order.get("order_id","")
            if oid:
                log(f"  ORDER ✅ id={oid}")
                trade={"ts":datetime.now(timezone.utc).isoformat(),"coin":c["asset"],"ticker":c["ticker"],
                       "side":side,"entry_cost":entry_cents,"contracts":n,"cost":cost,"order_id":oid,
                       "confidence":ai["confidence"],"thesis":ai["thesis"],"risk":ai["risk"],"outcome":None,"pnl":0}
                state["trades"].append(trade)
                if dk not in state["daily"]: state["daily"][dk]={"trades":0,"pnl":0}
                state["daily"][dk]["trades"]+=1
                tg(f"⚡ APEX {c['asset']} {side.upper()} x{n} @{entry_cents}c\n{ai['thesis']}\nRisk: {ai['risk']}\nBalance:${bal} Cost:${cost}")
                break
            else:
                log(f"  ORDER FAILED ❌ {resp}")
        except Exception as e: log(f"  Execute error: {e}")

    save_state(state)

if __name__ == "__main__":
    run()