import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Konfigurasi Dasar
sns.set(style='whitegrid')
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# --- HELPER FUNCTIONS ---

def create_daily_rent_df(df):
    # Menggunakan resample untuk mendapatkan total harian
    daily_rent_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum",
        "registered": "sum",
        "casual": "sum"
    }).reset_index()
    return daily_rent_df

def create_time_category_rent_df(df):
    # Menghitung rata-rata penyewaan per kategori waktu
    time_category_df = df.groupby("time_category").cnt.mean().reset_index()
    sort_order = ['Morning Rush', 'Midday', 'Evening Rush', 'Quiet Hours']
    time_category_df['time_category'] = pd.Categorical(
        time_category_df['time_category'], 
        categories=sort_order, 
        ordered=True
    )
    return time_category_df.sort_values("time_category")

def create_season_rent_df(df):
    # Menghitung rata-rata harian per musim agar grafik responsif
    season_df = df.groupby("season").cnt.mean().reset_index()
    return season_df

# --- LOAD DATA (DIPERBAIKI) ---
@st.cache_data
def load_data():
    # Mengambil path folder tempat file dashboard_.py ini berada
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "Main_data.csv")
    
    # Membaca data menggunakan path absolut agar terdeteksi di Streamlit Cloud
    df = pd.read_csv(file_path)
    df['dteday'] = pd.to_datetime(df['dteday'])
    return df

all_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.title("Bike Sharing Analysis 🚲")
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Menentukan rentang tanggal minimal dan maksimal
    min_date = all_df["dteday"].min().date()
    max_date = all_df["dteday"].max().date()
    
    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# --- FILTER LOGIC ---
main_df = all_df[(all_df["dteday"].dt.date >= start_date) & 
                (all_df["dteday"].dt.date <= end_date)]

# Menyiapkan DataFrame turunan
daily_rent_df = create_daily_rent_df(main_df)
time_category_df = create_time_category_rent_df(main_df)
season_rent_df = create_season_rent_df(main_df)

# --- MAIN PAGE ---
st.header('Bike Sharing Dashboard 🚲')

# Row 1: Metrik Utama
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Penyewaan", value=f"{daily_rent_df.cnt.sum():,}")
with col2:
    st.metric("Pengguna Registered", value=f"{daily_rent_df.registered.sum():,}")
with col3:
    st.metric("Pengguna Casual", value=f"{daily_rent_df.casual.sum():,}")

st.markdown("---")

# Row 2: Visualisasi Pertanyaan Bisnis Utama
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Rata-rata Penyewaan per Musim")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x="season", y="cnt", data=season_rent_df, palette="Blues_d", ax=ax)
    ax.set_xlabel(None)
    ax.set_ylabel("Rata-rata Penyewaan")
    st.pyplot(fig)

with col_right:
    st.subheader("Pola Jam Sibuk (Hari Kerja vs Hari Libur)")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=main_df, x="hr", y="cnt", hue="workingday", palette="tab10", marker="o", ax=ax)
    ax.set_xticks(range(0, 24))
    ax.set_xlabel("Jam (0-23)")
    ax.set_ylabel("Rata-rata Penyewaan")
    st.pyplot(fig)

st.markdown("---")

# Row 3: Advanced Analysis
st.subheader("Advanced Analysis: Kategori Waktu & Demand Level")

col_a, col_b = st.columns(2)

with col_a:
    st.write("**Rata-rata Penyewaan Berdasarkan Kategori Waktu**")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x="time_category", y="cnt", data=time_category_df, palette="rocket", ax=ax)
    ax.set_xlabel(None)
    ax.set_ylabel("Rata-rata Penyewaan")
    st.pyplot(fig)

with col_b:
    if 'demand_category' in main_df.columns:
        st.write("**Distribusi Suhu per Level Permintaan**")
        fig, ax = plt.subplots(figsize=(10, 6))
        demand_order = ['Low Demand', 'Medium Demand', 'High Demand', 'Very High Demand']
        sns.boxplot(x="demand_category", y="temp", data=main_df, order=demand_order, palette="magma", ax=ax)
        ax.set_xlabel("Level Permintaan")
        ax.set_ylabel("Suhu (Normalized)")
        st.pyplot(fig)
    else:
        st.warning("Kolom 'demand_category' tidak ditemukan di data.")

st.caption('Copyright (c) 2026 - Andika Ardiansyah (Data Science Track)')
