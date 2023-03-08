import requests
import pandas as pd
import os

from cprint import cprint
from dotenv import load_dotenv

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
        data, columns=["Employer", "Job Title", "Publisher", "Apply Link"]
    )

    if os.path.exists("jobs.csv"):
        present_data = pd.read_csv("jobs.csv")
        df = pd.concat([present_data, df]).drop_duplicates().reset_index(drop=True)

    df.to_csv("jobs.csv", index=False)
    all_companies = store_jobs(df.to_dict("records"))
    get_companies(all_companies)


def jobs_to_get() -> int:

    while True:
        try:
            num = int(input("Enter the number of jobs you want to get: "))

            if num < 1:
                raise ValueError
            break

        except ValueError:
            print("Please enter a valid number")

    return (num,)


def job_titles_to_get(num: int) -> list:
    titles = []

    for _ in range(num):
        while True:
            title = input("Enter the job title you want to get: ")

            if title == "":
                print("Please enter a valid title")
            else:
                titles.append(title)
                break

    return titles


def job_location_to_get() -> str:

    while True:
        location = input("Enter the location you want to get jobs from: ")

        if location == "":
            print("Please enter a valid location")
        else:
            break

    return location


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
                    },
                    ignore_index=True,
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
        print(f"Company: {company.name} has {len(company.info)} roles")

        for role in company.info:
            print(f"Role: {role['role']}\nLink: {role['link']}\n")


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
