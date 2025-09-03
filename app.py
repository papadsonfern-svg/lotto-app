import streamlit as st
import pandas as pd

st.set_page_config(page_title="โปรแกรมเจ้ามือหวยออนไลน์", layout="wide")

st.markdown("<h1 style='text-align: center;'>💸 โปรแกรมเจ้ามือหวยออนไลน์</h1>", unsafe_allow_html=True)

# -------------------------
# ค่าเริ่มต้น
# -------------------------
if "bets" not in st.session_state:
    st.session_state.bets = []

if "blocked_numbers" not in st.session_state:
    st.session_state.blocked_numbers = {}

# -------------------------
# Sidebar: ตั้งค่าเลขอั้น
# -------------------------
with st.sidebar:
    st.header("⚙️ ตั้งค่าเลขอั้น")
    blocked_num = st.text_input("เลขอั้น (เช่น 19 หรือ 123)")
    blocked_limit = st.number_input("ยอดสูงสุดของเลขอั้น", min_value=0, step=10)

    if st.button("เพิ่มเลขอั้น"):
        if blocked_num:
            st.session_state.blocked_numbers[blocked_num] = blocked_limit
            st.success(f"เพิ่มเลขอั้น {blocked_num} (ไม่เกิน {blocked_limit} บาท)")

    if st.session_state.blocked_numbers:
        st.subheader("📌 รายการเลขอั้น")
        blocked_data = []
        for num, limit in st.session_state.blocked_numbers.items():
            already = sum(b["ยอดซื้อ"] for b in st.session_state.bets if b["เลข"] == num)
            remaining = max(limit - already, 0)
            blocked_data.append({"เลข": num, "รับสูงสุด": limit, "ซื้อไปแล้ว": already, "รับเพิ่มได้": remaining})
        st.dataframe(pd.DataFrame(blocked_data))

# -------------------------
# Layout 3 คอลัมน์
# -------------------------
col1, col2, col3 = st.columns([1.5, 2, 2])

# -------------------------
# col1: ฟอร์มเพิ่มโพย
# -------------------------
with col1:
    st.markdown("### 📝 เพิ่มโพยใหม่")
    with st.form("add_bet"):
        number = st.text_input("เลข (2 หรือ 3 หลัก)").strip()
        bet_type = st.selectbox("ประเภท", ["2ตัวบน", "2ตัวล่าง", "3ตัวเต็ง", "3ตัวโต๊ด"])
        amount = st.number_input("ยอดซื้อ", min_value=1, step=1)
        submitted = st.form_submit_button("เพิ่มโพย")

        if submitted:
            if not number.isdigit():
                st.error("❌ ต้องกรอกเป็นตัวเลขเท่านั้น")
            else:
                if number in st.session_state.blocked_numbers:
                    max_limit = st.session_state.blocked_numbers[number]
                    already = sum(b["ยอดซื้อ"] for b in st.session_state.bets if b["เลข"] == number)
                    if already + amount > max_limit:
                        st.error(f"❌ เลข {number} เป็นเลขอั้น รับได้อีกไม่เกิน {max_limit - already} บาท")
                    else:
                        st.session_state.bets.append({"เลข": number, "ประเภท": bet_type, "ยอดซื้อ": amount})
                        st.success(f"✅ รับโพย {number} ({bet_type}) {amount} บาท")
                else:
                    st.session_state.bets.append({"เลข": number, "ประเภท": bet_type, "ยอดซื้อ": amount})
                    st.success(f"✅ รับโพย {number} ({bet_type}) {amount} บาท")

# -------------------------
# col2: ตารางโพยทั้งหมด
# -------------------------
with col2:
    st.markdown("### 📊 โพยทั้งหมด")
    if st.session_state.bets:
        df = pd.DataFrame(st.session_state.bets)
        st.dataframe(df, use_container_width=True)

        # รวมเลขซ้ำ
        st.markdown("### 🔄 รวมเลขซ้ำแยกตามประเภท")

        for cat in ["2ตัวบน", "2ตัวล่าง", "3ตัวเต็ง", "3ตัวโต๊ด"]:
            cat_df = df[df["ประเภท"] == cat].groupby("เลข", as_index=False).sum()
            if not cat_df.empty:
                st.write(f"👉 {cat}")
                st.dataframe(cat_df)

# -------------------------
# col3: สรุปผลรวม
# -------------------------
with col3:
    if st.session_state.bets:
        df = pd.DataFrame(st.session_state.bets)

        st.markdown("### 💰 สรุปยอดรวมตามประเภท")
        summary = df.groupby("ประเภท")["ยอดซื้อ"].sum()
        st.write(summary)

        st.markdown("### 💵 ยอดรวมทั้งหมด")
        st.success(f"{df['ยอดซื้อ'].sum():,.0f} บาท")
