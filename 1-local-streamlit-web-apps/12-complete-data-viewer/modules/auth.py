import hmac
import streamlit as st

def check_user_and_password():
    
    def password_entered():
        if (st.session_state["username"] in st.secrets["passwords"] and hmac.compare_digest(st.session_state["password"], st.secrets.passwords[st.session_state["username"]])):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    def login_form():
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", key="password", type="password")
            st.form_submit_button("Login", on_click= password_entered)

    if not st.session_state.get("password_correct", False):
        login_form()
        if "password_correct" in st.session_state:
            st.error("😒 Password Incorrect")
            st.stop()
