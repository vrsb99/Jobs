import requests
import pandas as pd
import os

from cprint import cprint
from dotenv import load_dotenv
from inputs import jobs_to_get, job_titles_to_get, job_location_to_get
from company import Company

load_dotenv()
DEBUG = True
USE_API = False
JOB_TITLES = [
    "Software Engineer Intern",
    "Data Engineer Intern",
    "Data Science Intern",
    "Machine Learning Intern",
]
URL = "https://jsearch.p.rapidapi.com/search"
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
PATH = "jobs.csv"


def main():
    """Change the value of DEBUG to True to use the default values for job titles and location
    1. Get the number of jobs to get
    2. Get the job titles to get
    3. Get the location to get jobs from
    4. Get the jobs from RapidAPI's JSearch API
    5. Store the jobs in a csv file after removing duplicates and expired jobs
    6. Store the jobs in a list of Company objects
    8. Print the companies
    """
    # 1, 2, 3
    if not DEBUG:
        num = jobs_to_get()
        titles = job_titles_to_get(num)
        location = job_location_to_get()
    else:
        titles = JOB_TITLES
        location = "Singapore"

    # 4
    data = get_jobs(titles, location) if USE_API else []

    # 5
    df = pd.DataFrame(
        data,
        columns=["Employer", "Job Title", "Publisher", "Apply Link", "Expiry Date"],
    )

    if os.path.exists(PATH):
        present_data = pd.read_csv(PATH)
        present_data["Expiry Date"] = pd.to_datetime(present_data["Expiry Date"])
        df = (
            pd.concat([present_data, df])
            .drop_duplicates(["Employer", "Job Title"])
            .reset_index(drop=True)
        )
        df = df[
            (df["Expiry Date"].dt.date > pd.Timestamp.now().date())
            & (~df["Expiry Date"].isnull())
        ].reset_index(drop=True)

    df.to_csv(PATH, index=False)

    # 6
    all_companies = store_jobs(df.to_dict("records"))
    # 7
    get_companies(all_companies)


def get_jobs(titles: list, location: str) -> list:
    """Receives the jobs in json format from RapidAPI's JSearch API

    Args:
        titles (list): job titles to search for
        location (str): location to search for jobs

    Returns:
        list: list of jobs in a dictionary format
    """

    data = []
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }

    for title in titles:
        querystring: dict = {
            "query": f"{title} in {location}",
            "page": "1",
            "num_pages": "10",
            "date_posted": "week",
        }
        response = requests.request("GET", URL, headers=headers, params=querystring)

        try:
            for job in response.json()["data"]:
                data.append(
                    {
                        "Employer": job["employer_name"],
                        "Job Title": job["job_title"],
                        "Publisher": job["job_publisher"],
                        "Apply Link": job["job_apply_link"],
                        "Expiry Date": job["job_offer_expiration_datetime_utc"].split(
                            "T"
                        )[0]
                        if job["job_offer_expiration_datetime_utc"]
                        else None,
                    }
                )
        except KeyError:
            cprint.err("API Limit Reached")
            break

    return data


def store_jobs(all_jobs: list) -> list:
    """Stores jobs in a list of Company objects

    Args:
        all_jobs (list): list of jobs in a dictionary format

    Returns:
        list: list of jobs in a Company object format
    """
    all_companies: list = []

    for job in all_jobs:

        if job["Employer"] in [c.name for c in all_companies]:
            index = [c.name for c in all_companies].index(job["Employer"])
            all_companies[index].add_info(
                {"role": job["Job Title"], "link": job["Apply Link"]}
            )
        else:
            all_companies.append(
                Company(
                    job["Employer"],
                    {"role": job["Job Title"], "link": job["Apply Link"]},
                )
            )

    return all_companies


def get_companies(all_companies: list):
    """Prints out all the companies and their roles

    Args:
        all_companies (list): list of jobs in a Company object format
    """
    for company in all_companies:
        cprint.ok(f"Company: {company.name} has {len(company.info)} roles\n")

        for role in company.info:
            cprint.info(f"Role: {role['role']}\nLink: {role['link']}\n")


if __name__ == "__main__":
    main()
