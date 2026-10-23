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
/* st.image bungkus <img> dalam beberapa lapis div (stElementContainer >
   stFullScreenFrame > stImage), semuanya ikut menyusut ke lebar gambar --
   jadi margin:auto harus ditaruh di stElementContainer (elemen yang benar-
   benar jadi flex item di dalam stVerticalBlock), bukan di <img> itu sendiri
   yang sudah tidak sisa ruang untuk di-center. Selektor ini aman dipakai
   untuk elemen lain (judul, caption) di dalam hero karena elemen yang
   lebarnya sudah 100% tidak terpengaruh oleh margin:auto. */
.st-key-hero [data-testid="stElementContainer"] {
    margin-left: auto !important;
    margin-right: auto !important;
}
.st-key-hero img {
    display: block !important;
    width: 420px !important;
    max-width: 420px !important;
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

/* Kartu hasil laporan siswa (lib/report_view.py). Font sengaja besar supaya
   mudah dibaca di HP. Tidak ada penanda ambang kelulusan di sini. */
.mm-report {
    margin-top: 1.75rem;
    padding-top: 1.75rem;
    border-top: 1px solid #e3e8ed;
    color: #1b2835;
}
.mm-report__top {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    align-items: start;
    gap: 1.25rem 2rem;
}
.mm-report__name {
    font-size: clamp(1.7rem, 5vw, 2.25rem);
    font-weight: 700;
    line-height: 1.2;
    color: #0d2438;
}
.mm-report__email {
    font-size: 1.2rem;
    color: #4a5a6a;
    margin-top: 0.4rem;
    overflow-wrap: anywhere;
}
.mm-report__meta {
    font-size: 1.1rem;
    color: #6b7b8b;
    margin-top: 0.2rem;
}
.mm-report__status {
    text-align: left;
}
.mm-report__label {
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    color: #5b6b7b;
}
.mm-pill {
    display: inline-block;
    margin: 0.55rem 0 0.7rem;
    padding: 0.55rem 1.2rem;
    border-radius: 999px;
    font-size: 1.25rem;
    font-weight: 700;
}
.mm-pill::before {
    content: "\\25CF";
    margin-right: 0.55rem;
    font-size: 0.9em;
}
.mm-pill--pass { background: #e3f4e1; color: #1c7a2c; }
.mm-pill--fail { background: #fde8e8; color: #b3261e; }
.mm-report__weeks {
    font-size: 1.1rem;
    color: #5b6b7b;
}
.mm-tiles {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1rem;
    margin-top: 1.75rem;
}
.mm-tile {
    border: 1px solid #dadfe3;
    border-radius: 12px;
    padding: 1.2rem 1.4rem 1.3rem;
}
.mm-tile__label {
    font-size: 1.1rem;
    font-weight: 700;
    color: #5b6b7b;
}
.mm-tile__value {
    font-size: clamp(2.8rem, 9vw, 3.6rem);
    font-weight: 700;
    line-height: 1.1;
    margin: 0.4rem 0 0.9rem;
    color: #0d2438;
}
.mm-tile__value small {
    font-size: 1.5rem;
    font-weight: 600;
    color: #6b7b8b;
    margin-left: 0.1rem;
}
.mm-bar {
    height: 10px;
    border-radius: 999px;
    background: #eef2f5;
    overflow: hidden;
}
.mm-bar > i { display: block; height: 100%; border-radius: 999px; }
.mm-report__note {
    margin-top: 1.25rem;
    padding: 0.9rem 1.15rem;
    border-radius: 10px;
    background: #eef5fb;
    color: #35506a;
    font-size: 1.05rem;
    line-height: 1.5;
}
.mm-report__note::before {
    content: "\\2139";
    margin-right: 0.6rem;
    font-weight: 700;
}
.mm-bar--blue { background: #0b77ba; }
.mm-bar--green { background: #7cb518; }
@media (min-width: 900px) {
    .mm-report__top { grid-template-columns: minmax(0, 1fr) auto; }
    .mm-report__status { text-align: right; }
}
@media (max-width: 640px) {
    .st-key-card { padding: 1.5rem 1.1rem 1.25rem; }
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
