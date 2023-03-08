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