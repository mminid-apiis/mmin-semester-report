"""Tampilan bermerek tetap (terinspirasi halaman login APIIS Volunteer App):
gradasi navy gelap di latar, kartu putih membulat untuk konten utama. Tidak
ada lagi toggle terang/gelap -- ini satu-satunya tampilan aplikasi.
"""

import base64

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
/* Tombol "Fork"/GitHub (disuntikkan Streamlit Community Cloud) dan menu titik tiga
   disembunyikan dari pengunjung. Sengaja TIDAK menyembunyikan stToolbar penuh
   supaya navigasi atas tidak ikut hilang. */
[data-testid="stToolbarActions"],
[data-testid="stMainMenu"],
[data-testid="stAppDeployButton"] {
    display: none !important;
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
/* Judul dua warna: kata terakhir hijau APIIS. */
.st-key-hero .mm-title {
    margin: 0.6rem 0 0;
    padding: 0;
    font-size: clamp(2.1rem, 7vw, 3.1rem);
    font-weight: 800;
    letter-spacing: -0.01em;
    line-height: 1.15;
}
.st-key-hero .mm-title span {
    color: #7cb518 !important;
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
/* Logo tidak perlu tombol "Fullscreen" bawaan st.image (hasilnya layar putih kosong
   karena logo transparan). Hanya di hero; tabel di panel admin tetap punya toolbar. */
.st-key-hero [data-testid="stElementToolbar"] {
    display: none !important;
}
.st-key-hero img {
    display: block !important;
    width: 420px !important;
    max-width: 420px !important;
    height: auto !important;
}

.st-key-card, .st-key-card_wide {
    position: relative;
    z-index: 1;
    background: #ffffff;
    border-radius: 14px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.25), 0 8px 10px -6px rgba(0, 0, 0, 0.15);
    border-top: 5px solid #7cb518;
    padding: 2rem 2.5rem 1.75rem;
    max-width: 660px;
    margin: 2rem auto 3rem;
}
/* Halaman hasil: kartu lebar, tanpa form. */
.st-key-card_wide {
    max-width: 1100px;
    padding: 2.25rem 2.5rem 2rem;
}
.st-key-card [data-testid="stWidgetLabel"] p,
.st-key-card_wide [data-testid="stWidgetLabel"] p {
    font-size: 1.02rem;
    font-weight: 600;
    color: #1b2835;
}
.st-key-card [data-testid="stFormSubmitButton"] button {
    min-height: 3.4rem;
    font-size: 1.05rem;
    font-weight: 600;
    background: #2f7bc4;
    border-color: #2f7bc4;
    color: #ffffff;
}
.st-key-card [data-testid="stFormSubmitButton"] button:hover {
    background: #2468a8;
    border-color: #2468a8;
    color: #ffffff;
}

/* Kartu hasil laporan siswa (lib/report_view.py). Font sengaja besar supaya
   mudah dibaca di HP. Tidak ada penanda ambang kelulusan di sini. */
.mm-report {
    color: #1b2835;
}
.mm-report__top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid #e3e8ed;
}
.mm-report__who {
    flex: 1 1 auto;
    min-width: 0;
}
.mm-report__kelas {
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: #5b6b7b;
}
.mm-report__chip {
    flex: none;
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    background: #eef5fb;
    color: #35506a;
    font-size: 0.95rem;
    font-weight: 600;
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
    margin-top: 1.75rem;
}
.mm-report__label {
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    color: #5b6b7b;
}
.mm-pill {
    display: flex;
    align-items: flex-start;
    margin: 0.55rem 0 0.7rem;
    padding: 0.9rem 1.3rem;
    border-radius: 14px;
    font-size: clamp(1.1rem, 3.2vw, 1.3rem);
    font-weight: 700;
    line-height: 1.4;
}
.mm-pill::before {
    content: "\\25CF";
    flex: none;
    margin-right: 0.7rem;
    font-size: 0.9em;
    line-height: 1.55;
}
.mm-pill--pass { background: #e3f4e1; color: #1c7a2c; }
.mm-pill--warn { background: #fff3c4; color: #7a5200; }
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
.mm-report__rank {
    margin-top: 1.25rem;
    padding: 0.9rem 1.15rem;
    border-radius: 10px;
    border: 1px solid #dadfe3;
    border-left: 5px solid #0b77ba;
    color: #1b2835;
    font-size: 1.15rem;
    line-height: 1.5;
}
.mm-report__rank strong {
    font-size: 1.5rem;
    color: #0d2438;
}
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
@media (max-width: 640px) {
    .st-key-card, .st-key-card_wide { padding: 1.5rem 1.1rem 1.25rem; }
    .mm-report__top { flex-direction: column; gap: 0.9rem; }
    .mm-report__chip { align-self: flex-start; }
    .st-key-hero img { width: min(240px, 62vw) !important; max-width: 240px !important; }
}

.st-key-footer, .st-key-footer p {
    color: #b9d1e5 !important;
    text-align: center;
    font-size: 0.8rem;
}
</style>
"""


# Bendera di knop tombol bahasa (SVG kecil, di-embed sebagai data URI).
_UK_FLAG_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 30">'
    '<clipPath id="s"><path d="M0,0 v30 h60 v-30 z"/></clipPath>'
    '<clipPath id="t"><path d="M30,15 h30 v15 z v15 h-30 z h-30 v-15 z v-15 h30 z"/></clipPath>'
    '<g clip-path="url(#s)"><path d="M0,0 v30 h60 v-30 z" fill="#012169"/>'
    '<path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/>'
    '<path d="M0,0 L60,30 M60,0 L0,30" clip-path="url(#t)" stroke="#C8102E" stroke-width="4"/>'
    '<path d="M30,0 v30 M0,15 h60" stroke="#fff" stroke-width="10"/>'
    '<path d="M30,0 v30 M0,15 h60" stroke="#C8102E" stroke-width="6"/></g></svg>'
)
_ID_FLAG_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 3 2">'
    '<rect width="3" height="1" fill="#E70011"/><rect y="1" width="3" height="1" fill="#fff"/></svg>'
)


def _data_uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


# Tombol geser bahasa EN | ID di pojok kanan atas (dirender app.py lewat
# render_language_switcher()). st.toggle bawaan ditata ulang: kiri (mati) = English,
# kanan (hidup) = Indonesia; knopnya menampilkan bendera bahasa yang aktif.
_LANG_TOGGLE_CSS = """
<style>
/* Ikut bergulir bersama halaman: diposisikan absolut terhadap area gulir (stMain). */
[data-testid="stMain"] {
    position: relative;
}
.st-key-langswitch {
    position: absolute;
    top: 0.55rem;
    right: 1rem;
    z-index: 1000002;
    width: auto !important;
}
.st-key-langswitch [data-testid="stElementContainer"] {
    width: auto !important;
}
.st-key-langswitch label {
    position: relative;
    display: flex;
    align-items: center;
    gap: 0.65rem;
    width: auto !important;
    padding: 0.32rem 0.9rem;
    border-radius: 999px;
    background: #eef1f5;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.28), inset 0 1px 1px rgba(255, 255, 255, 0.9);
    cursor: pointer;
}
.st-key-langswitch label > span {
    position: absolute;
    opacity: 0;
}
.st-key-langswitch label [data-testid="stWidgetLabel"] {
    display: none;
}
.st-key-langswitch label::before,
.st-key-langswitch label::after {
    font-size: 0.95rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    color: #aeb7c2;
    transition: color 0.15s;
}
.st-key-langswitch label::before { content: "EN"; }
.st-key-langswitch label::after { content: "ID"; }
.st-key-langswitch label:not(:has(input:checked))::before { color: #2f3d4e; }
.st-key-langswitch label:has(input:checked)::after { color: #2f3d4e; }
.st-key-langswitch label > div:not([data-testid]) {
    position: relative !important;
    flex: none;
    width: 62px !important;
    height: 30px !important;
    margin: 0 !important;
    border-radius: 999px !important;
    background: #dde2e8 !important;
    box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.2), inset 0 -1px 2px rgba(255, 255, 255, 0.7) !important;
}
.st-key-langswitch label > div:not([data-testid]) > div {
    position: absolute !important;
    top: 2px !important;
    left: 3px !important;
    width: 26px !important;
    height: 26px !important;
    margin: 0 !important;
    box-sizing: border-box;
    border: 2px solid #ffffff;
    border-radius: 50% !important;
    transform: none !important;
    background: url("__UK_FLAG__") center / cover no-repeat !important;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.35), inset 0 0 0 1px rgba(0, 0, 0, 0.1);
    transition: left 0.2s ease !important;
}
.st-key-langswitch label:has(input:checked) > div:not([data-testid]) > div {
    left: calc(100% - 29px) !important;
    background-image: url("__ID_FLAG__") !important;
}
.st-key-langswitch label:has(input:focus-visible) {
    outline: 2px solid #1690d0;
    outline-offset: 3px;
}
@media (max-width: 640px) {
    .st-key-langswitch { top: 0.5rem; right: 0.6rem; }
    .st-key-langswitch label { gap: 0.45rem; padding: 0.28rem 0.65rem; }
    .st-key-langswitch label::before,
    .st-key-langswitch label::after { font-size: 0.8rem; }
}
</style>
"""


def apply_branding():
    toggle_css = _LANG_TOGGLE_CSS.replace("__UK_FLAG__", _data_uri(_UK_FLAG_SVG)).replace(
        "__ID_FLAG__", _data_uri(_ID_FLAG_SVG)
    )
    st.markdown(_BRAND_CSS + toggle_css, unsafe_allow_html=True)
