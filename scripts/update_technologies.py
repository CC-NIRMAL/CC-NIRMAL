import os
import re
from github import Github

# Use the automatically provided GITHUB_TOKEN
token = os.getenv("GH_TOKEN")
if not token:
    raise ValueError("No GH_TOKEN found")

g = Github(token)
user = g.get_user()
username = user.login

# Collect all languages from all repos (including private if token has access)
languages = {}
for repo in user.get_repos():
    # Skip forks if you want only your original projects
    # if repo.fork: continue
    repo_langs = repo.get_languages()
    for lang, bytes_count in repo_langs.items():
        languages[lang] = languages.get(lang, 0) + bytes_count

# Sort by bytes descending
sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)

# Generate markdown: badges using shields.io
badges = []
for lang, bytes_count in sorted_langs[:20]:  # show top 20
    # encode language name for URL
    encoded = lang.replace(" ", "%20").replace("#", "%23")
    badge = f"![{lang}](https://img.shields.io/badge/{encoded}-{bytes_count // 1024}KB-blue?logo={encoded}&logoColor=white)"
    badges.append(badge)

# Create a nice table (3 badges per row) to save space
rows = []
for i in range(0, len(badges), 3):
    row = " ".join(badges[i:i+3])
    rows.append(f"| {row} |")
    
if rows:
    tech_table = "| Technologies |\n|--------------|\n" + "\n".join(rows)
else:
    tech_table = "No languages detected yet. Push some code! 🚀"

# Read the current README
readme_path = "README.md"
with open(readme_path, "r") as f:
    content = f.read()

# Replace the content between <!-- TECH_START --> and <!-- TECH_END -->
pattern = r"(<!-- TECH_START -->\n).*?(\n<!-- TECH_END -->)"
replacement = r"\1" + tech_table + r"\2"
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open(readme_path, "w") as f:
    f.write(new_content)

print("Technologies section updated successfully.")
