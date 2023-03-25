import streamlit as st
import requests

from cprint import cprint
from streamlit_lottie import st_lottie
from project import main as project_main, Company, COLUMNS

# CONFIG
st.set_page_config(page_title="Job Search", page_icon=":briefcase:", layout="wide")

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def hide_anchor_link():
    st.markdown("""
        <style>
        .css-15zrgzn {display: none}
        </style>
        """, unsafe_allow_html=True)

def fill_fields():
    st.warning("Please fill in all the fields")
    
def show_results(all_companies: list):
    length = len(COLUMNS)
    with st.container():
        st.header("Companies:")
        for company in all_companies:
            st.subheader(f"{company.name} has {len(company.info)} roles\n")
            
            for idx, role in enumerate(company.info):
                st.markdown(f"{idx+1}. {role[COLUMNS[1]]}")
                
                for i in range (2, length-2):
                    
                    if role[COLUMNS[i]] != "Not Listed": st.markdown(f"{'&nbsp;'*8} {COLUMNS[i]}: {role[COLUMNS[i]]}") 
                    
                st.markdown(f"{'&nbsp;'*8} {COLUMNS[6]}: [Link]({role[COLUMNS[6]]})")

# LOADING ASSETS
lottie_url = "https://assets9.lottiefiles.com/packages/lf20_nk9kshb0.json"

# HEADER SECTION
with st.container():
    st.title("Job Search :briefcase:", hide_anchor_link())
    left_col, right_col = st.columns(2)
        
with st.container():
    st.info("Search for jobs in your area which are grouped by company")
    no_of_jobs = st.selectbox("Select the number of jobs you to search for: ", options=[1, 2, 3, 4])
    
with st.form("job_search"):
    
    location = st.text_input("Enter the city you want to search for jobs in: ", value="Singapore")
    
    job_titles = [None] * no_of_jobs
    
    for i in range(no_of_jobs):
        job_titles[i] = st.text_input(f"Enter the job title you want to search for: ", key=i)
    
    btn = st.form_submit_button("Search")
    
if btn:
    if all(job_titles) and location:
        with st.spinner("Searching for jobs..."):
            all_companies = project_main(job_titles, location)
        st.balloons()
        st.success("Done!")
        show_results(all_companies)
    else:
        fill_fields()

