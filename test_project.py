import pytest
from project import store_jobs, Company, jobs_to_get, job_titles_to_get, job_location_to_get


@pytest.mark.parametrize(
    "all_jobs",
    [
        [
            {
                "Employer": "Google",
                "Job Title": "Software Engineer",
                "Publisher": "Google",
                "Apply Link": "https://google.com",
                "Expiry Date": "2021-08-31",
            },
            {
                "Employer": "Facebook",
                "Job Title": "Software Engineer",
                "Publisher": "Facebook",
                "Apply Link": "https://facebook.com",
                "Expiry Date": "2021-08-31",
            },
        ]
    ],
)
def test_store_jobs(all_jobs):
    all_companies = store_jobs(all_jobs)
    assert all_companies == [
        Company(
            all_jobs[each]["Employer"],
            {"role": all_jobs[each]["Job Title"], "link": all_jobs[each]["Apply Link"]},
        )
        for each in range(len(all_jobs))
    ]