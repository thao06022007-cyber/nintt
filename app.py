import streamlit as st
import pandas as pd
from groq import Groq
import os
import time

st.set_page_config(page_title="AI Survey Analysis", layout="wide")

st.title("📊 AI Survey Analysis")

# 🔐 API KEY
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ Chưa có API KEY. Vào Settings → Secrets để thêm GROQ_API_KEY")
else:
    client = Groq(api_key=api_key)

    uploaded_file = st.file_uploader("📂 Upload file Excel", type=["xlsx"])

    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)

            st.subheader("📋 Dữ liệu mẫu")
            st.dataframe(df.head())

            # ✅ kiểm tra cột
            if "Cluster" not in df.columns or "Content" not in df.columns:
                st.error("❌ File phải có cột 'Cluster' và 'Content'")
            else:
                # 🧹 làm sạch
                df["Content"] = df["Content"].astype(str)
                df = df[df["Content"].str.strip() != ""]

                # 🔥 fix cluster
                df["Cluster"] = pd.to_numeric(df["Cluster"], errors="coerce")
                df = df.dropna(subset=["Cluster"])
                df["Cluster"] = df["Cluster"].astype(int)

                clusters = (
                    df.groupby("Cluster")["Content"]
                    .apply(list)
                    .sort_index()
                )

                st.subheader("📊 Kết quả phân tích")

                # ✅ SESSION STATE (fix nút)
                if "run" not in st.session_state:
                    st.session_state.run = False

                if st.button("🚀 Phân tích"):
                    st.session_state.run = True

                if st.session_state.run:
                    st.write("👉 Đang phân tích...")

                    for c, texts in clusters.items():
                        st.markdown(f"### 🔹 Cluster {c}")

                        text = "\n".join(texts[:3])

                        try:
                            with st.spinner("Đang xử lý..."):
                                response = client.chat.completions.create(
                                    model="llama-3.1-8b-instant",
                                    messages=[{
                                        "role": "user",
                                        "content": f"""
Phân tích:

1. Chủ đề chính (1 câu)
2. Ý nghĩa (insight)

{text}
"""
                                    }]
                                )

                            st.success("✔ Xong")
                            st.write(response.choices[0].message.content)

                            time.sleep(0.5)  # chống treo

                        except Exception as e:
                            st.error(f"❌ Lỗi API: {e}")

        except Exception as e:
            st.error(f"❌ Lỗi đọc file: {e}")
