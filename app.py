import streamlit as st
from movies import recommendation_page, filter_page

# Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

# Set up the sidebar navigation
st.sidebar.image("logo_moviedash.png", width=200)
st.sidebar.title("🎬 MovieDash")
page = st.sidebar.radio("Navigation", ["Recommendations", "Filter"])

# Display the selected page
if page == "Recommendations":
    recommendation_page()
else:
    filter_page()
