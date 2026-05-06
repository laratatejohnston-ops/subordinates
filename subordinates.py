import streamlit as st

from modules.db import init_database, login_user, create_user
from modules.activity_log import render_activity_log
from modules.shared_calendar import render_shared_calendar
from modules.what_to_do import render_what_to_do
from modules.personal_times import render_personal_times

st.set_page_config(
    page_title="Subordinates",
    page_icon="🍸",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #fff8f3;
    }

    h1, h2, h3 {
        color: #3b2f2f;
    }

    div.stButton > button {
        border-radius: 14px;
        background-color: #f2c6c2;
        color: #3b2f2f;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }

    div.stButton > button:hover {
        background-color: #e8aaa5;
        color: white;
    }

    .calendar-card {
        padding: 12px;
        border-radius: 16px;
        margin-bottom: 10px;
        border: 1px solid #ead6ce;
        background-color: #fffaf7;
    }

    .solid-event {
        opacity: 1;
        border-left: 8px solid #3b2f2f;
    }

    .suggestion-event {
        opacity: 0.55;
        border-left: 8px dashed #3b2f2f;
    }

    .rejected-event {
        opacity: 0.35;
        text-decoration: line-through;
    }
</style>
""", unsafe_allow_html=True)

init_database()

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🍸 Subordinates")
    st.subheader("Login or create an account")

    login_tab, signup_tab = st.tabs(["Login", "Create account"])

    with login_tab:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            user = login_user(email, password)

            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Wrong email or password.")

    with signup_tab:
        name = st.text_input("Your name")
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")
        colour = st.color_picker("Choose your calendar colour", "#C8E6C9")

        if st.button("Create account"):
            success = create_user(name, new_email, new_password, colour)

            if success:
                st.success("Account created. Now login.")
            else:
                st.error("This email already exists.")

    st.stop()

st.title("🍸 Subordinates")
st.caption(f"Logged in as {st.session_state.user['name']}")

if st.button("Logout"):
    st.session_state.user = None
    st.rerun()

tab1, tab2, tab3, tab4 = st.tabs([
    "1. Logging",
    "2. Shared Calendar",
    "3. What should we do?",
    "4. Personal Times"
])

with tab1:
    render_activity_log(st.session_state.user)

with tab2:
    render_shared_calendar(st.session_state.user)

with tab3:
    render_what_to_do(st.session_state.user)

with tab4:
    render_personal_times(st.session_state.user)