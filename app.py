import streamlit as st
import requests

from search_and_store import main as project_main

# CONFIG
st.set_page_config(page_title="Job Search", page_icon=":briefcase:")

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
    
def show_results(all_companies: dict):
    with st.container():
        st.markdown("Use this website as a tool to find jobs grouped by company. But it is recommended to apply for jobs on the company's website.")
        st.markdown("## Companies:")
        
        for company_name, roles in all_companies.items():
            length = len(roles)
            st.markdown(f"### {company_name} has {length} roles\n")
            
            for idx, role in enumerate(roles):
                st.markdown(f"{idx+1}. Job Title: {role['Job Title']}")
                
                for key, value in role.items():
                    if key not in ["Job Title", "Application Page"] and value is not None and value != "Not Listed":
                        st.markdown(f"{'&nbsp;'*8} {key}: {value}")

                st.markdown(f"{'&nbsp;'*8} Application Page: [Link]({role['Application Page']})")


# LOADING ASSETS
lottie_url = "https://assets9.lottiefiles.com/packages/lf20_nk9kshb0.json"

# HEADER SECTION
with st.container():
    st.title("Job Search :briefcase:", hide_anchor_link())
    left_col, right_col = st.columns(2)
        
with st.container():
    st.info("Search for jobs in your area which are grouped by company")
    no_of_jobs = st.selectbox("Select the number of jobs you want to search for: ", options=[1, 2, 3, 4])
    
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

