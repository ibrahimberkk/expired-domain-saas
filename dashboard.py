import streamlit as st
import pandas as pd
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Expired Domain Panel",
    layout="wide"
)

# --------------------------------------------------
# LOAD USERS
# --------------------------------------------------
with open("users.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# --------------------------------------------------
# LOGIN
# --------------------------------------------------
st.title("Giriş Yap")
name, authentication_status, username = authenticator.login()


if authentication_status is False:
    st.error("Kullanıcı adı veya şifre hatalı")
    st.stop()

elif authentication_status is None:
    st.warning("Lütfen giriş yapın")
    st.stop()

authenticator.logout("Çıkış", "sidebar")
st.sidebar.success(f"Hoş geldin {name}")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
df = pd.read_csv("seo_checked_domains.csv")

# ---- SAFE COLUMN CHECKS ----
if "backlink_estimate" not in df.columns:
    df["backlink_estimate"] = 0

if "niche" not in df.columns:
    df["niche"] = "general"

if "seo_score" not in df.columns:
    df["seo_score"] = 0

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("🔍 Filtreler")

max_seo_score = int(df["seo_score"].max())

min_seo, max_seo = st.sidebar.slider(
    "SEO Skoru",
    0,
    max(1, max_seo_score),
    (0, max(1, max_seo_score))
)

selected_niches = st.sidebar.multiselect(
    "Niche",
    sorted(df["niche"].unique()),
    default=list(df["niche"].unique())
)

max_backlink = int(df["backlink_estimate"].max())

if max_backlink > 0:
    min_backlink = st.sidebar.slider(
        "Min Backlink Tahmini",
        0,
        max_backlink,
        0
    )
else:
    min_backlink = 0
    st.sidebar.info("Backlink verisi henüz yok")


filtered_df = df[
    (df["seo_score"] >= min_seo) &
    (df["seo_score"] <= max_seo) &
    (df["niche"].isin(selected_niches)) &
    (df["backlink_estimate"] >= min_backlink)
]

# -----------
