import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config("เจ้ามือหวยออนไลน์", layout="wide")

if "orders" not in st.session_state:
    st.session_state.orders = pd.DataFrame(columns=["ประเภท","เลข","ยอดซื้อ","สถานะ","เวลา"])

# ตั้งค่า
st.sidebar.header("⚙️ ตั้งค่า")
percent = st.sidebar.number_input("เปอร์เซ็นต์หัก (%)", 0, 100, 20)
block2 = st.sidebar.text_input("เลขอั้น 2 ตัว (เช่น 19,29,99)")
block3 = st.sidebar.text_input("เลขอั้น 3 ตัว (เช่น 123,456,999)")

block2_set = {x.strip().zfill(2) for x in block2.split(",") if x.strip()}
block3_set = {x.strip().zfill(3) for x in block3.split(",") if x.strip()}

# เพิ่มโพย
st.header("📝 เพิ่มโพย")
col1, col2, col3, col4 = st.columns([2,1,1,1])
with col1:
    lotto_type = st.selectbox("ประเภท", ["2 ตัวบน","2 ตัวล่าง","3 ตัวเต็ง","3 ตัวโต๊ด"])
with col2:
    num = st.text_input("เลข")
with col3:
    amount = st.number_input("ยอดซื้อ", min_value=0, value=0)
with col4:
    if st.button("➕ เพิ่ม"):
        if lotto_type.startswith("2"):
            num = num.zfill(2)
            status = "อั้น" if num in block2_set else "ปกติ"
        else:
            num = num.zfill(3)
            status = "อั้น" if num in block3_set else "ปกติ"
        new = {"ประเภท": lotto_type, "เลข": num, "ยอดซื้อ": amount, "สถานะ": status, "เวลา": datetime.now()}
        st.session_state.orders = pd.concat([st.session_state.orders, pd.DataFrame([new])], ignore_index=True)

# แสดงโพย
st.subheader("📋 โพยทั้งหมด")
if st.session_state.orders.empty:
    st.info("ยังไม่มีโพย")
else:
    df = st.session_state.orders.groupby(["ประเภท","เลข","สถานะ"], as_index=False).sum()
    df["หลังหัก%"] = df["ยอดซื้อ"] * (100 - percent) / 100
    st.dataframe(df, use_container_width=True)

    total = df["ยอดซื้อ"].sum()
    total_net = df["หลังหัก%"].sum()
    st.metric("ยอดรวมทั้งหมด", f"{total:,.0f} บาท")
    st.metric(f"หลังหัก {percent}%", f"{total_net:,.0f} บาท")
    st.download_button("📥 ดาวน์โหลด CSV", df.to_csv(index=False).encode("utf-8-sig"),
                       "lotto_summary.csv", "text/csv")
