import requests
import pandas as pd
import os

from cprint import cprint
from dotenv import load_dotenv
from typing import List

load_dotenv()
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
COLUMNS = ["Employer", "Job Title", "Publisher", "Responsibilities", "Qualifications", "Max Salary", "Application Page", "Expiry Date"]


def main(titles: List[str] = JOB_TITLES, location: str = "Singapore"):
    """Change the value of DEBUG to True to use the default values for job titles and location
    1. Get the jobs from RapidAPI's JSearch API
    2. Store the jobs in a csv file after removing duplicates and expired jobs
    3. Store the jobs in a list of Company objects
    4. Print the companies
    """

    # 1
    data = get_jobs(titles, location) if USE_API else []

    # 2
    df = pd.DataFrame(
        data,
        columns= COLUMNS
    )

    if os.path.exists(PATH):
        present_data = pd.read_csv(PATH)
        df = (
            pd.concat([present_data, df])
            .drop_duplicates(["Employer", "Job Title"])
            .reset_index(drop=True)
        )
        
        df["Expiry Date"] = pd.to_datetime(df["Expiry Date"])
        
        df = df[
            (df["Expiry Date"].dt.date > pd.Timestamp.now().date())
            & (~df["Expiry Date"].isnull())
        ].reset_index(drop=True)

    df.to_csv(PATH, index=False)

    # 3
    all_companies = store_jobs(df.to_dict("records"))
    # 4
    return all_companies


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
                        COLUMNS[0]: job["employer_name"],
                        COLUMNS[1]: job["job_title"],
                        COLUMNS[2]: job["job_publisher"],
                        COLUMNS[3]: job["job_highlights"]["Responsibilities"] if job["job_highlights"].get("Responsibilities") else "Not Listed",
                        COLUMNS[4]: job["job_highlights"]["Qualifications"] if job["job_highlights"].get("Qualifications") else "Not Listed",
                        COLUMNS[5]: job["job_max_salary"] if job["job_max_salary"] else "Not Listed",
                        COLUMNS[6]: job["job_apply_link"],
                        COLUMNS[7]: job["job_offer_expiration_datetime_utc"].split(
                            "T"
                        )[0]
                        if job["job_offer_expiration_datetime_utc"]
                        else None,
                    }
                )
        except KeyError as e:
            cprint.err("error", e)
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
    length = len(COLUMNS)

    for job in all_jobs:

        if job[COLUMNS[0]] in [c.name for c in all_companies]:
            index = [c.name for c in all_companies].index(job[COLUMNS[0]])
            all_companies[index].add_info(
                {COLUMNS[i]: job[COLUMNS[i]] for i in range(1, length)}
            )
        else:
            all_companies.append(
                Company(
                    job[COLUMNS[0]],
                    {COLUMNS[i]: job[COLUMNS[i]] for i in range(1, length)},
                )
            )

    return all_companies

class Company:
    def __init__(self, name: str, info: dict):
        self.name = name
        self.info = info

    def __eq__(self, other):
        return self.name == other.name and self.info == other.info

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, info: dict):
        if all(key in info for key in COLUMNS[1:]):
            self._info = [info]
        else:
            raise ValueError("Invalid info. Check Code")

    def add_info(self, info):
        if all(key in info for key in COLUMNS[1:]):
            self._info.append(info)
        else:
            raise ValueError("Invalid info. Check Code")

if __name__ == "__main__":
    main()
