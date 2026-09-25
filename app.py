import streamlit as st

from lib.branding import apply_branding
from lib.i18n import t

st.set_page_config(
    page_title="MMin Semester Report",
    page_icon="assets/logo_apiis.png",
    layout="wide",
)
apply_branding()

page = st.navigation(
    [
        st.Page("app_pages/student.py", title=t("nav_student"), icon=":material/school:"),
        st.Page("app_pages/admin.py", title=t("nav_admin"), icon=":material/admin_panel_settings:"),
    ],
    position="top",
)
page.run()
