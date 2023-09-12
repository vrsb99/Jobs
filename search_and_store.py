import requests
import os
import psycopg2
import streamlit as st

from dotenv import load_dotenv
from typing import List
from postgres import connection

load_dotenv()
USE_API = True
JOB_TITLES = [
    "Software Engineer Intern",
    "Data Engineer Intern",
    "Data Science Intern",
    "Machine Learning Intern",
]
URL = "https://jsearch.p.rapidapi.com/search"
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
PATH = "jobs.csv"
COLUMNS = [
    "Employer",
    "Job Title",
    "Publisher",
    "Responsibilities",
    "Qualifications",
    "Max Salary",
    "Application Page",
    "Expiry Date",
    "Title Searched",
]


def main(titles: List[str] = JOB_TITLES, location: str = "Singapore"):
    """Change the value of DEBUG to True to use the default values for job titles and location
    1. Get the jobs from RapidAPI's JSearch API
    2. Store the jobs in the database, delete expired jobs and manage titles
    3. Get the jobs from the database and group them by company
    """

    # 1
    data = get_jobs(titles, location) if USE_API else []

    # 2
    ensure_table_exists(connection)
    store_database_jobs(connection, data) if USE_API else None

    # 3
    searched_jobs = get_database_jobs(connection, titles)
    grouped_jobs = group_jobs_by_company(searched_jobs)

    return grouped_jobs

@st.cache_data()
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
            "date_posted": "month",
        }
        response = requests.request("GET", URL, headers=headers, params=querystring)

        try:
            for job in response.json()["data"]:
                data.append(
                    {
                        COLUMNS[0]: job["employer_name"],
                        COLUMNS[1]: job["job_title"],
                        COLUMNS[2]: job["job_publisher"],
                        COLUMNS[3]: job["job_highlights"]["Responsibilities"]
                        if job["job_highlights"].get("Responsibilities")
                        else "Not Listed",
                        COLUMNS[4]: job["job_highlights"]["Qualifications"]
                        if job["job_highlights"].get("Qualifications")
                        else "Not Listed",
                        COLUMNS[5]: job["job_max_salary"]
                        if job["job_max_salary"]
                        else "Not Listed",
                        COLUMNS[6]: job["job_apply_link"],
                        COLUMNS[7]: job["job_offer_expiration_datetime_utc"].split("T")[
                            0
                        ]
                        if job["job_offer_expiration_datetime_utc"]
                        else None,
                        COLUMNS[8]: title,
                    }
                )
        except KeyError as e:
            print(e)
            break

    return data


def ensure_table_exists(_connection: psycopg2.extensions.connection) -> None:
    cursor = _connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            job_id SERIAL PRIMARY KEY,
            employer TEXT,
            job_title TEXT,
            job_publisher TEXT,
            responsibilities TEXT,
            qualifications TEXT,
            max_salary TEXT,
            apply_link TEXT,
            expiry_date DATE,
            title_searched TEXT[],
            CONSTRAINT unique_job UNIQUE (employer, job_title)
        );
        """
    )
    _connection.commit()
    cursor.close()


@st.cache_resource()
def store_database_jobs(
    _connection: psycopg2.extensions.connection, data: list
) -> None:
    cursor = _connection.cursor()

    # Delete expired jobs
    cursor.execute("DELETE FROM jobs WHERE expiry_date < NOW()")
    _connection.commit()
    
    # Insert new jobs without duplicates and manage titles
    for job in data:
        title_searched = job.pop("Title Searched")

        cursor.execute(
            """
            INSERT INTO jobs (employer, job_title, job_publisher, responsibilities, qualifications, max_salary, apply_link, expiry_date, title_searched)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, ARRAY[%s])
            ON CONFLICT ON CONSTRAINT unique_job
            DO UPDATE SET title_searched = array_append(jobs.title_searched, EXCLUDED.title_searched[1])
            RETURNING job_id;
            """,
            tuple(job.values()) + (title_searched,),
        )

    _connection.commit()
    cursor.close()


@st.cache_data()
def get_database_jobs(
    _connection: psycopg2.extensions.connection, titles: List[str]
) -> list:
    cursor = _connection.cursor()
    cursor.execute(
        """
        SELECT DISTINCT ON (employer, job_title) employer, job_title, job_publisher, responsibilities, qualifications, max_salary, apply_link, expiry_date
        FROM jobs
        WHERE title_searched && %s
        ORDER BY employer, job_title, expiry_date DESC;
        """,
        (titles,),
    )
    database_jobs = cursor.fetchall()
    cursor.close()

    return database_jobs

@st.cache_data()
def group_jobs_by_company(database_jobs: list) -> dict:
    grouped_jobs = {}

    for job in database_jobs:
        company_name = job[0]

        if company_name not in grouped_jobs:
            grouped_jobs[company_name] = []

        grouped_jobs[company_name].append(
            {
                "Job Title": job[1],
                "Publisher": job[2],
                "Responsibilities": job[3],
                "Qualifications": job[4],
                "Max Salary": job[5],
                "Application Page": job[6],
                "Expiry Date": job[7],
            }
        )

    return grouped_jobs


if __name__ == "__main__":
    main()
