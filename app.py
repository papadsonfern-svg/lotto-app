import streamlit as st
import pandas as pd

st.set_page_config(page_title="โปรแกรมเจ้ามือหวยออนไลน์", layout="centered")

st.title("💸 โปรแกรมเจ้ามือหวยออนไลน์")

# -------------------------
# กำหนดค่าตั้งต้น
# -------------------------
if "bets" not in st.session_state:
    st.session_state.bets = []

if "blocked_numbers" not in st.session_state:
    st.session_state.blocked_numbers = {}

# -------------------------
# ส่วนกำหนดเลขอั้น
# -------------------------
st.sidebar.header("⚙️ ตั้งค่าเลขอั้น")
blocked_num = st.sidebar.text_input("เลขอั้น (เช่น 19 หรือ 123)")
blocked_limit = st.sidebar.number_input("ยอดสูงสุดของเลขอั้น", min_value=0, step=10)

if st.sidebar.button("เพิ่มเลขอั้น"):
    if blocked_num:
        st.session_state.blocked_numbers[blocked_num] = blocked_limit
        st.sidebar.success(f"เพิ่มเลขอั้น {blocked_num} (ไม่เกิน {blocked_limit} บาท)")

if st.session_state.blocked_numbers:
    st.sidebar.subheader("📌 รายการเลขอั้น")
    for k, v in st.session_state.blocked_numbers.items():
        st.sidebar.write(f"{k} → {v} บาท")

# -------------------------
# ฟอร์มรับโพย
# -------------------------
st.subheader("📝 เพิ่มโพยใหม่")

with st.form("add_bet"):
    number = st.text_input("เลข (2 หรือ 3 หลัก)").strip()
    bet_type = st.selectbox("ประเภท", ["2ตัวบน", "2ตัวล่าง", "3ตัวเต็ง", "3ตัวโต๊ด"])
    amount = st.number_input("ยอดซื้อ", min_value=1, step=1)

    submitted = st.form_submit_button("เพิ่มโพย")

    if submitted:
        if not number.isdigit():
            st.error("❌ ต้องกรอกเป็นตัวเลขเท่านั้น")
        else:
            # ตรวจสอบเลขอั้น
            if number in st.session_state.blocked_numbers:
                max_limit = st.session_state.blocked_numbers[number]
                # ยอดที่ซื้อไปแล้ว
                already = sum(
                    b["ยอดซื้อ"]
                    for b in st.session_state.bets
                    if b["เลข"] == number
                )
                if already + amount > max_limit:
                    st.error(f"❌ เลข {number} เป็นเลขอั้น รับได้อีกไม่เกิน {max_limit - already} บาท")
                else:
                    st.session_state.bets.append({"เลข": number, "ประเภท": bet_type, "ยอดซื้อ": amount})
                    st.success(f"✅ รับโพย {number} ({bet_type}) {amount} บาท")
            else:
                # ถ้าไม่ใช่เลขอั้น
                st.session_state.bets.append({"เลข": number, "ประเภท": bet_type, "ยอดซื้อ": amount})
                st.success(f"✅ รับโพย {number} ({bet_type}) {amount} บาท")

# -------------------------
# ตารางโพยทั้งหมด
# -------------------------
if st.session_state.bets:
    df = pd.DataFrame(st.session_state.bets)

    st.subheader("📊 โพยทั้งหมด")
    st.dataframe(df, use_container_width=True)

    # รวมโพยเลขซ้ำ
    st.subheader("🔄 รวมเลขซ้ำ")
    merged = df.groupby(["เลข", "ประเภท"], as_index=False).sum()
    st.dataframe(merged, use_container_width=True)

    # สรุปยอดรวม
    st.subheader("💰 สรุปยอดรวมตามประเภท")
    summary = merged.groupby("ประเภท")["ยอดซื้อ"].sum()
    st.write(summary)

    st.subheader("💵 ยอดรวมทั้งหมด")
    st.success(f"{df['ยอดซื้อ'].sum():,.0f} บาท")
