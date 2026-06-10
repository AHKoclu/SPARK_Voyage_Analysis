import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import tempfile
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="SPARK Voyage Analyzer", layout="wide", page_icon="📈")

# --- 2. SIDEBAR: VESSEL INFO ---
st.sidebar.header("🚢 Vessel & Voyage Info")
vessel_name = st.sidebar.text_input("Vessel Name", "M/V Beks")
voyage_num = st.sidebar.text_input("Voyage Number", "Voy-2026-05")
fleet_name = st.sidebar.text_input("Fleet Name", "SPARK Fleet")
st.sidebar.divider()

# --- 3. MAIN HEADER ---
st.title("📈 Post-Voyage Performance Analyzer")
st.markdown("*Compare Chartering Pre-Voyage Estimations against Actual End-of-Voyage Data.*")
st.divider()

# --- 4. INPUT SECTION (ESTIMATED VS ACTUAL) ---
st.subheader("📝 Data Entry")

col_est, col_act = st.columns(2)

with col_est:
    st.markdown("### 🔵 Pre-Voyage Estimation")
    
    st.markdown("#### 1. Cargo & Weather")
    est_cargo = st.number_input("Cargo Quantity (MT) [Est]", value=55000.0, step=1000.0)
    est_weather = st.number_input("Weather Factor (%) [Est]", value=15.0, step=1.0)
    
    st.markdown("#### 2. Navigation (Dist & Speed)")
    est_bal_dist = st.number_input("Ballast Distance (NM) [Est]", value=1200.0, step=100.0)
    est_lad_dist = st.number_input("Laden Distance (NM) [Est]", value=4500.0, step=100.0)
    est_bal_spd = st.number_input("Ballast Speed (Knot) [Est]", value=12.5, step=0.5)
    est_lad_spd = st.number_input("Laden Speed (Knot) [Est]", value=11.5, step=0.5)
    
    st.markdown("#### 3. Time (Days)")
    est_work_days = st.number_input("Work Days (Days) [Est]", value=4.0, step=0.5)
    est_idle_days = st.number_input("Idle Days (Days) [Est]", value=1.0, step=0.5)
    
    st.markdown("#### 4. Fuel Consumptions (MT)")
    est_fo_sea = st.number_input("FO Sea [Est]", value=350.0, step=10.0)
    est_fo_work = st.number_input("FO Work [Est]", value=15.0, step=5.0)
    est_fo_idle = st.number_input("FO Idle [Est]", value=5.0, step=1.0)
    
    est_do_sea = st.number_input("DO Sea [Est]", value=15.0, step=5.0)
    est_do_work = st.number_input("DO Work [Est]", value=20.0, step=5.0)
    est_do_idle = st.number_input("DO Idle [Est]", value=5.0, step=1.0)

with col_act:
    st.markdown("### 🔴 End-of-Voyage Actual")
    
    st.markdown("#### 1. Cargo & Weather")
    act_cargo = st.number_input("Cargo Quantity (MT) [Act]", value=54800.0, step=1000.0)
    act_weather = st.number_input("Weather Factor (%) [Act]", value=18.0, step=1.0)
    
    st.markdown("#### 2. Navigation (Dist & Speed)")
    act_bal_dist = st.number_input("Ballast Distance (NM) [Act]", value=1250.0, step=100.0)
    act_lad_dist = st.number_input("Laden Distance (NM) [Act]", value=4600.0, step=100.0)
    act_bal_spd = st.number_input("Ballast Speed (Knot) [Act]", value=12.0, step=0.5)
    act_lad_spd = st.number_input("Laden Speed (Knot) [Act]", value=11.0, step=0.5)
    
    st.markdown("#### 3. Time (Days)")
    act_work_days = st.number_input("Work Days (Days) [Act]", value=4.5, step=0.5)
    act_idle_days = st.number_input("Idle Days (Days) [Act]", value=2.0, step=0.5)
    
    st.markdown("#### 4. Fuel Consumptions (MT)")
    act_fo_sea = st.number_input("FO Sea [Act]", value=385.0, step=10.0)
    act_fo_work = st.number_input("FO Work [Act]", value=18.0, step=5.0)
    act_fo_idle = st.number_input("FO Idle [Act]", value=11.0, step=1.0)
    
    act_do_sea = st.number_input("DO Sea [Act]", value=16.5, step=5.0)
    act_do_work = st.number_input("DO Work [Act]", value=22.5, step=5.0)
    act_do_idle = st.number_input("DO Idle [Act]", value=10.0, step=1.0)

