"""
A module for obtaining repo readme and language data from the github API.
Before using this module, read through it, and follow the instructions marked
TODO.
After doing so, run it like this:
    python acquire.py
To create the `data.json` file that contains the data.
"""
import os
import json
from typing import Dict, List
import requests

from env import github_token, github_username

# TODO: Make a github personal access token.
#     1. Go here and generate a personal access token https://github.com/settings/tokens
#     2. Save it in your env.py file under the variable `github_token`
# TODO: Replace YOUR_GITHUB_USERNAME below with your github username.
# TODO: Add more repositories to the `repos` list.

repos = ["gocodeup/codeup-setup-script", "gocodeup/movies-application"]

headers = {
    "Authorization": f"token {github_token}",
    "User-Agent": github_username,
}

if (
    headers["Authorization"] == "token "
    or headers["User-Agent"] == "YOUR_GITHUB_USERNAME"
):
    raise Exception(
        "You need to follow the instructions marked TODO in this script before trying to use it"
    )


def github_api_request(url: str) -> requests.Response:
    return requests.get(url, headers=headers)


def get_repo_language(repo: str) -> str:
    url = f"https://api.github.com/repos/{repo}"
    return github_api_request(url).json()["language"]


def get_repo_languages(repo: str) -> str:
    url = f"https://api.github.com/repos/{repo}/languages"
    return github_api_request(url).json()


def get_repo_contents(repo: str) -> List[Dict[str, str]]:
    url = f"https://api.github.com/repos/{repo}/contents/"
    return github_api_request(url).json()


def get_readme_download_url(files: List[Dict[str, str]]) -> str:
    """
    Takes in a response from the github api that lists
    the files in a repo and returns the url that can be
    used to download the repo's README file.
    """
    for file in files:
        if file["name"].lower().startswith("readme"):
            return file["download_url"]


def process_repo(repo: str) -> Dict[str, str]:
    """
    Takes a repo name like "gocodeup/codeup-setup-script" and returns
    a dictionary with the language of the repo and the readme contents.
    """
    print(repo)
    contents = get_repo_contents(repo)
    readme_url = get_readme_download_url(contents)
    print(readme_url)
    readme_contents = requests.get(get_readme_download_url(contents)).text if readme_url else None
    
    return {
        "repo": repo,
        "language": get_repo_language(repo),
        "language_all": get_repo_languages(repo),
        "readme_contents": readme_contents,
    }


def scrape_github_data(repos=repos, filepath="data.json"):
    """
    Loop through all of the repos and process them. Saves the data in
    `data.json`.
    """
    data = [process_repo(repo) for repo in repos]
    json.dump(data, open(filepath, "w"))


if __name__ == "__main__":
    scrape_github_data()