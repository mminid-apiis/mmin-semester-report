import streamlit as st

_DARK_CSS = """
<style>
[data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
    background-color: #0e1117 !important;
    color: #fafafa !important;
}
section[data-testid="stSidebar"] {
    background-color: #161a23 !important;
}
h1, h2, h3, h4, h5, h6, p, span, label, li,
[data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"] {
    color: #fafafa !important;
}
[data-testid="stExpander"] {
    background-color: #161a23 !important;
    border-color: #30363d !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    background-color: #161a23 !important;
    color: #fafafa !important;
}
.stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {
    background-color: #262730 !important;
    color: #fafafa !important;
    border-color: #454b5a !important;
}
button {
    background-color: #262730 !important;
    color: #fafafa !important;
    border-color: #454b5a !important;
}
button[kind="primary"], [data-testid="baseButton-primary"] {
    background-color: #6c63ff !important;
    color: #ffffff !important;
    border-color: #6c63ff !important;
}
[data-testid="stAlert"] {
    background-color: #1f2430 !important;
}
[data-testid="stAlertContentSuccess"], [data-testid="stAlertContentSuccess"] * {
    color: #6fe3a1 !important;
}
[data-testid="stAlertContentInfo"], [data-testid="stAlertContentInfo"] * {
    color: #7fc8f8 !important;
}
[data-testid="stAlertContentWarning"], [data-testid="stAlertContentWarning"] * {
    color: #ffd479 !important;
}
[data-testid="stAlertContentError"], [data-testid="stAlertContentError"] * {
    color: #ff8a8a !important;
}
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
    color: #fafafa !important;
}
[data-testid="stDataFrame"] {
    background-color: #161a23 !important;
}
hr {
    border-color: #30363d !important;
}
</style>
"""


def is_dark() -> bool:
    return st.session_state.get("dark_mode", False)


def apply_theme():
    if is_dark():
        st.markdown(_DARK_CSS, unsafe_allow_html=True)