# --- 5. AUTOMATIC CALCULATIONS ---
# Estimated Calculations
est_tot_dist = est_bal_dist + est_lad_dist
est_sea_days = (est_bal_dist / (est_bal_spd * 24) if est_bal_spd > 0 else 0) + (est_lad_dist / (est_lad_spd * 24) if est_lad_spd > 0 else 0)
est_tot_days = est_sea_days + est_work_days + est_idle_days
est_tot_fo = est_fo_sea + est_fo_work + est_fo_idle
est_tot_do = est_do_sea + est_do_work + est_do_idle

# Actual Calculations
act_tot_dist = act_bal_dist + act_lad_dist
act_sea_days = (act_bal_dist / (act_bal_spd * 24) if act_bal_spd > 0 else 0) + (act_lad_dist / (act_lad_spd * 24) if act_lad_spd > 0 else 0)
act_tot_days = act_sea_days + act_work_days + act_idle_days
act_tot_fo = act_fo_sea + act_fo_work + act_fo_idle
act_tot_do = act_do_sea + act_do_work + act_do_idle

# --- 6. DASHBOARD & VISUALIZATION ---
st.divider()
st.subheader("📊 Performance Dashboard")

# Row 1: Key Metrics
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Weather Factor (%)", f"{act_weather:.1f}%", f"{act_weather - est_weather:+.1f}%", delta_color="inverse")
m2.metric("Total Cargo (MT)", f"{act_cargo:,.0f}", f"{act_cargo - est_cargo:+,.0f} MT", delta_color="normal")
m3.metric("Total Distance (NM)", f"{act_tot_dist:,.0f}", f"{act_tot_dist - est_tot_dist:+,.0f} NM", delta_color="inverse")
m4.metric("Total Voyage Days", f"{act_tot_days:.1f}", f"{act_tot_days - est_tot_days:+.1f} Days", delta_color="inverse")
m5.metric("Average Speed (Kts)", f"{(act_bal_spd + act_lad_spd)/2:.1f}", f"{((act_bal_spd + act_lad_spd)/2) - ((est_bal_spd + est_lad_spd)/2):+.1f} Kts", delta_color="normal")

st.markdown("<br>", unsafe_allow_html=True)
m6, m7, m8, m9, m10 = st.columns(5)
m6.metric("Total FO Cons (MT)", f"{act_tot_fo:.1f}", f"{act_tot_fo - est_tot_fo:+.1f} MT", delta_color="inverse")
m7.metric("Total DO Cons (MT)", f"{act_tot_do:.1f}", f"{act_tot_do - est_tot_do:+.1f} MT", delta_color="inverse")
m8.metric("Sea Days", f"{act_sea_days:.1f}", f"{act_sea_days - est_sea_days:+.1f} Days", delta_color="inverse")
m9.metric("Work Days", f"{act_work_days:.1f}", f"{act_work_days - est_work_days:+.1f} Days", delta_color="inverse")
m10.metric("Idle Days", f"{act_idle_days:.1f}", f"{act_idle_days - est_idle_days:+.1f} Days", delta_color="inverse")

# Row 2: Charts
c1, c2 = st.columns(2)

