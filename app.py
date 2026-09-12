import streamlit as st

from lib.branding import apply_branding

st.set_page_config(
    page_title="MMin Semester Report",
    page_icon="assets/logo_apiis.png",
    layout="wide",
)
apply_branding()

page = st.navigation(
    [
        st.Page("app_pages/student.py", title="Laporan Semester", icon=":material/school:"),
        st.Page("app_pages/admin.py", title="Admin", icon=":material/admin_panel_settings:"),
    ],
    position="top",
)
page.run()
