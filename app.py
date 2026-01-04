import streamlit as st
import pandas as pd
from ipo_scanner import run_ipo_scan 

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="My Trading Dashboard", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home / Dashboard", "IPO Strategy Scanner"])

# ==========================================
# PAGE 1: HOME PAGE (Placeholder)
# ==========================================
if page == "Home / Dashboard":
    st.header("🏠 My Trading Dashboard")
    st.write("Welcome to your trading tools.")
    st.info("👈 Select 'IPO Strategy Scanner' from the sidebar to start scanning.")
    
    # AGAR AAPKE PAAS PURANA CODE HAI TO USE ISKE NICHE PASTE KAREIN
    # Example:
    # st.write("My old scanner code results...")


# ==========================================
# PAGE 2: IPO SCANNER (FULL WORKING CODE)
# ==========================================
elif page == "IPO Strategy Scanner":
    st.header("🆕 IPO Breakout Strategy (Multibagger Finder)")
    
    with st.expander("ℹ️ Strategy Rules (Click to Expand)"):
        st.markdown("""
        1. **Wait Phase:** Stock consolidates for 3-10 months after Listing.
        2. **Breakout:** Buy when Price crosses the Highest High of the Wait Phase.
        3. **Stop Loss:** Fixed 10% below Entry Price.
        4. **Target:** Open (Ride the trend for Multibaggers).
        """)
    
    col1, col2 = st.columns([2, 5])
    
    with col1:
        st.subheader("Controls")
        # Checkbox for Telegram
        send_telegram = st.checkbox("🔔 Send Alerts to Telegram (Fresh Only)", value=False)
        
        if st.button("🚀 Run Scan Now", use_container_width=True):
            st.info("Scanning Market... Please wait (2-3 mins)")
            
            my_bar = st.progress(0, text="Starting scan...")
            
            try:
                # Logic File ko call kar rahe hain
                df_results, alerts_count = run_ipo_scan(progress_bar=my_bar, enable_alerts=send_telegram)
                
                my_bar.empty()
                
                if not df_results.empty:
                    st.session_state['ipo_data'] = df_results
                    st.success("Scan Complete!")
                    
                    if send_telegram:
                        if alerts_count > 0:
                            st.toast(f"✅ Sent {alerts_count} Alerts!", icon="🚀")
                            st.success(f"Sent {alerts_count} alerts to Telegram.")
                        else:
                            st.info("No fresh breakouts found today (Last 3 days).")
                else:
                    st.warning("No stocks found matching criteria.")
            except Exception as e:
                st.error(f"Error: {e}")

    # Results Display
    if 'ipo_data' in st.session_state:
        df = st.session_state['ipo_data']
        
        total_pnl = df['P&L (Rs)'].sum()
        winners = len(df[df['Return %'] > 0])
        total_trades = len(df)
        win_rate = (winners/total_trades)*100 if total_trades > 0 else 0
        
        st.divider()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Net P&L", f"₹ {total_pnl:,.2f}")
        m2.metric("Win Rate", f"{round(win_rate, 1)}%")
        m3.metric("Total Active Trades", total_trades)
        
        def highlight_status(val):
            color = 'green' if 'PROFIT' in val else 'red'
            return f'color: {color}; font-weight: bold'

        st.subheader("Scanner Results")
        st.dataframe(
            df.style.map(highlight_status, subset=['Status'])
                    .format({"Return %": "{:.2f}%", "P&L (Rs)": "₹ {:.2f}", "Entry Price": "₹ {:.2f}", "CMP": "₹ {:.2f}"}),
            use_container_width=True,
            height=600
        )
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name="ipo_report.csv", mime="text/csv")
