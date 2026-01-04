# ... (Previous imports)
# ipo_scanner se import
from ipo_scanner import run_ipo_scan

# ... (Previous code)

# --- PAGE 2: NEW IPO SCANNER ---
elif page == "IPO Strategy Scanner":
    st.header("🆕 IPO Breakout Strategy (Multibagger Finder)")
    
    # ... (Description text) ...
    
    col1, col2 = st.columns([2, 4])
    
    with col1:
        # Checkbox for Telegram
        send_telegram = st.checkbox("🔔 Send Alerts to Telegram (Fresh Only)")
        
        if st.button("🚀 Run Scan Now"):
            st.info("Scanning Market... Please wait (takes 2-3 mins)")
            
            my_bar = st.progress(0, text="Starting scan...")
            
            # --- UPDATED CALL WITH ALERTS ---
            df_results, alerts_count = run_ipo_scan(progress_bar=my_bar, enable_alerts=send_telegram)
            
            my_bar.empty()
            
            if not df_results.empty:
                st.session_state['ipo_data'] = df_results
                st.success("Scan Complete!")
                
                # Show Alert Status
                if send_telegram:
                    if alerts_count > 0:
                        st.toast(f"✅ Sent {alerts_count} Alerts to Telegram!", icon="🚀")
                    else:
                        st.info("No fresh breakouts found today (No alerts sent).")
            else:
                st.warning("No stocks found matching criteria.")

    # ... (Baaki ka Table display code same rahega) ...