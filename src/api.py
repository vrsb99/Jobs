import requests
import pandas as pd
import os

from cprint import cprint
from dotenv import load_dotenv
from datetime import datetime
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


def main():

    if not DEBUG:
        num = jobs_to_get()
        titles = job_titles_to_get(num)
        location = job_location_to_get()
    else:
        titles = JOB_TITLES
        location = "Singapore"

    data = get_jobs(titles, location) if USE_API else []
    df = pd.DataFrame(
        data, columns=["Employer", "Job Title", "Publisher", "Apply Link", "Expiry Date"]
    )

    if os.path.exists("jobs.csv"):
        present_data = pd.read_csv("jobs.csv")
        present_data["Expiry Date"] = pd.to_datetime(present_data["Expiry Date"])
        df = pd.concat([present_data, df]).drop_duplicates(["Employer", "Job Title"]).reset_index(drop=True)
        df = df[(df["Expiry Date"].dt.date > pd.Timestamp.now().date()) & (~df["Expiry Date"].isnull())].reset_index(drop=True)

    df.to_csv("jobs.csv", index=False)
    all_companies = store_jobs(df.to_dict("records"))
    get_companies(all_companies)


def get_jobs(titles: list, location: str) -> list:

    data = []
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }

    for title in titles:
        querystring = {
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
                        "Expiry Date": job["job_offer_expiration_datetime_utc"].split("T")[0] if job["job_offer_expiration_datetime_utc"] else None,
                    }
                )
        except KeyError:
            cprint.err("API Limit Reached")
            break

    return data


def store_jobs(all_jobs: list) -> list:
    all_companies = []
    
    for job in all_jobs:

        try:
            index = [c.name for c in all_companies].index(job["Employer"])
            all_companies[index].add_info(
                {"role": job["Job Title"], "link": job["Apply Link"]}
            )
        except ValueError:
            all_companies.append(
                Company(
                    job["Employer"],
                    {"role": job["Job Title"], "link": job["Apply Link"]},
                )
            )

    return all_companies


def get_companies(all_companies: list):
    for company in all_companies:
        cprint.ok(f"Company: {company.name} has {len(company.info)} roles\n")

        for role in company.info:
            cprint.info(f"Role: {role['role']}\nLink: {role['link']}\n")


class Company:
    def __init__(self, name: str, info: dict):
        self.name = name
        self._info = [info]

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, info: dict):
        if all(key in info for key in ["role", "link"]):
            self._info = [info]
        else:
            cprint.err("Invalid info. Check Code")

    def add_info(self, info):
        if all(key in info for key in ["role", "link"]):
            self._info.append(info)
        else:
            cprint.err("Invalid info. Check Code")


if __name__ == "__main__":
    main()
