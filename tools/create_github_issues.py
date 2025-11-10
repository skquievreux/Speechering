#!/usr/bin/env python3
"""
GitHub Issues Creator
Erstellt automatisch alle Issues aus GITHUB_ISSUES.md via GitHub API

Verwendung:
    python scripts/create_github_issues.py

Benötigt:
    - GITHUB_TOKEN Environment-Variable oder .env
    - Repository: skquievreux/Speechering
"""

import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# HTTP-Client
try:
    import requests
except ImportError:
    print("ERROR: requests nicht installiert")
    print("Bitte ausführen: pip install requests")
    sys.exit(1)

# .env Support
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("WARNING: python-dotenv nicht installiert - verwende nur Environment-Variablen")


class GitHubIssueCreator:
    """Erstellt GitHub Issues via API"""

    def __init__(self, repo: str = "skquievreux/Speechering", token: str = None):
        self.repo = repo
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.api_base = "https://api.github.com"
        self.session = requests.Session()

        if not self.token:
            raise ValueError("GITHUB_TOKEN nicht gefunden in Environment oder .env")

        self.session.headers.update({
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Voice-Transcriber-Issue-Creator'
        })

    def parse_github_issues_md(self, filepath: Path) -> List[Dict]:
        """
        Parst GITHUB_ISSUES.md und extrahiert alle Issues

        Returns:
            List von Issue-Dictionaries
        """
        content = filepath.read_text(encoding='utf-8')

        issues = []
        current_issue = None

        # Regex für Issue-Heading
        issue_pattern = re.compile(r'^### Issue #(\d+): (.+)$', re.MULTILINE)

        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]

            # Finde Issue-Heading
            match = issue_pattern.match(line)
            if match:
                # Speichere vorheriges Issue
                if current_issue:
                    issues.append(current_issue)

                issue_num = match.group(1)
                issue_title = match.group(2)

                current_issue = {
                    'number': int(issue_num),
                    'title': issue_title,
                    'body': '',
                    'labels': []
                }

                # Sammle Body bis zum nächsten Issue oder Section-Ende
                i += 1
                body_lines = []

                while i < len(lines):
                    next_line = lines[i]

                    # Stop bei nächstem Issue
                    if issue_pattern.match(next_line):
                        break

                    # Stop bei neuem P-Level (## 🚨 P1, etc.)
                    if re.match(r'^## [🚨⚠️📋🎨]', next_line):
                        break

                    body_lines.append(next_line)
                    i += 1

                # Parse Body
                body = '\n'.join(body_lines).strip()

                # Extrahiere Labels aus Body
                labels_match = re.search(r'\*\*Labels:\*\*\s+(.+)', body)
                if labels_match:
                    labels_str = labels_match.group(1)
                    labels = [l.strip().strip('`') for l in labels_str.split(',')]
                    current_issue['labels'] = labels

                current_issue['body'] = body
                continue

            i += 1

        # Letztes Issue hinzufügen
        if current_issue:
            issues.append(current_issue)

        return issues

    def create_issue(self, title: str, body: str, labels: List[str] = None) -> Dict:
        """
        Erstellt ein GitHub Issue via API

        Returns:
            Response-JSON mit Issue-Daten
        """
        url = f"{self.api_base}/repos/{self.repo}/issues"

        data = {
            'title': title,
            'body': body
        }

        if labels:
            data['labels'] = labels

        response = self.session.post(url, json=data)
        response.raise_for_status()

        return response.json()

    def issue_exists(self, title: str) -> Tuple[bool, int]:
        """
        Prüft ob Issue mit diesem Titel bereits existiert

        Returns:
            (exists: bool, issue_number: int)
        """
        url = f"{self.api_base}/repos/{self.repo}/issues"
        params = {'state': 'all', 'per_page': 100}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        issues = response.json()

        for issue in issues:
            if issue['title'] == title:
                return True, issue['number']

        return False, 0

    def create_all_issues(self, issues: List[Dict], dry_run: bool = False):
        """
        Erstellt alle Issues

        Args:
            issues: Liste von Issue-Dicts
            dry_run: Wenn True, nur Preview ohne tatsächliches Erstellen
        """
        print(f"📋 Gefunden: {len(issues)} Issues\n")

        created_count = 0
        skipped_count = 0
        errors = []

        for i, issue in enumerate(issues, 1):
            title = issue['title']
            body = issue['body']
            labels = issue.get('labels', [])

            print(f"[{i}/{len(issues)}] Issue #{issue['number']}: {title}")

            if dry_run:
                print(f"  Labels: {', '.join(labels)}")
                print(f"  Body: {body[:100]}...")
                print(f"  ✅ (DRY RUN - nicht erstellt)\n")
                continue

            # Prüfe ob Issue bereits existiert
            exists, existing_number = self.issue_exists(title)
            if exists:
                print(f"  ⚠️  Übersprungen - existiert bereits als #{existing_number}\n")
                skipped_count += 1
                continue

            try:
                # Erstelle Issue
                result = self.create_issue(title, body, labels)
                created_issue_num = result['number']
                issue_url = result['html_url']

                print(f"  ✅ Erstellt als #{created_issue_num}")
                print(f"  🔗 {issue_url}\n")

                created_count += 1

                # Rate Limiting: Warte 1 Sekunde zwischen Requests
                if i < len(issues):
                    time.sleep(1)

            except requests.exceptions.HTTPError as e:
                error_msg = f"❌ Fehler bei Issue #{issue['number']}: {e}"
                print(f"  {error_msg}\n")
                errors.append(error_msg)
                continue

        # Zusammenfassung
        print("=" * 60)
        print(f"✅ Erfolgreich erstellt: {created_count}")
        print(f"⚠️  Übersprungen (existiert bereits): {skipped_count}")

        if errors:
            print(f"❌ Fehler: {len(errors)}")
            for error in errors:
                print(f"   {error}")


def main():
    """Hauptfunktion"""
    import argparse

    parser = argparse.ArgumentParser(description='Erstellt GitHub Issues aus GITHUB_ISSUES.md')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Zeigt nur Preview ohne tatsächliches Erstellen'
    )
    parser.add_argument(
        '--repo',
        default='skquievreux/Speechering',
        help='GitHub Repository (default: skquievreux/Speechering)'
    )
    parser.add_argument(
        '--token',
        default=None,
        help='GitHub Personal Access Token (default: $GITHUB_TOKEN)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("GitHub Issues Creator")
    print("=" * 60)
    print(f"Repository: {args.repo}")
    print(f"Dry Run: {args.dry_run}")
    print("=" * 60)
    print()

    # Finde GITHUB_ISSUES.md
    issues_file = Path(__file__).parent.parent / 'GITHUB_ISSUES.md'

    if not issues_file.exists():
        print(f"❌ FEHLER: {issues_file} nicht gefunden")
        sys.exit(1)

    try:
        # Erstelle Creator
        creator = GitHubIssueCreator(repo=args.repo, token=args.token)

        # Parse Issues
        print(f"📖 Lese {issues_file}...")
        issues = creator.parse_github_issues_md(issues_file)

        if not issues:
            print("⚠️  Keine Issues gefunden in GITHUB_ISSUES.md")
            sys.exit(0)

        # Erstelle Issues
        creator.create_all_issues(issues, dry_run=args.dry_run)

        print()
        print("✅ Fertig!")

    except ValueError as e:
        print(f"❌ FEHLER: {e}")
        print()
        print("Bitte GITHUB_TOKEN setzen:")
        print("  export GITHUB_TOKEN=ghp_xxxxxxxxxxxx")
        print("  oder .env erstellen mit GITHUB_TOKEN=...")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