with c1:
    fig_fuel = go.Figure(data=[
        go.Bar(name='Estimated', x=['Total FO', 'FO Sea', 'FO Work', 'FO Idle', 'Total DO', 'DO Sea', 'DO Work', 'DO Idle'], 
               y=[est_tot_fo, est_fo_sea, est_fo_work, est_fo_idle, est_tot_do, est_do_sea, est_do_work, est_do_idle], marker_color='#1f77b4'),
        go.Bar(name='Actual', x=['Total FO', 'FO Sea', 'FO Work', 'FO Idle', 'Total DO', 'DO Sea', 'DO Work', 'DO Idle'], 
               y=[act_tot_fo, act_fo_sea, act_fo_work, act_fo_idle, act_tot_do, act_do_sea, act_do_work, act_do_idle], marker_color='#d62728')
    ])
    fig_fuel.update_layout(title="Fuel Consumption Breakdown (MT)", barmode='group', template='plotly_dark')
    st.plotly_chart(fig_fuel, use_container_width=True)

with c2:
    fig_time = go.Figure(data=[
        go.Bar(name='Estimated', x=['Total Days', 'Sea Days', 'Work Days', 'Idle Days'], 
               y=[est_tot_days, est_sea_days, est_work_days, est_idle_days], marker_color='#2ca02c'),
        go.Bar(name='Actual', x=['Total Days', 'Sea Days', 'Work Days', 'Idle Days'], 
               y=[act_tot_days, act_sea_days, act_work_days, act_idle_days], marker_color='#ff7f0e')
    ])
    fig_time.update_layout(title="Time & Duration Breakdown (Days)", barmode='group', template='plotly_dark')
    st.plotly_chart(fig_time, use_container_width=True)

