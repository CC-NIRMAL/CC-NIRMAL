import os
import re
import sys

from github import Github


def shields_escape(text: str) -> str:
    """Escape a string for use inside a shields.io static badge segment.

    Shields treats '-' and '_' specially, so they must be doubled; other
    characters that break URLs are percent-encoded. This handles names like
    'C#', 'C++', and 'Objective-C' correctly.
    """
    return (
        text.replace("-", "--")
        .replace("_", "__")
        .replace(" ", "%20")
        .replace("#", "%23")
        .replace("+", "%2B")
    )


def main() -> None:
    token = os.getenv("GH_TOKEN")
    if not token:
        sys.exit("Error: GH_TOKEN environment variable is not set.")

    gh = Github(token)
    user = gh.get_user()
    print(f"Authenticated as: {user.login}")

    # Aggregate language byte counts across every repo the token can see.
    languages: dict[str, int] = {}
    for repo in user.get_repos(type="owner"):
        if repo.fork:  # skip forks so the stats reflect your own code
            continue
        try:
            for lang, byte_count in repo.get_languages().items():
                languages[lang] = languages.get(lang, 0) + byte_count
        except Exception as exc:  # empty repo, access issue, etc.
            print(f"  Skipped {repo.name}: {exc}")

    # Sort by total bytes (most used first) and keep the top 20.
    top = sorted(languages.items(), key=lambda kv: kv[1], reverse=True)[:20]

    if top:
        badges = [
            f'<img src="https://img.shields.io/badge/'
            f'{shields_escape(lang)}-{byte_count // 1024}KB-blue?style=flat-square" '
            f'alt="{lang}" />'
            for lang, byte_count in top
        ]
        # Lay the badges out 3 per row inside a centered block.
        rows = ["".join(badges[i:i + 3]) for i in range(0, len(badges), 3)]
        tech_block = '<p align="center">\n  ' + "<br>\n  ".join(rows) + "\n</p>"
    else:
        tech_block = "_No language data yet — go push some code!_ 🚀"

    readme_path = "README.md"
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"(<!-- TECH_START -->\n).*?(\n<!-- TECH_END -->)"
    if not re.search(pattern, content, flags=re.DOTALL):
        sys.exit("Error: TECH_START / TECH_END markers not found in README.md.")

    new_content = re.sub(
        pattern,
        lambda m: m.group(1) + tech_block + m.group(2),
        content,
        flags=re.DOTALL,
    )

    if new_content == content:
        print("Technologies section already up to date — nothing to commit.")
        return

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("README.md technologies section updated.")


if __name__ == "__main__":
    main()
