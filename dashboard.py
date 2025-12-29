import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import random

# -------------------------------
# SAYFA AYARLARI
# -------------------------------
st.set_page_config(
    page_title="Expired Domain SaaS",
    layout="wide"
)

# -------------------------------
# KULLANICI AYARLARI (STATIK)
# -------------------------------
credentials = {
    "usernames": {
        "admin": {
            "name": "Admin",
            "password": "$2b$12$0Yp8pYtG7tZz0Qx1j1jYQO8E1E2p9V6nGJQ6Z0V9bP5nQF9GQX9a2"
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "expired_domain_cookie",
    "expired_domain_key",
    cookie_expiry_days=7
)

# -------------------------------
# LOGIN
# -------------------------------
st.title("🔐 Giriş Yap")

authenticator.login(location="main")

authentication_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")

if authentication_status is False:
    st.error("Kullanıcı adı veya şifre yanlış")
    st.stop()

if authentication_status is None:
    st.warning("Lütfen giriş yapın")
    st.stop()

# -------------------------------
# DASHBOARD
# -------------------------------
st.success(f"Hoş geldin {name}")

authenticator.logout("Çıkış Yap", "sidebar")

st.sidebar.title("Ayarlar")

st.header("🚀 Expired Domain Tarama Paneli")

# -------------------------------
# INPUTLAR
# -------------------------------
niche = st.text_input(
    "Niche / Sektör",
    placeholder="örnek: teknoloji, sağlık, e-ticaret"
)

domain_count = st.slider(
    "Kaç domain üretilecek?",
    min_value=5,
    max_value=50,
    value=10
)

min_backlink = st.slider(
    "Minimum Backlink Tahmini",
    min_value=0,
    max_value=500,
    value=0
)

# -------------------------------
# BUTON
# -------------------------------
if st.button("🔍 Taramayı Başlat"):
    if not niche:
        st.warning("Lütfen bir niche giriniz")
    else:
        with st.spinner("Expired domainler aranıyor..."):
            data = []

            for i in range(domain_count):
                backlink = random.randint(1, 500)
                seo_score = random.randint(10, 100)

                if backlink >= min_backlink:
                    data.append({
                        "domain": f"{niche}{i+1}.com",
                        "niche": niche,
                        "backlink_estimate": backlink,
                        "seo_score": seo_score
                    })

            df = pd.DataFrame(data)

        if df.empty:
            st.warning("Filtrelere uygun domain bulunamadı")
        else:
            st.success(f"{len(df)} domain bulundu")

            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 CSV olarak indir",
                data=csv,
                file_name=f"{niche}_expired_domains.csv",
                mime="text/csv"
            )

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("Expired Domain SaaS • Demo Version")
