
# Load pages
import pages.home
import pages.locator
import pages.analysis

# Load libraries
import streamlit as st

st.set_page_config(
     page_title="Neighborhood Identification",
     layout='centered',
     initial_sidebar_state='expanded',
 )

pages = {
    # "Explore Neighborhoods": pages.home,
    "Analyze a Neighborhood": pages.locator
    # "Compare Neighborhoods": pages.analysis
}

def main():
    
    st.sidebar.header("Navigation")

    selection = st.sidebar.radio('', list(pages.keys()))

    pages[selection].create_page_structure()

if __name__ == '__main__':
    
    main()