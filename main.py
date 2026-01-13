"""
Third project to Engeto Online Python Academy
author: Monika Kiskova
email: stastnamona@seznam.cz
"""

import csv
import sys
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.volby.cz/pls/ps2017nss/"


def get_args(argv: list) -> tuple:
    """
    Function parses and validates arguments.
    Parameters: argv (list): List of arguments. All arguments are strings.
    Return: tuple: Strings on first and second index of the list included in tuple (url and output csv).
    Example:
    >>> arguments = get_args(['C:\\Users\\...\\main.py', 'https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101', 'vysledky_benesov.csv'])
    >>> arguments = ('https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101', 'vysledky_benesov.csv')
    """
    if len(argv) != 3:
        raise ValueError("Two arguments are necessary (url and csv name).")
    first_arg, second_arg = argv[1].strip(), argv[2].strip()
    if first_arg.lower().endswith(".csv") and second_arg.startswith("https"):
        raise ValueError("Arguments are probably swapped (firstly url, secondly csv).")
    if not first_arg.lower().startswith("https"):
        raise ValueError("First argument must be an url that starts with https.")
    if not second_arg.lower().endswith(".csv"):
        raise ValueError("Second argument must be a csv file name ending .csv.")
    return first_arg, second_arg


def load_page(url: str) -> BeautifulSoup:
    """
    Function downloads a page.
    Parameters: url (str): Specific url used as the first argument.
    Return: BeautifulSoup: Appropriate part of url dedicated for scrapping.
    """
    response = requests.get(url)
    return BeautifulSoup(response.text, features="html.parser")


def to_int(text: str) -> int:
    """
    Function converts number written as text to integer. It keeps only digits without spaces.
    Parameters: text (str): Number written as string.
    Return: int: Number written as integer.
    Example:
    >>> number = to_int('13 104')
    >>> number = 13104
    """
    text_to_list = text.split()
    join_list = "".join(text_to_list)
    number_of_votes = int(join_list)
    return number_of_votes


def get_municipalities(url: str) -> list:
    """
    Function scrapes municipality code, municipality name and results url from a page.
    Parameters: url (str): Specific url used as the first argument.
    Return: list: List of all municipalities found on a specific page. Details of each municipality are included in dicts.
    """
    page = load_page(url)
    municipalities = []
    all_rows = page.find_all("tr")
    for row in all_rows:
        columns = row.find_all("td")
        if len(columns) < 2:
            continue
        a_href = columns[0].find("a")
        if not a_href:
            continue
        code = a_href.get_text(strip=True)
        href = a_href.get("href", "")
        if not code.isdigit():
            continue
        name = columns[1].get_text()
        municipalities.append(
            {"code": code, "name": name, "url": urljoin(BASE_URL, href)}
        )
    if not municipalities:
        raise ValueError("A list of municipalities is not found on the page.")
    return municipalities


def parse_summary(page: BeautifulSoup) -> tuple:
    """
    Function parses and validates summary table. Returns registered voters, envelopes issued and valid votes from a results page.
    """
    table = next(
        (
            page_table
            for page_table in page.find_all("table")
            if "Voliči v seznamu" in page_table.get_text(" ", strip=True)
        ),
        None,
    )
    if not table:
        raise ValueError("Summary table not found.")
    data_rows = [tr for tr in table.find_all("tr") if tr.find_all("td")]
    if not data_rows:
        raise ValueError("Summary table is empty.")
    cells = [td.get_text() for td in data_rows[-1].find_all("td")]
    if len(cells) < 8:
        raise ValueError("Summary table does not have appropriate format.")
    return to_int(cells[3]), to_int(cells[4]), to_int(cells[7])


def parse_party_votes(page: BeautifulSoup) -> dict:
    """
    Function provides electoral party names and number of votes for each party.
    Parameters: page (BeautifulSoup): Appropriate part of url dedicated for scrapping.
    Return: dict: Combination of electoral party names and number of votes of each party.
    """
    party_votes = {}
    all_tables = page.find_all("table")
    for table in all_tables:
        text = table.get_text()
        if ("Strana" not in text) or ("Platné hlasy" not in text):
            continue
        for row in table.find_all("tr"):
            columns = row.find_all("td")
            if len(columns) < 3 or not columns[0].get_text().isdigit():
                continue
            party_name = columns[1].get_text()
            party_votes[party_name] = to_int(columns[2].get_text())
    if not party_votes:
        raise ValueError("Voting results not found on municipality page.")
    return party_votes


def scrape_municipality(municipality: dict) -> tuple:
    """
    Function downloads and parses one municipality results page. Returns results of functions parse_party_votes() and parse_summary().
    """
    page = load_page(municipality["url"])
    votes = parse_party_votes(page)
    summary = parse_summary(page)
    return votes, summary


def scrape_all(municipalities):
    """
    Function scrapes all municipalities.
    """
    rows = []
    party_names = []
    for municipality in municipalities:
        party_votes, (registered, envelopes, valid) = scrape_municipality(municipality)
        for party in party_votes:
            if party not in party_names:
                party_names.append(party)
        row = {
            "Code": municipality["code"],
            "Location": municipality["name"],
            "Registered voters": registered,
            "Envelopes issued": envelopes,
            "Valid votes": valid,
        }
        row.update(party_votes)
        rows.append(row)
    return rows, party_names


def save_csv(filename: str, rows: list, party_names: list) -> int:
    """
    Function saves rows to csv and returns number of written data rows.
    """
    base_columns = [
        "Code",
        "Location",
        "Registered voters",
        "Envelopes issued",
        "Valid votes",
    ]
    header = base_columns + party_names
    with open(filename, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, 0) for key in header})
    return len(rows)


def main():
    try:
        url, output_file = get_args(sys.argv)
        print(f"Downloading data from: {url}")
        municipalities = get_municipalities(url)
        rows, parties = scrape_all(municipalities)
        written = save_csv(output_file, rows, parties)
        print(
            f"Downloading completed. Saved as {output_file} (number of rows: {written})."
        )
    except ValueError as error:
        print(f"ERROR: {error}")
        sys.exit(1)
    except requests.RequestException as error:
        print(f"Downloading ERROR: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
