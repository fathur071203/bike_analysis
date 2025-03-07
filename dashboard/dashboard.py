import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

st.set_page_config(page_title="Dashboard Peminjaman Sepeda", layout="wide")
@st.cache_data
def load_data():
    day_df = pd.read_csv("dashboard/day_data.csv")
    hour_df = pd.read_csv("dashboard/hour_data.csv")
    return day_df, hour_df
day_df, hour_df = load_data()

day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
day_df["year_month"] = day_df["dteday"].dt.to_period("M")

# Sidebar berdasarkan tanggal
st.sidebar.header("Filter")
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", 
                                  [day_df["dteday"].min(), day_df["dteday"].max()], 
                                  min_value=day_df["dteday"].min(), 
                                  max_value=day_df["dteday"].max())

# Filter 
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = day_df[(day_df["dteday"] >= pd.Timestamp(start_date)) & (day_df["dteday"] <= pd.Timestamp(end_date))]
    filtered_hour_df = hour_df[(hour_df["dteday"] >= pd.Timestamp(start_date)) & (hour_df["dteday"] <= pd.Timestamp(end_date))]
else:
    filtered_df = day_df
    filtered_hour_df = hour_df

filtered_monthly_df = filtered_df.groupby("year_month")["cnt"].sum().reset_index()
total_peminjaman = filtered_monthly_df["cnt"].sum()

#Ringkasan Statistik
st.markdown("## 📊 Ringkasan Statistik")

avg_daily = filtered_df["cnt"].mean()
max_rent = filtered_df["cnt"].max()
min_rent = filtered_df["cnt"].min()
max_rent_date = filtered_df.loc[filtered_df["cnt"].idxmax(), "dteday"].strftime("%Y-%m-%d")
min_rent_date = filtered_df.loc[filtered_df["cnt"].idxmin(), "dteday"].strftime("%Y-%m-%d")

col1, col2, col3 = st.columns(3)
col1.metric(label="📈 Rata-rata Peminjaman Harian", value=f"{avg_daily:.0f}")
col2.metric(label="🔝 Peminjaman Tertinggi", value=f"{max_rent} ({max_rent_date})")
col3.metric(label="🔻 Peminjaman Terendah", value=f"{min_rent} ({min_rent_date})")

prev_period_df = day_df[
    (day_df["dteday"] >= (pd.Timestamp(start_date) - pd.DateOffset(days=(end_date - start_date).days))) & 
    (day_df["dteday"] < pd.Timestamp(start_date))
]

prev_total = prev_period_df["cnt"].sum()
change_percentage = ((total_peminjaman - prev_total) / prev_total) * 100 if prev_total > 0 else 0
st.metric(label="📊 Perubahan dari Periode Sebelumnya", value=f"{change_percentage:.2f}%", 
          delta=change_percentage, delta_color="inverse")

st.markdown("## 📊 Dashboard Peminjaman Sepeda")
st.metric(label="Total Peminjaman", value=total_peminjaman)
st.markdown("---")

# Bagian 1: Tren Peminjaman Sepeda
st.subheader("Tren Peminjaman Sepeda")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📅 Tren Bulanan")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(filtered_monthly_df["year_month"].astype(str), filtered_monthly_df["cnt"], marker='o', color="#90CAF9")
    ax.set_xticklabels(filtered_monthly_df["year_month"], rotation=45)
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total Peminjaman")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(fig)

with col2:
    if "day_category" in filtered_hour_df.columns:
        st.markdown("### ⏰ Tren Peminjaman per Jam")
        hourly_trend = filtered_hour_df.groupby(["hr", "day_category"])["cnt"].mean().reset_index()
        fig, ax = plt.subplots(figsize=(8, 5))
        for category in hourly_trend["day_category"].unique():
            subset = hourly_trend[hourly_trend["day_category"] == category]
            ax.plot(subset["hr"], subset["cnt"], marker='o', label=category)
        ax.legend(title="Kategori Hari")
        ax.set_xlabel("Jam")
        ax.set_ylabel("Rata-rata Peminjaman")
        ax.grid(axis="y", linestyle="--", alpha=0.7)
        st.pyplot(fig)

# Bagian 2: Analisis Kategori Hari
st.markdown("---")
st.subheader("Analisis Berdasarkan Kategori Hari")
col3, col4 = st.columns(2)

with col3:
    if "day_category" in filtered_df.columns:
        st.markdown("### 📊 Statistik Kategori Hari")
        day_category_stats = filtered_df.groupby("day_category")["cnt"].agg(["mean", "min", "max"]).reset_index()
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = ["skyblue", "lightcoral", "lightgreen"]
        sns.barplot(data=day_category_stats, x="day_category", y="mean", palette=colors, ax=ax)

        for i, row in enumerate(day_category_stats.itertuples()):
            ax.text(i, row.mean, f'{row.mean:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
            ax.plot([i, i], [row.min, row.max], color="black", linestyle="--", linewidth=1.5)
            ax.scatter(i, row.min, color="red", marker="v", label="Min" if i == 0 else "")
            ax.scatter(i, row.max, color="green", marker="^", label="Max" if i == 0 else "")

        ax.set_xlabel("Kategori Hari")
        ax.set_ylabel("Jumlah Sewa Rata-rata")
        ax.set_title("Rata-rata, Min, dan Max Sewa Sepeda per Kategori Hari")
        ax.set_xticklabels(day_category_stats["day_category"], rotation=15)
        ax.grid(axis="y", linestyle="--", alpha=0.7)

        if "Min" in ax.get_legend_handles_labels()[1]:
            ax.legend()
        st.pyplot(fig)

with col4:
    if "day_category" in filtered_df.columns:
        st.markdown("### 👥 Perbandingan Tipe Pengguna")
        day_trend = filtered_df.groupby("day_category")[["casual", "registered"]].mean().reset_index()
        fig, ax = plt.subplots(figsize=(8, 5))
        barplot = sns.barplot(data=day_trend.melt(id_vars="day_category", var_name="User Type", value_name="Avg Count"), 
                              x="day_category", y="Avg Count", hue="User Type", ax=ax)
        
        for p in barplot.patches:
            ax.text(p.get_x() + p.get_width() / 2., p.get_height(), f'{p.get_height():.0f}', 
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_xlabel("Kategori Hari")
        ax.set_ylabel("Rata-rata Peminjaman")
        ax.legend(title="Tipe Pengguna")
        st.pyplot(fig)

# Bagian 3: Tren Musiman
st.markdown("---")
st.subheader("Tren Peminjaman Berdasarkan Musim")
season_labels = {1: "Musim Semi", 2: "Musim Panas", 3: "Musim Gugur", 4: "Musim Dingin"}
seasonal_trend = filtered_df.groupby(["season", "yr"])["cnt"].mean().reset_index()
seasonal_trend["season"] = seasonal_trend["season"].map(season_labels)
order = ["Musim Semi", "Musim Panas", "Musim Gugur", "Musim Dingin"]
seasonal_trend["season"] = pd.Categorical(seasonal_trend["season"], categories=order, ordered=True)

fig, ax = plt.subplots(figsize=(8, 5))
sns.lineplot(data=seasonal_trend, x="season", y="cnt", hue="yr", style="yr", markers=True, dashes=False, ax=ax)
ax.set_xlabel("Musim")
ax.set_ylabel("Rata-rata Peminjaman Sepeda")
ax.legend(title="Tahun", labels=["2011", "2012"])
ax.grid(axis="y", linestyle="--", alpha=0.6)
st.pyplot(fig)

st.markdown("---")
st.write("© 2025 - Muhammad Fathurrahman")
