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
        headers = {'Authorization': f'token {token}'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f'Error fetching repositories: {response.status_code}')
        current_page_repos = response.json()
        if not current_page_repos:
            break
        repos.extend([repo for repo in current_page_repos if not repo['fork']])
        page += 1
    return repos

def get_languages(username, token, repos):
    languages = defaultdict(int)
    total_bytes = 0
    for repo in repos:
        url = f'https://api.github.com/repos/{username}/{repo["name"]}/languages'
        headers = {'Authorization': f'token {token}'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            continue
        repo_languages = response.json()
        for lang, bytes_of_code in repo_languages.items():
            languages[lang] += bytes_of_code
            total_bytes += bytes_of_code
    
    # Convert to percentages
    language_percentages = {lang: (bytes_of_code / total_bytes) * 100 for lang, bytes_of_code in languages.items()}
    return language_percentages

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
                for lang, percentage in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                    file.write(f'- {lang}: {percentage:.2f}%\n')
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
