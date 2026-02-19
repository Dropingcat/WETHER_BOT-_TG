# scripts/generate_changelog.py
import subprocess
import re
from collections import defaultdict

def get_commits():
    """Получает коммиты из Git в формате conventional commits."""
    result = subprocess.run(
        ["git", "log", "--oneline", "--no-decorate"],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    return result.stdout.strip().split("\n")

def parse_commit(line):
    """Парсит строку коммита: 'feat(weather): add simulator' → (type, scope, desc)"""
    match = re.match(r"^(feat|fix|refactor|docs|test|chore)(?:\((\w+)\))?:\s*(.+)", line)
    if match:
        return match.group(1), match.group(2) or "", match.group(3)
    return None, None, None

def main():
    commits = get_commits()
    changes = defaultdict(list)
    
    for line in commits:
        typ, scope, desc = parse_commit(line)
        if typ and desc:
            if typ == "feat":
                changes["Added"].append(f"- {desc}")
            elif typ == "fix":
                changes["Fixed"].append(f"- {desc}")
            elif typ == "refactor":
                changes["Changed"].append(f"- {desc}")
    
    # Вывод в формате CHANGELOG.md
    print("## [Unreleased]\n")
    for section, items in changes.items():
        if items:
            print(f"### {section}\n")
            for item in items:
                print(item)
            print()

if __name__ == "__main__":
    main()