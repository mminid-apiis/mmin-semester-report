"""Tampilan bermerek tetap (terinspirasi halaman login APIIS Volunteer App):
gradasi navy gelap di latar, kartu putih membulat untuk konten utama. Tidak
ada lagi toggle terang/gelap -- ini satu-satunya tampilan aplikasi.
"""

import streamlit as st

_BRAND_CSS = """
<style>
.stApp {
    background: linear-gradient(135deg, #0d2438 0%, #0c3c60 55%, #0a2c49 100%);
}
[data-testid="stHeader"] {
    background: transparent !important;
}
[data-testid="stHeader"] * {
    color: #eef4fa !important;
}
[data-testid="stHeader"] svg {
    fill: #eef4fa !important;
}
[data-testid="stTopNavLink"], [data-testid="stTopNavLink"] * {
    color: #9fb8ce !important;
}
[data-testid="stTopNavLink"][aria-current="page"], [data-testid="stTopNavLink"][aria-current="page"] * {
    color: #ffffff !important;
    font-weight: 600;
}
.stApp::before, .stApp::after {
    content: "";
    position: fixed;
    width: 24rem;
    height: 24rem;
    border-radius: 50%;
    pointer-events: none;
    z-index: 0;
}
.stApp::before {
    top: -6rem;
    right: -6rem;
    background: radial-gradient(closest-side, #1690d0, transparent);
}
.stApp::after {
    bottom: -7rem;
    left: -6rem;
    background: radial-gradient(closest-side, #7cb518, transparent);
}

.st-key-hero, .st-key-hero p, .st-key-hero span, .st-key-hero div {
    color: #eef4fa !important;
    text-align: center;
}
.st-key-hero h1 {
    color: #ffffff !important;
    text-align: center;
}
.st-key-hero img {
    display: block !important;
    margin: 0 auto !important;
    width: 140px !important;
    max-width: 140px !important;
    height: auto !important;
}

.st-key-card {
    position: relative;
    z-index: 1;
    background: #ffffff;
    border-radius: 14px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.25), 0 8px 10px -6px rgba(0, 0, 0, 0.15);
    padding: 2rem 2.5rem 1.5rem;
    max-width: 1100px;
    margin: 2rem auto 3rem;
}

.st-key-footer, .st-key-footer p {
    color: #7fa8c9 !important;
    text-align: center;
    font-size: 0.8rem;
}
</style>
"""


def apply_branding():
    st.markdown(_BRAND_CSS, unsafe_allow_html=True)
