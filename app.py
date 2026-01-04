import streamlit as st
import pandas as pd
# Apni IPO logic file import karein
from ipo_scanner import run_ipo_scan 

# Page Config (Ye sabse pehli line honi chahiye)
st.set_page_config(page_title="My Trading Dashboard", layout="wide")

# Sidebar Navigation (Menu)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Old Scanner", "IPO Strategy Scanner"])

# ==========================================
# PAGE 1: AAPKA PURANA SCANNER
# ==========================================
if page == "Old Scanner":
    st.header("My Existing Scanner")
    
    # ----------------------------------------
    # YAHAN APNA PURANA CODE PASTE KAREIN
    # ----------------------------------------
    st.write("Aapka purana scanner yahan dikhega.") 
    # Example:
    # df = load_my_data()
    # st.dataframe(df)


# ==========================================
# PAGE 2: NAYA IPO SCANNER
# ==========================================
elif page == "IPO Strategy Scanner":
    st.header("🆕 IPO Breakout Strategy (Multibagger Finder)")
    
    st.markdown("""
    **Strategy Rules:**
    1. Wait for 3-10 Months Setup.
    2. Buy on Resistance Breakout.
    3. Stop Loss: Fixed 10%.
    4. Target: Open (Ride the trend).
    """)
    
    col1, col2 = st.columns([2, 4])
    
    with col1:
        # Checkbox for Telegram
        send_telegram = st.checkbox("🔔 Send Alerts to Telegram (Fresh Only)")
        
        if st.button("🚀 Run Scan Now"):
            st.info("Scanning Market... Please wait (takes 2-3 mins)")
            
            my_bar = st.progress(0, text="Starting scan...")
            
            # Run Logic
            try:
                df_results, alerts_count = run_ipo_scan(progress_bar=my_bar, enable_alerts=send_telegram)
                
                my_bar.empty()
                
                if not df_results.empty:
                    st.session_state['ipo_data'] = df_results
                    st.success("Scan Complete!")
                    
                    if send_telegram:
                        if alerts_count > 0:
                            st.toast(f"✅ Sent {alerts_count} Alerts to Telegram!", icon="🚀")
                        else:
                            st.info("No fresh breakouts found today.")
                else:
                    st.warning("No stocks found matching criteria.")
            except Exception as e:
                st.error(f"Error running scan: {e}")

    # Results Display
    if 'ipo_data' in st.session_state:
        df = st.session_state['ipo_data']
        
        total_pnl = df['P&L (Rs)'].sum()
        winners = len(df[df['Return %'] > 0])
        total_trades = len(df)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Net P&L", f"₹ {total_pnl:,.2f}")
        m2.metric("Win Rate", f"{round((winners/total_trades)*100, 1)}%")
        m3.metric("Total Active Trades", total_trades)
        
        st.divider()
        
        def highlight_status(val):
            color = 'green' if 'PROFIT' in val else 'red'
            return f'color: {color}; font-weight: bold'

        st.subheader("Scanner Results")
        st.dataframe(
            df.style.map(highlight_status, subset=['Status'])
                    .format({"Return %": "{:.2f}%", "P&L (Rs)": "₹ {:.2f}"}),
            use_container_width=True,
            height=600
        )
