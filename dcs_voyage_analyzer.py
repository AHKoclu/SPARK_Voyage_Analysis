import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
import tempfile
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="SPARK Voyage Analyzer", layout="wide", page_icon="📈")

# --- 2. SIDEBAR: VESSEL INFO ---
st.sidebar.image("https://iili.io/CBuH8kg.png", use_container_width=True)
st.sidebar.header("🚢 Vessel & Voyage Info")
vessel_name = st.sidebar.text_input("Vessel Name", "M/V Master Charterer")
voyage_num = st.sidebar.text_input("Voyage Number", "Voy-2026-05")
fleet_name = st.sidebar.text_input("Fleet Name", "SPARK Fleet")
st.sidebar.divider()

# --- 3. MAIN HEADER ---
st.title("📈 Post-Voyage Performance & Cost Analyzer")
st.markdown("*Compare Chartering Pre-Voyage Estimations and Costs against Actual End-of-Voyage Data.*")
st.divider()

# --- 4. INPUT SECTION (ESTIMATED VS ACTUAL) ---
st.subheader("📝 Data Entry")

col_est, col_act = st.columns(2)

with col_est:
    st.markdown("### 🔵 Pre-Voyage Estimation")
    
    st.markdown("#### 1. Cargo & Weather")
    est_cargo = st.number_input("Cargo Quantity (MT) [Est]", value=55000.0, step=1000.0)
    est_weather = st.number_input("Weather Factor (%) [Est]", value=15.0, step=1.0)
    
    st.markdown("#### 2. Fuel Unit Prices ($/MT)")
    est_fo_price = st.number_input("FO Unit Price ($/MT) [Est]", value=600.0, step=10.0)
    est_do_price = st.number_input("DO Unit Price ($/MT) [Est]", value=850.0, step=10.0)
    
    st.markdown("#### 3. Navigation (Dist & Speed)")
    est_bal_dist = st.number_input("Ballast Distance (NM) [Est]", value=1200.0, step=100.0)
    est_lad_dist = st.number_input("Laden Distance (NM) [Est]", value=4500.0, step=100.0)
    est_bal_spd = st.number_input("Ballast Speed (Knot) [Est]", value=12.5, step=0.5)
    est_lad_spd = st.number_input("Laden Speed (Knot) [Est]", value=11.5, step=0.5)
    
    st.markdown("#### 4. Time (Days)")
    est_sea_days = st.number_input("Sea Days (Days) [Est]", value=10.0, step=0.5)
    est_work_days = st.number_input("Work Days (Days) [Est]", value=2.0, step=0.5)
    est_idle_days = st.number_input("Idle Days (Days) [Est]", value=7.0, step=0.5)
    
    st.markdown("#### 5. Total Fuel Consumptions (MT)")
    est_tot_fo = st.number_input("Total FO [Est]", value=370.0, step=10.0)
    est_tot_do = st.number_input("Total DO [Est]", value=40.0, step=5.0)

    st.markdown("#### 6. Efficiency KPI Inputs")
    est_lad_mt_day = st.number_input("Laden Cons. (MT/Day) [Est]", value=26.0, step=0.5)
    est_bal_mt_day = st.number_input("Ballast Cons. (MT/Day) [Est]", value=24.0, step=0.5)
    est_work_fuel = st.number_input("Work Total Cons. (MT) [Est]", value=50.0, step=1.0)
    est_idle_fuel = st.number_input("Idle Total Cons. (MT) [Est]", value=28.0, step=1.0)

