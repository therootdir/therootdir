import os
import requests
from collections import defaultdict

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
README_FILE = 'README.md'

def get_repos(username, token):
    repos = []
    page = 1
    while True:
        url = f'https://api.github.com/user/repos?page={page}&per_page=100'
        response = requests.get(url, auth=(username, token))
        if response.status_code != 200:
            raise Exception(f'Error fetching repositories: {response.status_code}')
        current_page_repos = response.json()
        if not current_page_repos:
            break
        repos.extend(current_page_repos)
        page += 1
    return repos

def get_languages(username, token, repos):
    languages = defaultdict(int)
    for repo in repos:
        url = f'https://api.github.com/repos/{username}/{repo["name"]}/languages'
        response = requests.get(url, auth=(username, token))
        if response.status_code != 200:
            continue
        repo_languages = response.json()
        for lang, bytes_of_code in repo_languages.items():
            languages[lang] += bytes_of_code
    return languages

def update_readme(languages):
    with open(README_FILE, 'r') as file:
        lines = file.readlines()

    with open(README_FILE, 'w') as file:
        in_section = False
        for line in lines:
            if line.strip() == '<!--START_SECTION:languages-->':
                in_section = True
                file.write(line)
                file.write('\n')
                for lang, bytes_of_code in languages.items():
                    file.write(f'- {lang}: {bytes_of_code} bytes\n')
                file.write('<!--END_SECTION:languages-->\n')
            elif line.strip() == '<!--END_SECTION:languages-->':
                in_section = False
            elif not in_section:
                file.write(line)

def main():
    repos = get_repos(GITHUB_USERNAME, GITHUB_TOKEN)
    languages = get_languages(GITHUB_USERNAME, GITHUB_TOKEN, repos)
    update_readme(languages)

if __name__ == "__main__":
    main()