# --- 7. PDF REPORT GENERATOR ---
def generate_voyage_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # 1. Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(190, 10, "Post-Voyage Performance Analysis", ln=True, align='C')
    pdf.ln(5)
    
    # 2. Vessel & Voyage Info
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 8, f"Vessel Name: {vessel_name}", ln=True)
    pdf.cell(190, 8, f"Voyage Number: {voyage_num}", ln=True)
    pdf.cell(190, 8, f"Fleet: {fleet_name}", ln=True)
    
    # Get current Y to draw line dynamically
    current_y = pdf.get_y() + 2
    pdf.line(10, current_y, 200, current_y)
    pdf.set_y(current_y + 5)
    
    # 3. Data Table
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 8, "Parameter", 1)
    pdf.cell(40, 8, "Estimated", 1)
    pdf.cell(40, 8, "Actual", 1)
    pdf.cell(30, 8, "Difference", 1, ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    
    def add_row(param, est, act, unit):
        diff = act - est
        diff_str = f"{diff:+.1f} {unit}"
        pdf.cell(50, 8, param, 1)
        pdf.cell(40, 8, f"{est:.1f} {unit}", 1)
        pdf.cell(40, 8, f"{act:.1f} {unit}", 1)
        pdf.cell(30, 8, diff_str, 1, ln=True)

    add_row("Weather Factor", est_weather, act_weather, "%")
    add_row("Cargo Quantity", est_cargo, act_cargo, "MT")
    add_row("Total Distance", est_tot_dist, act_tot_dist, "NM")
    add_row("Sea Days", est_sea_days, act_sea_days, "Days")
    add_row("Work Days", est_work_days, act_work_days, "Days")
    add_row("Idle Days", est_idle_days, act_idle_days, "Days")
    add_row("Total FO Cons", est_tot_fo, act_tot_fo, "MT")
    add_row("FO Work Cons", est_fo_work, act_fo_work, "MT")
    add_row("FO Idle Cons", est_fo_idle, act_fo_idle, "MT")
    add_row("Total DO Cons", est_tot_do, act_tot_do, "MT")
    add_row("DO Work Cons", est_do_work, act_do_work, "MT")
    add_row("DO Idle Cons", est_do_idle, act_do_idle, "MT")
    pdf.ln(10)
    
    # 4. Dashboard Charts
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(190, 10, "Visual Performance Charts", ln=True)
    pdf.ln(5)
    
    try:
        # Dashboarddaki grafikleri aynen PDF'e aktarma (Kaleido gerektirir)
        tmp_dir = tempfile.gettempdir()
        fuel_img_path = os.path.join(tmp_dir, "fuel_chart.png")
        time_img_path = os.path.join(tmp_dir, "time_chart.png")
        
        # Renk temasını PDF'e uygun (beyaz arka plan) yapmak için güncelleme
        fig_fuel_pdf = go.Figure(fig_fuel)
        fig_fuel_pdf.update_layout(template='plotly_white', title_font_color='black', font_color='black')
        
        fig_time_pdf = go.Figure(fig_time)
        fig_time_pdf.update_layout(template='plotly_white', title_font_color='black', font_color='black')
        
        fig_fuel_pdf.write_image(fuel_img_path, width=800, height=400)
        fig_time_pdf.write_image(time_img_path, width=800, height=400)
        
        current_y = pdf.get_y()
        pdf.image(fuel_img_path, x=10, y=current_y, w=190)
        
        # Ikinci grafik icin yeni sayfa
        pdf.add_page()
        pdf.image(time_img_path, x=10, y=20, w=190)
        pdf.set_y(120)
        
    except Exception as e:
        # Kaleido yoksa ust uste binmeyi onleyen dinamik Y eksenli native cizimler
        def draw_bar_chart(title, val_est, val_act, unit):
            pdf.set_font("Helvetica", "B", 10)
            y_pos = pdf.get_y()
            
            # Sayfa sonuna geldiysek yeni sayfa ac
            if y_pos > 250:
                pdf.add_page()
                y_pos = pdf.get_y()
                
            pdf.cell(190, 6, title, ln=True)
            
            max_val = max(val_est, val_act) * 1.2
            if max_val == 0: max_val = 1
            
            width_est = (val_est / max_val) * 120
            width_act = (val_act / max_val) * 120
            
            # Estimated Bar (Blue)
            pdf.set_fill_color(31, 119, 180)
            pdf.rect(40, y_pos + 8, width_est, 6, 'F')
            pdf.set_xy(10, y_pos + 8)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(30, 6, "Estimated:", 0, 0)
            pdf.set_xy(42 + width_est, y_pos + 8)
            pdf.cell(30, 6, f"{val_est:.1f} {unit}")
            
            # Actual Bar (Red)
            pdf.set_fill_color(214, 39, 40)
            pdf.rect(40, y_pos + 16, width_act, 6, 'F')
            pdf.set_xy(10, y_pos + 16)
            pdf.cell(30, 6, "Actual:", 0, 0)
            pdf.set_xy(42 + width_act, y_pos + 16)
            pdf.cell(30, 6, f"{val_act:.1f} {unit}")
            
            pdf.set_y(y_pos + 30) # Bir sonraki cizim icin aralik birak
            
        draw_bar_chart("Total Fuel Oil (FO) Consumption", est_tot_fo, act_tot_fo, "MT")
        draw_bar_chart("Total Diesel Oil (DO) Consumption", est_tot_do, act_tot_do, "MT")
        draw_bar_chart("Total Voyage Duration", est_tot_days, act_tot_days, "Days")

    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(190, 5, "* This report is generated electronically by the MarineDeCarb Simulator.", ln=True)
    
    # Save to temp
    tmp_path = os.path.join(tempfile.gettempdir(), "Voyage_Analyzer_Report.pdf")
    pdf.output(tmp_path)
    with open(tmp_path, "rb") as f:
        data = f.read()
    return data

# --- 8. DOWNLOAD BUTTON ---
st.sidebar.header("📥 Reporting")
if st.sidebar.button("📄 Download PDF Report", type="primary"):
    pdf_bytes = generate_voyage_pdf()
    file_name = f"{vessel_name.replace(' ', '_')}_{voyage_num}_Analysis.pdf"
    st.sidebar.download_button(
        label="💾 Save Report", 
        data=pdf_bytes, 
        file_name=file_name, 
        mime="application/pdf"
    )
    st.sidebar.success("✅ PDF is ready!")
