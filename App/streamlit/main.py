
# Load libraries
import pages.home
import pages.locator
import pages.analysis
import streamlit as st

st.set_page_config(
     page_title="Neighborhood Identification",
     layout='centered',
     initial_sidebar_state='expanded',
 )

pages = {
    "Home": pages.home,
    "Find an Address": pages.locator,
    "Find a Neighborhood": pages.analysis
}

def main():
    
    st.sidebar.header("Navigation")

    selection = st.sidebar.radio('', list(pages.keys()))

    pages[selection].create_page_structure()

if __name__ == '__main__':
    
    main()