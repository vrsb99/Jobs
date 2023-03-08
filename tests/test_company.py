import pytest
from src.company import Company


@pytest.mark.parametrize(
    ("name", "info"),
    [
        ("Google", {"role": "Software Engineer", "link": "https://google.com"}),
        ("Facebook", {"role": "Software Engineer", "link": "https://facebook.com"}),
    ],
)
def test_valid_company(name, info):
    company = Company(name, info)

    assert company.name == name
    assert company.info == [info]


@pytest.mark.parametrize(
    ("name", "info"),
    [
        ("Google", {"link": "https://google.com"}),
        ("Facebook", {"role": "Software Engineer"}),
    ],
)
def test_invalid_company(name, info):

    with pytest.raises(ValueError):
        Company(name, info)
