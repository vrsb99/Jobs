import pytest
from inputs import jobs_to_get, job_titles_to_get, job_location_to_get


@pytest.mark.parametrize("num", [i for i in range(1, 10)])
def test_jobs_to_get_working_inputs(monkeypatch, num):
    monkeypatch.setattr("builtins.input", lambda _: num)

    assert jobs_to_get() == num


@pytest.mark.parametrize(
    "num, title",
    [
        (1, ["Software Engineer Intern"]),
        (2, ["Data Science Intern", "Data Engineer Intern"]),
    ],
)
def test_job_titles_to_get_working_titles(monkeypatch, num, title):
    each = iter(title)
    monkeypatch.setattr("builtins.input", lambda _: next(each))

    assert job_titles_to_get(num) == title


@pytest.mark.parametrize("location", ["Singapore", "Malaysia", "Indonesia"])
def test_job_location_to_get_working_location(monkeypatch, location):
    monkeypatch.setattr("builtins.input", lambda _: location)

    assert job_location_to_get() == location
