import streamlit as st
import pandas as pd
from groq import Groq
import os

st.title("📊 AI Survey Analysis")

# API KEY
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ Chưa có API KEY")
else:
    client = Groq(api_key=api_key)

    uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        st.write("📂 Dữ liệu:")
        st.write(df.head())

        # kiểm tra cột
        if "Cluster" not in df.columns or "Content" not in df.columns:
            st.error("❌ File phải có cột Cluster và Content")
        else:
            # làm sạch
            df["Content"] = df["Content"].astype(str)
            df = df[df["Content"].str.strip() != ""]

            # fix cluster
            df["Cluster"] = pd.to_numeric(df["Cluster"], errors="coerce")
            df = df.dropna(subset=["Cluster"])
            df["Cluster"] = df["Cluster"].astype(int)

            clusters = df.groupby("Cluster")["Content"].apply(list).sort_index()

            if st.button("🚀 Phân tích"):
                st.write("👉 Đang chạy...")

                for c, texts in clusters.items():
                    st.subheader(f"Cluster {c}")

                    text = "\n".join(texts[:3])

                    try:
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{
                                "role": "user",
                                "content": f"""
1. Chủ đề chính
2. Ý nghĩa

{text}
"""
                            }]
                        )

                        st.success("✔ Xong")
                        st.write(response.choices[0].message.content)

                    except Exception as e:
                        st.error(f"Lỗi: {e}")