with col_act:
    st.markdown("### 🔴 End-of-Voyage Actual")
    
    st.markdown("#### 1. Cargo & Weather")
    act_cargo = st.number_input("Cargo Quantity (MT) [Act]", value=54800.0, step=1000.0)
    act_weather = st.number_input("Weather Factor (%) [Act]", value=18.0, step=1.0)
    
    st.markdown("#### 2. Fuel Unit Prices ($/MT)")
    act_fo_price = st.number_input("FO Unit Price ($/MT) [Act]", value=620.0, step=10.0)
    act_do_price = st.number_input("DO Unit Price ($/MT) [Act]", value=840.0, step=10.0)
    
    st.markdown("#### 3. Navigation (Dist & Speed)")
    act_bal_dist = st.number_input("Ballast Distance (NM) [Act]", value=1250.0, step=100.0)
    act_lad_dist = st.number_input("Laden Distance (NM) [Act]", value=4600.0, step=100.0)
    act_bal_spd = st.number_input("Ballast Speed (Knot) [Act]", value=12.0, step=0.5)
    act_lad_spd = st.number_input("Laden Speed (Knot) [Act]", value=11.0, step=0.5)
    
    st.markdown("#### 4. Time (Days)")
    act_sea_days = st.number_input("Sea Days (Days) [Act]", value=10.0, step=0.5)
    act_work_days = st.number_input("Work Days (Days) [Act]", value=3.0, step=0.5)
    act_idle_days = st.number_input("Idle Days (Days) [Act]", value=12.0, step=0.5)
    
    st.markdown("#### 5. Total Fuel Consumptions (MT)")
    act_tot_fo = st.number_input("Total FO [Act]", value=414.0, step=10.0)
    act_tot_do = st.number_input("Total DO [Act]", value=49.0, step=5.0)

    st.markdown("#### 6. Efficiency KPI Inputs")
    act_lad_mt_day = st.number_input("Laden Cons. (MT/Day) [Act]", value=22.0, step=0.5)
    act_bal_mt_day = st.number_input("Ballast Cons. (MT/Day) [Act]", value=20.0, step=0.5)
    act_work_fuel = st.number_input("Work Total Cons. (MT) [Act]", value=81.0, step=1.0)
    act_idle_fuel = st.number_input("Idle Total Cons. (MT) [Act]", value=36.0, step=1.0)

# --- 5. AUTOMATIC CALCULATIONS & COSTING ---
# Estimated Calculations & Costs
est_tot_dist = est_bal_dist + est_lad_dist
est_tot_days = est_sea_days + est_work_days + est_idle_days

est_fo_cost = est_tot_fo * est_fo_price
est_do_cost = est_tot_do * est_do_price
est_total_cost = est_fo_cost + est_do_cost

est_lad_mt_nm = est_lad_mt_day / est_lad_spd if est_lad_spd > 0 else 0
est_bal_mt_nm = est_bal_mt_day / est_bal_spd if est_bal_spd > 0 else 0
est_work_mt_day = est_work_fuel / est_work_days if est_work_days > 0 else 0
est_idle_mt_day = est_idle_fuel / est_idle_days if est_idle_days > 0 else 0

# Actual Calculations & Costs
act_tot_dist = act_bal_dist + act_lad_dist
act_tot_days = act_sea_days + act_work_days + act_idle_days

act_fo_cost = act_tot_fo * act_fo_price
act_do_cost = act_tot_do * act_do_price
act_total_cost = act_fo_cost + act_do_cost

act_lad_mt_nm = act_lad_mt_day / act_lad_spd if act_lad_spd > 0 else 0
act_bal_mt_nm = act_bal_mt_day / act_bal_spd if act_bal_spd > 0 else 0
act_work_mt_day = act_work_fuel / act_work_days if act_work_days > 0 else 0
act_idle_mt_day = act_idle_fuel / act_idle_days if act_idle_days > 0 else 0

# --- 6. DASHBOARD & VISUALIZATION ---
st.divider()
st.subheader("📊 Performance & Financial Dashboard")

