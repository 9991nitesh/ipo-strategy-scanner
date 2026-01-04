import streamlit as st
import pandas as pd
from ipo_scanner import run_ipo_scan 

# 1. Page Config sabse pehle aana chahiye
st.set_page_config(page_title="My Trading Dashboard", layout="wide")

# 2. Sidebar Setup
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page:", ["Home Page", "IPO Strategy Scanner"])

# ==========================================
# PAGE 1: HOME PAGE
# ==========================================
if page == "Home Page":
    st.header("🏠 Welcome to Dashboard")
    st.write("Ye aapka Home Page hai.")
    st.info("👈 Left Sidebar se 'IPO Strategy Scanner' select karein.")
    
    # Jab code chal jaye, tab aap yahan apna purana scanner paste kar sakte hain.
    # Filhal ise khali rehne dein taaki koi error na aaye.

# ==========================================
# PAGE 2: IPO SCANNER
# ==========================================
elif page == "IPO Strategy Scanner":
    st.header("🆕 IPO Breakout Scanner")
    
    col1, col2 = st.columns([2, 5])
    
    with col1:
        st.subheader("Controls")
        send_telegram = st.checkbox("🔔 Send Telegram Alerts", value=False)
        
        if st.button("🚀 Run Scan Now"):
            st.info("Scanning Market... (Wait 2 mins)")
            my_bar = st.progress(0, text="Starting...")
            
            try:
                # Logic call kar rahe hain
                df_results, alerts_count = run_ipo_scan(progress_bar=my_bar, enable_alerts=send_telegram)
                my_bar.empty()
                
                if not df_results.empty:
                    st.session_state['ipo_data'] = df_results
                    st.success("Done!")
                    if send_telegram and alerts_count > 0:
                        st.success(f"Sent {alerts_count} alerts!")
                else:
                    st.warning("No stocks found.")
            except Exception as e:
                st.error(f"Error: {e}")

    # Display Results
    if 'ipo_data' in st.session_state:
        df = st.session_state['ipo_data']
        
        # Metrics
        total_pnl = df['P&L (Rs)'].sum()
        winners = len(df[df['Return %'] > 0])
        
        st.divider()
        m1, m2 = st.columns(2)
        m1.metric("Total P&L", f"₹ {total_pnl:,.2f}")
        m2.metric("Winning Trades", winners)
        
        # Table Styling
        def highlight(val):
            return 'color: green; font-weight: bold' if 'PROFIT' in val else 'color: red'

        st.dataframe(
            df.style.map(highlight, subset=['Status'])
              .format({"Return %": "{:.2f}%", "P&L (Rs)": "₹ {:.2f}"}),
            use_container_width=True,
            height=600
        )