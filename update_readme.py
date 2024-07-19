import os
import requests
from collections import defaultdict
import logging

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
README_FILE = 'README.md'

logging.basicConfig(level=logging.INFO)

def get_repos(username, token):
    repos = []
    page = 1
    while True:
        url = f'https://api.github.com/users/{username}/repos?page={page}&per_page=100'
        headers = {'Authorization': f'token {token}'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logging.error(f'Error fetching repositories: {response.status_code}')
            logging.error(f'Response content: {response.text}')
            raise Exception(f'Error fetching repositories: {response.status_code}')
        current_page_repos = response.json()
        if not current_page_repos:
            break
        repos.extend(current_page_repos)
        page += 1
    logging.info(f'Fetched {len(repos)} repositories')
    return repos

def get_languages(username, token, repos):
    languages = defaultdict(int)
    for repo in repos:
        url = f'https://api.github.com/repos/{username}/{repo["name"]}/languages'
        headers = {'Authorization': f'token {token}'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logging.warning(f'Error fetching languages for {repo["name"]}: {response.status_code}')
            continue
        repo_languages = response.json()
        for lang, bytes_of_code in repo_languages.items():
            languages[lang] += bytes_of_code
    logging.info(f'Fetched languages: {dict(languages)}')
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
                for lang, bytes_of_code in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                    file.write(f'- {lang}: {bytes_of_code} bytes\n')
                file.write('<!--END_SECTION:languages-->\n')
            elif line.strip() == '<!--END_SECTION:languages-->':
                in_section = False
            elif not in_section:
                file.write(line)
    logging.info('README updated successfully')

def main():
    logging.info('Starting script execution')
    repos = get_repos(GITHUB_USERNAME, GITHUB_TOKEN)
    languages = get_languages(GITHUB_USERNAME, GITHUB_TOKEN, repos)
    update_readme(languages)
    logging.info('Script execution completed')

if __name__ == "__main__":
    main()