# Row 1: Financial KPIs
f1, f2, f3 = st.columns(3)
f1.metric("Total Fuel Cost ($)", f"${act_total_cost:,.2f}", f"${act_total_cost - est_total_cost:+,.2f}", delta_color="inverse")
f2.metric("FO Total Cost ($)", f"${act_fo_cost:,.2f}", f"${act_fo_cost - est_fo_cost:+,.2f}", delta_color="inverse")
f3.metric("DO Total Cost ($)", f"${act_do_cost:,.2f}", f"${act_do_cost - est_do_cost:+,.2f}", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# Row 2: Operational KPIs
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Weather Factor (%)", f"{act_weather:.1f}%", f"{act_weather - est_weather:+.1f}%", delta_color="inverse")
m2.metric("Total Cargo (MT)", f"{act_cargo:,.0f}", f"{act_cargo - est_cargo:+,.0f} MT", delta_color="inverse")
m3.metric("Total Distance (NM)", f"{act_tot_dist:,.0f}", f"{act_tot_dist - est_tot_dist:+,.0f} NM", delta_color="inverse")
m4.metric("Total Voyage Days", f"{act_tot_days:.1f}", f"{act_tot_days - est_tot_days:+.1f} Days", delta_color="inverse")
m5.metric("Average Speed (Kts)", f"{(act_bal_spd + act_lad_spd)/2:.1f}", f"{((act_bal_spd + act_lad_spd)/2) - ((est_bal_spd + est_lad_spd)/2):+.1f} Kts", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("⚙️ Efficiency Metrics (MT/NM & MT/Day)")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Laden MT/NM", f"{act_lad_mt_nm:.4f}", f"{act_lad_mt_nm - est_lad_mt_nm:+.4f}", delta_color="inverse")
k2.metric("Ballast MT/NM", f"{act_bal_mt_nm:.4f}", f"{act_bal_mt_nm - est_bal_mt_nm:+.4f}", delta_color="inverse")
k3.metric("Work MT/Day", f"{act_work_mt_day:.2f}", f"{act_work_mt_day - est_work_mt_day:+.2f}", delta_color="inverse")
k4.metric("Idle MT/Day", f"{act_idle_mt_day:.2f}", f"{act_idle_mt_day - est_idle_mt_day:+.2f}", delta_color="inverse")

# Row 3: Charts (Plotly for Web View)
c1, c2, c3 = st.columns(3)

with c1:
    fig_cost = go.Figure(data=[
        go.Bar(name='Estimated', x=['Total Cost', 'FO Cost', 'DO Cost'], y=[est_total_cost, est_fo_cost, est_do_cost], marker_color='#9467bd'),
        go.Bar(name='Actual', x=['Total Cost', 'FO Cost', 'DO Cost'], y=[act_total_cost, act_fo_cost, act_do_cost], marker_color='#e377c2')
    ])
    fig_cost.update_layout(title="Financial Cost Comparison ($)", barmode='group', template='plotly_dark')
    st.plotly_chart(fig_cost, use_container_width=True)

with c2:
    fig_fuel = go.Figure(data=[
        go.Bar(name='Estimated', x=['Total FO', 'Total DO'], 
               y=[est_tot_fo, est_tot_do], marker_color='#1f77b4'),
        go.Bar(name='Actual', x=['Total FO', 'Total DO'], 
               y=[act_tot_fo, act_tot_do], marker_color='#d62728')
    ])
    fig_fuel.update_layout(title="Fuel Consumption Breakdown (MT)", barmode='group', template='plotly_dark')
    st.plotly_chart(fig_fuel, use_container_width=True)

with c3:
    fig_time = go.Figure(data=[
        go.Bar(name='Estimated', x=['Total Days', 'Sea Days', 'Work Days', 'Idle Days'], 
               y=[est_tot_days, est_sea_days, est_work_days, est_idle_days], marker_color='#2ca02c'),
        go.Bar(name='Actual', x=['Total Days', 'Sea Days', 'Work Days', 'Idle Days'], 
               y=[act_tot_days, act_sea_days, act_work_days, act_idle_days], marker_color='#ff7f0e')
    ])
    fig_time.update_layout(title="Time & Duration Breakdown (Days)", barmode='group', template='plotly_dark')
    st.plotly_chart(fig_time, use_container_width=True)

c4, c5 = st.columns(2)

with c4:
    fig_eff_sea = go.Figure(data=[
        go.Bar(name='Estimated', x=['Laden MT/NM', 'Ballast MT/NM'], y=[est_lad_mt_nm, est_bal_mt_nm], marker_color='#17becf'),
        go.Bar(name='Actual', x=['Laden MT/NM', 'Ballast MT/NM'], y=[act_lad_mt_nm, act_bal_mt_nm], marker_color='#bcbd22')
    ])
    fig_eff_sea.update_layout(title="Sea Efficiency (MT/NM)", barmode='group', template='plotly_dark')
    st.plotly_chart(fig_eff_sea, use_container_width=True)

with c5:
    fig_eff_port = go.Figure(data=[
        go.Bar(name='Estimated', x=['Work MT/Day', 'Idle MT/Day'], y=[est_work_mt_day, est_idle_mt_day], marker_color='#17becf'),
        go.Bar(name='Actual', x=['Work MT/Day', 'Idle MT/Day'], y=[act_work_mt_day, act_idle_mt_day], marker_color='#bcbd22')
    ])
    fig_eff_port.update_layout(title="Port Efficiency (MT/Day)", barmode='group', template='plotly_dark')
    st.plotly_chart(fig_eff_port, use_container_width=True)

# --- ENERGY DEPARTMENT COMMENT SECTION ---
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("✍️ Energy Department Comment")
energy_comment = st.text_area("Enter your analysis and comments here (This will be printed in the PDF report):", height=120)

# --- 7. PDF REPORT GENERATOR ---
def generate_voyage_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(190, 10, "Post-Voyage Performance & Cost Analysis", ln=True, align='C')
    pdf.ln(5)
    
    # 2. Vessel & Voyage Info
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, f"Vessel Name: {vessel_name}", ln=True)
    pdf.cell(190, 8, f"Voyage Number: {voyage_num}", ln=True)
    pdf.cell(190, 8, f"Fleet: {fleet_name}", ln=True)
    
    current_y = pdf.get_y() + 2
    pdf.line(10, current_y, 200, current_y)
    pdf.set_y(current_y + 5)
    
    # 3. Data Table
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 8, "Parameter", 1)
    pdf.cell(40, 8, "Estimated", 1)
    pdf.cell(40, 8, "Actual", 1)
    pdf.cell(40, 8, "Difference", 1, ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    
    def add_row(param, est, act, unit, is_currency=False, is_precision=False):
        diff = act - est
        if is_currency:
            est_str = f"${est:,.2f}"
            act_str = f"${act:,.2f}"
            diff_str = f"${diff:+,.2f}"
        elif is_precision:
            est_str = f"{est:,.4f} {unit}"
            act_str = f"{act:,.4f} {unit}"
            diff_str = f"{diff:+.4f} {unit}"
        else:
            est_str = f"{est:,.1f} {unit}"
            act_str = f"{act:,.1f} {unit}"
            diff_str = f"{diff:+.1f} {unit}"
            
        pdf.cell(50, 8, param, 1)
        pdf.cell(40, 8, est_str, 1)
        pdf.cell(40, 8, act_str, 1)
        
        # Fark (Difference) Hucresini Renklendirme
        fill = False
        if diff > 0.0001:
            pdf.set_fill_color(255, 204, 204) # Soft Red
            pdf.set_text_color(180, 0, 0)     # Dark Red Text
            fill = True
        elif diff < -0.0001:
            pdf.set_fill_color(204, 255, 204) # Soft Green
            pdf.set_text_color(0, 100, 0)     # Dark Green Text
            fill = True
            
        pdf.cell(40, 8, diff_str, 1, ln=True, fill=fill)
        pdf.set_text_color(0, 0, 0) # Rengi normale dondur

    add_row("Total Fuel Cost", est_total_cost, act_total_cost, "", is_currency=True)
    add_row("FO Total Cost", est_fo_cost, act_fo_cost, "", is_currency=True)
    add_row("DO Total Cost", est_do_cost, act_do_cost, "", is_currency=True)
    add_row("FO Unit Price", est_fo_price, act_fo_price, "$/MT")
    add_row("DO Unit Price", est_do_price, act_do_price, "$/MT")
    add_row("Weather Factor", est_weather, act_weather, "%")
    add_row("Cargo Quantity", est_cargo, act_cargo, "MT")
    add_row("Total Distance", est_tot_dist, act_tot_dist, "NM")
    add_row("Total Voyage Days", est_tot_days, act_tot_days, "Days")
    add_row("Sea Days", est_sea_days, act_sea_days, "Days")
    add_row("Work Days", est_work_days, act_work_days, "Days")
    add_row("Idle Days", est_idle_days, act_idle_days, "Days")
    add_row("Total FO Cons", est_tot_fo, act_tot_fo, "MT")
    add_row("Total DO Cons", est_tot_do, act_tot_do, "MT")
    add_row("Laden Efficiency", est_lad_mt_nm, act_lad_mt_nm, "MT/NM", is_precision=True)
    add_row("Ballast Efficiency", est_bal_mt_nm, act_bal_mt_nm, "MT/NM", is_precision=True)
    add_row("Work Rate", est_work_mt_day, act_work_mt_day, "MT/Day")
    add_row("Idle Rate", est_idle_mt_day, act_idle_mt_day, "MT/Day")
    pdf.ln(10)
    
    # 4. EXACT Dashboard Charts via Matplotlib
    pdf.add_page() # Force new page for charts
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(190, 10, "Visual Performance & Cost Charts", ln=True)
    pdf.ln(5)
    
    try:
        tmp_dir = tempfile.gettempdir()
        cost_img_path = os.path.join(tmp_dir, "cost_chart_mp.png")
        fuel_img_path = os.path.join(tmp_dir, "fuel_chart_mp.png")
        time_img_path = os.path.join(tmp_dir, "time_chart_mp.png")
        eff_sea_img_path = os.path.join(tmp_dir, "eff_sea_chart_mp.png")
        eff_port_img_path = os.path.join(tmp_dir, "eff_port_chart_mp.png")
        
        width = 0.35
        
        # --- Create Cost Chart ---
        labels_cost = ['Total Cost', 'FO Cost', 'DO Cost']
        est_cost_vals = [est_total_cost, est_fo_cost, est_do_cost]
        act_cost_vals = [act_total_cost, act_fo_cost, act_do_cost]
        x_cost = np.arange(len(labels_cost))
        
        fig0, ax0 = plt.subplots(figsize=(10, 4))
        ax0.bar(x_cost - width/2, est_cost_vals, width, label='Estimated', color='#9467bd')
        ax0.bar(x_cost + width/2, act_cost_vals, width, label='Actual', color='#e377c2')
        ax0.set_ylabel('Cost ($)')
        ax0.set_title('Financial Cost Comparison ($)')
        ax0.set_xticks(x_cost)
        ax0.set_xticklabels(labels_cost)
        ax0.legend()
        plt.tight_layout()
        plt.savefig(cost_img_path, format='png', dpi=150)
        plt.close(fig0)
        
        # --- Create Fuel Chart ---
        labels_fuel = ['Total FO', 'Total DO']
        est_fuel_vals = [est_tot_fo, est_tot_do]
        act_fuel_vals = [act_tot_fo, act_tot_do]
        x_fuel = np.arange(len(labels_fuel))
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(x_fuel - width/2, est_fuel_vals, width, label='Estimated', color='#1f77b4')
        ax.bar(x_fuel + width/2, act_fuel_vals, width, label='Actual', color='#d62728')
        ax.set_ylabel('Consumption (MT)')
        ax.set_title('Fuel Consumption Breakdown (MT)')
        ax.set_xticks(x_fuel)
        ax.set_xticklabels(labels_fuel)
        ax.legend()
        plt.tight_layout()
        plt.savefig(fuel_img_path, format='png', dpi=150)
        plt.close(fig)
        
        # --- Create Time Chart ---
        labels_time = ['Total Days', 'Sea Days', 'Work Days', 'Idle Days']
        est_time_vals = [est_tot_days, est_sea_days, est_work_days, est_idle_days]
        act_time_vals = [act_tot_days, act_sea_days, act_work_days, act_idle_days]
        x_time = np.arange(len(labels_time))
        
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        ax2.bar(x_time - width/2, est_time_vals, width, label='Estimated', color='#2ca02c')
        ax2.bar(x_time + width/2, act_time_vals, width, label='Actual', color='#ff7f0e')
        ax2.set_ylabel('Duration (Days)')
        ax2.set_title('Time & Duration Breakdown (Days)')
        ax2.set_xticks(x_time)
        ax2.set_xticklabels(labels_time)
        ax2.legend()
        plt.tight_layout()
        plt.savefig(time_img_path, format='png', dpi=150)
        plt.close(fig2)

        # --- Create Sea Efficiency Chart ---
        labels_eff_sea = ['Laden MT/NM', 'Ballast MT/NM']
        est_eff_sea = [est_lad_mt_nm, est_bal_mt_nm]
        act_eff_sea = [act_lad_mt_nm, act_bal_mt_nm]
        x_eff_sea = np.arange(len(labels_eff_sea))
        
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        ax3.bar(x_eff_sea - width/2, est_eff_sea, width, label='Estimated', color='#2ca02c')
        ax3.bar(x_eff_sea + width/2, act_eff_sea, width, label='Actual', color='#cf1746')
        ax3.set_ylabel('MT / NM')
        ax3.set_title('Sea Efficiency (MT/NM)')
        ax3.set_xticks(x_eff_sea)
        ax3.set_xticklabels(labels_eff_sea)
        ax3.legend()
        plt.tight_layout()
        plt.savefig(eff_sea_img_path, format='png', dpi=150)
        plt.close(fig3)
        
        # --- Create Port Efficiency Chart ---
        labels_eff_port = ['Work MT/Day', 'Idle MT/Day']
        est_eff_port = [est_work_mt_day, est_idle_mt_day]
        act_eff_port = [act_work_mt_day, act_idle_mt_day]
        x_eff_port = np.arange(len(labels_eff_port))
        
        fig4, ax4 = plt.subplots(figsize=(10, 4))
        ax4.bar(x_eff_port - width/2, est_eff_port, width, label='Estimated', color='#2ca02c')
        ax4.bar(x_eff_port + width/2, act_eff_port, width, label='Actual', color='#cf1746')
        ax4.set_ylabel('MT / Day')
        ax4.set_title('Port Efficiency (MT/Day)')
        ax4.set_xticks(x_eff_port)
        ax4.set_xticklabels(labels_eff_port)
        ax4.legend()
        plt.tight_layout()
        plt.savefig(eff_port_img_path, format='png', dpi=150)
        plt.close(fig4)
        
        # Add all generated charts into PDF layout dynamically
        current_y = pdf.get_y()
        
        # Page 2: Cost and Fuel
        pdf.image(cost_img_path, x=10, y=current_y, w=190)
        pdf.image(fuel_img_path, x=10, y=current_y + 110, w=190)
        
        # Page 3: Time and Sea Efficiency
        pdf.add_page()
        pdf.image(time_img_path, x=10, y=20, w=190)
        pdf.image(eff_sea_img_path, x=10, y=130, w=190)
        
        # Page 4: Port Efficiency
        pdf.add_page()
        pdf.image(eff_port_img_path, x=10, y=20, w=190)
        
    except Exception as e:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(255, 0, 0)
        pdf.cell(190, 10, "CHART GENERATION ERROR!", ln=True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(190, 8, f"Details: {str(e)}")

    # --- NEW: ENERGY DEPARTMENT COMMENT IN PDF ---
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(190, 10, "Energy Department Analysis Comment", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 11)
    
    # Turkce karakterleri ingilizceye cevir (PDF cokerse diye guvenlik onlemi)
    comment_text = energy_comment
    mapping = {"ç": "c", "Ç": "C", "ğ": "g", "Ğ": "G", "ı": "i", "İ": "I",
               "ö": "o", "Ö": "O", "ş": "s", "Ş": "S", "ü": "u", "Ü": "U",
               "’": "'", "‘": "'", "”": "\"", "“": "\"", "–": "-", "—": "-"}
    for k, v in mapping.items():
        comment_text = str(comment_text).replace(k, v)
        
    if not comment_text.strip():
        comment_text = "No additional comments provided for this voyage."
        
    pdf.multi_cell(190, 8, comment_text)

    # Footer (Sayfanin en altina hizala)
    if pdf.get_y() > 250:
        pdf.add_page()

    pdf.set_y(260)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(190, 5, "* This report is generated electronically by the SPARK Performance Simulator.", ln=True)
    
    tmp_path = os.path.join(tempfile.gettempdir(), "Voyage_Analyzer_Report.pdf")
    pdf.output(tmp_path)
    with open(tmp_path, "rb") as f:
        data = f.read()
    return data

# --- 8. DOWNLOAD BUTTON & SIGNATURE ---
st.sidebar.header("📥 Reporting")
if st.sidebar.button("📄 Download PDF Report", type="primary"):
    pdf_bytes = generate_voyage_pdf()
    file_name = f"{vessel_name.replace(' ', '_')}_{voyage_num}_Financial_Analysis.pdf"
    st.sidebar.download_button(
        label="💾 Save Report", 
        data=pdf_bytes, 
        file_name=file_name, 
        mime="application/pdf"
    )
    st.sidebar.success("✅ PDF is ready!")

# --- CAFCAFALİ ENERJİ DEPARTMANI İMZASI ---
st.sidebar.markdown("<br><br><br><br>", unsafe_allow_html=True)
st.sidebar.markdown(
    """
    <div style='text-align: center; border-top: 1px solid #444; padding-top: 15px;'>
        <p style='font-family: "Courier New", Courier, monospace; font-size: 14px; font-weight: bold; color: #FF0033; letter-spacing: 1px; margin-bottom: 2px;'>
            ⚡ Chartering Simulator ⚡
        </p>
        <p style='font-style: italic; font-size: 13px; color: #888888; font-family: "Georgia", serif;'>
            Developed by Energy Department
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)
