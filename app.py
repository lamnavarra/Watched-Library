import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import create_engine, text


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="𝐖𝐚𝐭𝐜𝐡𝐞𝐝 𝐋𝐢𝐛𝐫𝐚𝐫𝐲",
    page_icon="🎥",
    layout="wide"
)


# =========================================================
# AUTHENTICATION
# =========================================================

if not st.user.is_logged_in:

    st.title("🎥 Watched Library")

    st.write(
        "Sign in with Google to access your personal library."
    )

    if st.button("Continue with Google"):
        st.login("google")

    st.stop()


user_id = str(st.user.sub)

user_name = getattr(st.user, "name", "User")
user_email = getattr(st.user, "email", "")

# =========================================================
# GENRE COLORS
# =========================================================
genre_colors = {
    "Action": "#C44545",
    "Adventure": "#C8753D",
    "Comedy": "#C99A2E",
    "Drama": "#7656A8",
    "Fantasy": "#5369B8",
    "Horror": "#7D3038",
    "Mystery": "#485A75",
    "Romance": "#C45C82",
    "Sci-Fi": "#367C8D",
    "Thriller": "#59606F",
    "Other": "#66666F"
}


# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp {
    background-color: rgb(25, 29, 45);
    color: white;
}


/* =====================================================
   SIDEBAR
   ===================================================== */

[data-testid="stSidebar"] {
    background: #55555D !important;
}


/* Sidebar text */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: white !important;
}


/* =====================================================
   LABELS
   ===================================================== */

[data-testid="stWidgetLabel"] p {
    color: white !important;
}
