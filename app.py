import streamlit as st
import pandas as pd
from groq import Groq
import os
import time

st.title("📊 AI Survey Analysis")

# API
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.write(df.head())

    # 🧹 làm sạch
    df["Content"] = df["Content"].astype(str)
    df = df[df["Content"].str.strip() != ""]

    # 🔥 FIX thứ tự cluster (NHƯNG KHÔNG ĐỔI LOGIC)
    df["Cluster"] = pd.to_numeric(df["Cluster"], errors="coerce")
    df = df.dropna(subset=["Cluster"])
    df["Cluster"] = df["Cluster"].astype(int)

    clusters = df.groupby("Cluster")["Content"].apply(list).sort_index()

    if st.button("🚀 Phân tích"):
        for c, texts in clusters.items():
            st.subheader(f"Cluster {c}")

            text = "\n".join(texts[:3])  # giữ như cũ

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

                st.write(response.choices[0].message.content)

                time.sleep(0.5)  # 🔥 thêm nhẹ để tránh treo (quan trọng)

            except Exception as e:
                st.error(e)
