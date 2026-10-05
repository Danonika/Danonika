"""Publish aggregate line changes; never persist private repository metadata."""
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request


REPOSITORIES = """
query Repositories($login: String!, $cursor: String) {
  user(login: $login) {
    id
    repositories(first: 100, after: $cursor, isFork: false,
      ownerAffiliations: [OWNER, ORGANIZATION_MEMBER, COLLABORATOR]) {
      nodes { defaultBranchRef { target { ... on Commit { id } } } }
      pageInfo { hasNextPage endCursor }
    }
  }
}
"""
HISTORY = """
query History($id: ID!, $author: ID!, $cursor: String,
              $since: GitTimestamp!, $until: GitTimestamp!) {
  node(id: $id) {
    ... on Commit {
      history(first: 100, after: $cursor, author: {id: $author},
              since: $since, until: $until) {
        nodes { oid additions deletions parents(first: 2) { totalCount } }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}
"""


def graphql(query, variables):
    request = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': query, 'variables': variables}).encode(),
        headers={'Authorization': 'Bearer ' + os.environ['STATS_TOKEN'],
                 'Content-Type': 'application/json',
                 'User-Agent': 'Danonika-profile-stats'},
        method='POST',
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                result = json.load(response)
            break
        except urllib.error.HTTPError as error:
            if error.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f'GitHub API returned HTTP {error.code}; no totals published.') from None
        except (urllib.error.URLError, TimeoutError):
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError('GitHub API unavailable; no totals published.') from None
    # Do not print raw API errors: they may contain private repository details.
    if result.get('errors') or not result.get('data'):
        raise RuntimeError('GitHub GraphQL query failed; no partial totals published.')
    return result['data']


def next_cursor(connection, previous):
    page = connection['pageInfo']
    if not page['hasNextPage']:
        return None
    cursor = page['endCursor']
    if not cursor or cursor == previous:
        raise RuntimeError('Incomplete GitHub pagination; no partial totals published.')
    return cursor


def collect(login, since, until, query=graphql):
    heads, author, cursor = [], None, None
    while True:
        user = query(REPOSITORIES, {'login': login, 'cursor': cursor})['user']
        if not user:
            raise RuntimeError('Profile account not found.')
        author = user['id']
        repositories = user['repositories']
        for repo in repositories['nodes']:
            if repo is None:
                raise RuntimeError('Incomplete repository response; no totals published.')
            branch = repo['defaultBranchRef']
            if branch:
                heads.append(branch['target']['id'])
        cursor = next_cursor(repositories, cursor)
        if cursor is None:
            break

    seen, additions, deletions = set(), 0, 0
    for head in heads:
        cursor = None
        while True:
            node = query(HISTORY, {'id': head, 'author': author, 'cursor': cursor,
                                  'since': since, 'until': until})['node']
            if not node or 'history' not in node:
                raise RuntimeError('Commit history unavailable; no partial totals published.')
            history = node['history']
            for commit in history['nodes']:
                if not commit:
                    raise RuntimeError('Incomplete commit response; no totals published.')
                if commit['parents']['totalCount'] > 1 or commit['oid'] in seen:
                    continue
                for key in ('additions', 'deletions'):
                    if type(commit[key]) is not int or commit[key] < 0:
                        raise RuntimeError('Invalid line count; no totals published.')
                seen.add(commit['oid'])
                additions += commit['additions']
                deletions += commit['deletions']
            cursor = next_cursor(history, cursor)
            if cursor is None:
                break
    return {'additions': additions, 'deletions': deletions,
            'commits': len(seen), 'since': since, 'until': until}


def render(stats, dark=False):
    bg, border, title, muted = (
        ('0b1220', '233950', '67e8f9', 'a8bbcf') if dark else
        ('f8fbff', 'cddfed', '087fa3', '52677e'))
    added, removed = ('3fb950', 'ff7b72') if dark else ('1a7f37', 'cf222e')
    plus, minus = f"+{stats['additions']:,}", f"−{stats['deletions']:,}"
    font_size = min(32, 290 // max(len(plus), len(minus)))
    period = stats['since'][:10] + ' — ' + stats['until'][:10]
    description = escape(f"{stats['additions']:,} lines added and {stats['deletions']:,} lines deleted. "
                         f"{period}. Authored non-merge commits on default branches; "
                         'accessible public and private, non-fork repositories.')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="100" viewBox="0 0 480 100" role="img" aria-labelledby="title desc">
  <title id="title">Code changes · past 12 months</title>
  <desc id="desc">{description}</desc>
  <rect x="0.5" y="0.5" width="479" height="99" rx="12" fill="#{bg}" stroke="#{border}"/>
  <g font-family="Segoe UI, Ubuntu, sans-serif">
    <text x="25" y="26" font-size="18" font-weight="600" fill="#{title}">Code changes</text>
    <text x="455" y="26" text-anchor="end" font-size="10" fill="#{muted}">12 MONTHS · {period}</text>
    <path d="M240 43 V85" stroke="#{border}"/>
    <text x="25" y="65" font-size="{font_size}" font-weight="600" fill="#{added}">{plus}</text>
    <text x="260" y="65" font-size="{font_size}" font-weight="600" fill="#{removed}">{minus}</text>
    <text x="25" y="85" font-size="13" fill="#{muted}">lines added</text>
    <text x="260" y="85" font-size="13" fill="#{muted}">lines deleted</text>
  </g>
</svg>
'''


def main():
    until = datetime.now(timezone.utc).replace(microsecond=0)
    try:
        since = until.replace(year=until.year - 1)
    except ValueError:  # Leap day maps to February 28 in the previous year.
        since = until.replace(year=until.year - 1, day=28)
    timestamp = lambda value: value.isoformat().replace('+00:00', 'Z')
    stats = collect(os.environ.get('STATS_USERNAME', 'Danonika'),
                    timestamp(since), timestamp(until))
    destination = Path('assets/stats')
    destination.mkdir(parents=True, exist_ok=True)
    for theme in ('light', 'dark'):
        (destination / f'code-changes-{theme}.svg').write_text(render(stats, theme == 'dark'))
    (destination / 'code-changes.json').write_text(json.dumps(stats, indent=2) + '\n')
    print(f"Published aggregate line changes from {stats['commits']} unique non-merge commits.")


if __name__ == '__main__':
    main()
