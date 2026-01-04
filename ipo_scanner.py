import yfinance as yf
import pandas as pd
import requests
import io
import datetime

# --- USER CONFIGURATION ---
START_DATE_FILTER = "2021-01-01" 
CAPITAL_PER_TRADE = 10000 

# Telegram Credentials
TELEGRAM_BOT_TOKEN = "8422955277:AAHtxQSNbXfeYtBd0UjGp8-cOwV7VWOrVVE"
TELEGRAM_CHAT_ID = "1075420371"

def send_telegram_alert(stock, price, resistance, stop_loss, status):
    try:
        msg = (
            f"🚀 *IPO BREAKOUT ALERT (Website)* 🚀\n\n"
            f"📈 *Stock:* {stock}\n"
            f"💰 *Entry Price:* ₹{price}\n"
            f"🚧 *Resistance Broken:* ₹{resistance}\n"
            f"🛑 *Stop Loss:* ₹{stop_loss}\n"
            f"ℹ️ *Status:* {status}\n"
            f"⚠️ *Note:* Verify chart before buying."
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        params = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        requests.get(url, params=params)
    except Exception as e:
        print(f"Telegram Error: {e}")

def get_dynamic_stock_list():
    tickers = []
    # Method 1: Internet List
    try:
        url = "https://raw.githubusercontent.com/sahilrahman12/Nifty-500-Companies-List-with-Sector-Industry-Analysis/main/nifty_500.csv"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            if 'Symbol' in df.columns:
                tickers = [f"{x}.NS" for x in df['Symbol'].tolist()]
    except:
        pass

    # Method 2: Fallback List
    fallback_list = [
        "ZOMATO.NS", "PAYTM.NS", "LICI.NS", "AWL.NS", "NYKAA.NS", "POLICYBZR.NS",
        "DELHIVERY.NS", "CAMPUS.NS", "TATATECH.NS", "IREDA.NS", "JIOFIN.NS", 
        "DOMS.NS", "AZAD.NS", "BAJAJHFL.NS", "OLAELEC.NS", "PREMIERENE.NS", 
        "BHARTIHEXA.NS", "GODIGIT.NS", "AADHARHFC.NS", "JYOTICNC.NS", 
        "EXICOM.NS", "PLATIND.NS", "MUKKA.NS", "HAPPYFORGE.NS", "INOXINDIA.NS", 
        "MUTHOOTMF.NS", "INDIASHELTER.NS", "HONASA.NS", "CELLO.NS", "RRKABEL.NS", 
        "CONCORDBIO.NS", "SBFC.NS", "NETWEB.NS", "SENCO.NS", "CYIENTDLM.NS", 
        "IDEAFORGE.NS", "IKIO.NS", "MANKIND.NS", "AVALON.NS", "DIVGIITTS.NS", 
        "BSE.NS", "CDSL.NS", "ANGELONE.NS", "MCX.NS", "CAMS.NS", "KFINTECH.NS", 
        "MAPMYINDIA.NS", "DATAPATTNS.NS", "MEDPLUS.NS", "METROBRAND.NS"
    ]
    
    final_list = list(set(tickers + fallback_list))
    return final_list

def run_ipo_scan(progress_bar=None, enable_alerts=False):
    tickers = get_dynamic_stock_list()
    results = []
    
    total = len(tickers)
    processed = 0
    alerts_sent_count = 0
    
    for ticker in tickers:
        processed += 1
        if progress_bar:
            progress_bar.progress(processed / total, text=f"Scanning {ticker}...")

        try:
            df = yf.download(ticker, period="max", progress=False, auto_adjust=True)
            if df.empty or len(df) < 50: continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            listing_date = df.index[0]
            filter_date = pd.Timestamp(START_DATE_FILTER).tz_localize(listing_date.tz)
            
            # Filter Logic
            if listing_date < filter_date and ticker not in ["BSE.NS", "CDSL.NS"]:
                continue

            # Setup Period Logic
            cutoff_2024 = pd.Timestamp("2024-01-01").tz_localize(listing_date.tz)
            setup_days = 90 if listing_date >= cutoff_2024 else 250
            
            if len(df) < setup_days: continue

            setup_data = df.iloc[:setup_days]
            trading_data = df.iloc[setup_days:]
            
            if setup_data.empty or trading_data.empty: continue

            resistance = setup_data['High'].max()
            
            # Check Breakout
            breakout_mask = trading_data['Close'] > resistance
            breakouts = trading_data[breakout_mask]
            
            status = "NO ENTRY"
            entry_price = 0.0
            pnl_pct = 0.0
            pnl_rupees = 0.0
            entry_date = None
            
            if not breakouts.empty:
                first_entry = breakouts.iloc[0]
                entry_date = breakouts.index[0]
                entry_price = first_entry['Close']
                stop_loss = entry_price * 0.90
                
                post_entry = trading_data.loc[entry_date:][1:]
                cmp = df.iloc[-1]['Close']
                
                status = "PROFIT RUNNING"
                pnl_pct = ((cmp - entry_price) / entry_price) * 100
                
                if not post_entry.empty:
                    sl_hit = post_entry['Low'] < stop_loss
                    if sl_hit.any():
                        status = "SL HIT"
                        pnl_pct = -10.0 
                
                pnl_rupees = (pnl_pct / 100) * CAPITAL_PER_TRADE
                
                # --- TELEGRAM ALERT LOGIC ---
                if enable_alerts and status == "PROFIT RUNNING":
                    # Check Freshness: Kya entry pichle 3 din me hui hai?
                    # BSE/CDSL ke liye alert nahi bajega, sirf naye stocks ke liye.
                    current_time = pd.Timestamp.now().tz_localize(entry_date.tz)
                    days_since_entry = (current_time - entry_date).days
                    
                    if days_since_entry <= 3:
                        send_telegram_alert(ticker, round(entry_price, 2), round(resistance, 2), round(stop_loss, 2), "Fresh Breakout")
                        alerts_sent_count += 1
                
                results.append({
                    "Stock": ticker,
                    "List Date": listing_date.strftime('%Y-%m-%d'),
                    "Status": status,
                    "Entry Date": entry_date.strftime('%Y-%m-%d'),
                    "Entry Price": round(entry_price, 2),
                    "CMP": round(cmp, 2),
                    "Return %": round(pnl_pct, 2),
                    "P&L (Rs)": round(pnl_rupees, 2)
                })

        except Exception:
            continue
            
    return pd.DataFrame(results), alerts_sent_count