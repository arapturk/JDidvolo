import requests
import os
from github import Github

# Örnek ülkeler ve M3U listesi URL'leri (gerçek URL'leri kendi kaynaklarınıza göre güncelleyin)
countries = {
    "turkey": "https://example.com/turkey.m3u",
    "usa": "https://example.com/usa.m3u",
    "germany": "https://example.com/germany.m3u",
    # Diğer ülkeler ekleyin...
}

def fetch_m3u(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch {url}")
        return ""

def ensure_m3u_extension(m3u_content):
    lines = m3u_content.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("http") and not line.endswith(".m3u"):
            if "?" in line:
                base, query = line.split("?", 1)
                base = base.rstrip("/") + ".m3u"
                new_line = base + "?" + query
            else:
                new_line = line.rstrip("/") + ".m3u"
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    return "\n".join(new_lines)

def update_github_repo(file_name, content, repo_name, token, commit_message="Update M3U list"):
    g = Github(token)
    repo = g.get_repo(repo_name)
    try:
        file = repo.get_contents(file_name)
        repo.update_file(file.path, commit_message, content, file.sha)
        print(f"{file_name} updated successfully.")
    except Exception as e:
        # Dosya yoksa oluştur
        repo.create_file(file_name, commit_message, content)
        print(f"{file_name} created successfully.")

def main():
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_NAME = "kullanici_adi/repo_adi"  # GitHub kullanıcı adı ve repo adı

    for country, url in countries.items():
        m3u_content = fetch_m3u(url)
        if m3u_content:
            updated_content = ensure_m3u_extension(m3u_content)
            file_name = f"{country}.m3u"
            update_github_repo(file_name, updated_content, REPO_NAME, GITHUB_TOKEN)

if __name__ == "__main__":
    main()
