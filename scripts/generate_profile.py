#!/usr/bin/env python3
"""Reproduce the supplied terminal profile using only Python's standard library."""
import argparse
import datetime as dt
import html
import json
import os
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BG, BORDER, FG, MUTED = '#0d1117', '#262d35', '#c9d1d9', '#8b949e'
GREEN, BLUE, METRIC = '#009100', '#58a6ff', '#008f51'


def graphql(query, variables):
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        raise RuntimeError('Set GH_TOKEN or GITHUB_TOKEN to refresh GitHub data.')
    request = urllib.request.Request('https://api.github.com/graphql',
        data=json.dumps({'query': query, 'variables': variables}).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json',
                 'User-Agent': 'repository-profile-renderer'})
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.load(response)
    if result.get('errors'):
        raise RuntimeError(f"GitHub GraphQL error: {result['errors']}")
    return result['data']


def fetch(username):
    fields = '''repositories(first: 100, after: $cursor, privacy: PUBLIC,
        ownerAffiliations: OWNER, orderBy: {field: NAME, direction: ASC}) {
        totalCount pageInfo {hasNextPage endCursor} nodes {stargazerCount forkCount}}'''
    query = '''query($login: String!, $cursor: String) {user(login: $login) {
        login name bio websiteUrl location followers {totalCount} following {totalCount}
        gists(privacy: PUBLIC) {totalCount}
        contributionsCollection {contributionCalendar {totalContributions weeks {
            contributionDays {date contributionCount color weekday}}}}
    ''' + fields + '}}'
    user = graphql(query, {'login': username, 'cursor': None})['user']
    if user is None:
        raise RuntimeError(f'GitHub user {username!r} was not found.')
    repos = user['repositories']
    while repos['pageInfo']['hasNextPage']:
        page = graphql('query($login: String!, $cursor: String) {user(login: $login) {'
                       + fields + '}}',
                       {'login': username, 'cursor': repos['pageInfo']['endCursor']})
        page = page['user']['repositories']
        repos['nodes'].extend(page['nodes'])
        repos['pageInfo'] = page['pageInfo']
    return user


def streaks(days):
    longest = run = 0
    for day in days:
        run = run + 1 if day['contributionCount'] else 0
        longest = max(longest, run)
    active = days[:-1] if days and not days[-1]['contributionCount'] else days
    current = 0
    for day in reversed(active):
        if not day['contributionCount']:
            break
        current += 1
    return current, longest


def date_label(value):
    date = dt.date.fromisoformat(value)
    return f'{date:%b} {date.day}, {date.year}'


class SVG:
    def __init__(self, width, height, title):
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
                      f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
                      'aria-labelledby="title desc">',
                      f'<title id="title">{html.escape(title)}</title>',
                      '<desc id="desc">ASCII portrait, biography, actual GitHub contributions, '
                      'account metrics, and technology stack.</desc>',
                      '<style>text{font-family:Menlo,Consolas,"DejaVu Sans Mono",monospace}'
                      '.ticker{animation:scroll 95s linear infinite}'
                      '@keyframes scroll{to{transform:translateX(-VARpx)}}'
                      '@media(prefers-reduced-motion:reduce){.ticker{animation:none}}</style>',
                      f'<rect width="100%" height="100%" fill="{BG}"/>']

    def rect(self, x, y, w, h, fill=BG, radius=0, stroke=None):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
                          f'rx="{radius}" fill="{fill}"'
                          + (f' stroke="{stroke}"' if stroke else '') + '/>')

    def text(self, x, y, value, size=12, color=FG, weight='normal', extra=''):
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
                          f'font-weight="{weight}" {extra}>{html.escape(str(value))}</text>')

    def line(self, x, y, end):
        self.parts.append(f'<path d="M{x} {y}H{end}" stroke="{BORDER}"/>')

    def terminal(self, x, y, w, h, title, title_size=12):
        self.rect(x, y, w, h, radius=14, stroke=BORDER)
        self.line(x, y+28, x+w)
        for i, color in enumerate(('#ff5f57', '#ffbd2e', '#28c840')):
            self.parts.append(f'<circle cx="{x+19+i*15}" cy="{y+14}" r="4.8" fill="{color}"/>')
        self.text(x+w/2+20, y+18, title, title_size, MUTED, extra='text-anchor="middle"')

    def output(self):
        return '\n'.join(self.parts) + '\n</svg>\n'


def render(config, data, mobile=False):
    width, height = (480, 1614) if mobile else (958, 1236)
    s = SVG(width, height, f"{config['name']} — @{config['username']}")
    user, repos = config['username'], data['repositories']
    stars = sum(r['stargazerCount'] for r in repos['nodes'])
    forks = sum(r['forkCount'] for r in repos['nodes'])
    followers = data['followers']['totalCount']
    x, y, w, h = (68, 24, 344, 374) if mobile else (58, 48, 344, 374)
    s.terminal(x, y, w, h, f'{user}@github: ~$ ./portrait.sh', 10)
    for row, line in enumerate(config['portrait']):
        s.text(x+18, y+37+row*3.95, line, 3.42, '#008e00',
               extra='xml:space="preserve" textLength="308" lengthAdjust="spacingAndGlyphs"')
    s.line(x, y+h-40, x+w)
    s.text(x+18, y+h-22, f'{user}@github:~$ whoami', 12, MUTED)
    s.text(x+222, y+h-22, config['name'], 12, GREEN)

    x, y, w, h = (24, 418, 432, 374) if mobile else (448, 48, 458, 374)
    s.terminal(x, y, w, h, f'{user}@github: ~$ neofetch', 11)
    s.text(x+18, y+55, f'{user}@github', 14, '#39d353', 'bold')
    rows = [('Now', config['now']), ('Also', config['also']),
            ('Loc', config['location']), ('Site', config['site'])]
    for index, (label, value) in enumerate(rows):
        yy = y+78+index*23
        s.text(x+18, yy, label, 12, GREEN, 'bold')
        s.text(x+104, yy, value)
    s.text(x+18, y+180, '— Stack', 12, BLUE, 'bold')
    for index, (label, key) in enumerate([('Langs', 'languages'), ('Frontend', 'frontend'), ('Backend', 'backend')]):
        yy = y+202+index*23
        s.text(x+18, yy, label, 12, GREEN, 'bold')
        s.text(x+104, yy, config[key])
    s.text(x+18, y+280, '— Highlights', 12, BLUE, 'bold')
    s.line(x+112, y+276, x+w-18)
    for index, value in enumerate([f'{repos["totalCount"]} public repos, {followers} followers',
                                    f'Active developer with {stars} total stars']):
        s.text(x+18, y+303+index*23, '•', 15, '#26a641')
        s.text(x+32, y+303+index*23, value)

    calendar = data['contributionsCollection']['contributionCalendar']
    weeks = calendar['weeks']
    days = [day for week in weeks for day in week['contributionDays']]
    current, longest = streaks(days)
    best = max(days, key=lambda d: d['contributionCount']) if days else None
    x, y, w, h = (24, 812, 432, 406) if mobile else (58, 442, 844, 286)
    s.terminal(x, y, w, h, f'{user}@github: ~/contributions —graph', 10 if mobile else 14)
    chunks = [weeks[:27], weeks[27:]] if mobile else [weeks]
    for part, chunk in enumerate(chunks):
        gx, gy = x+(38 if mobile else 62), y+60+part*113
        step = min(14.35, (w-(52 if mobile else 86))/max(len(chunk), 1))
        last_month = None
        for col, week in enumerate(chunk):
            if not week['contributionDays']:
                continue
            date = dt.date.fromisoformat(week['contributionDays'][0]['date'])
            if date.month != last_month and col < len(chunk)-1:
                s.text(gx+col*step, gy-8, date.strftime('%b'), 11, MUTED)
                last_month = date.month
            for day in week['contributionDays']:
                s.parts.append(f'<g><title>{day["date"]}: {day["contributionCount"]} contributions</title>')
                s.rect(round(gx+col*step, 2), gy+day['weekday']*14.3, round(step-2.4, 2), 11.8,
                       ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353', '#69f0a0'][
                           min(5, (day['contributionCount']*5 + best['contributionCount']-1)//best['contributionCount'])
                           if best and best['contributionCount'] else 0], 3)
                s.parts.append('</g>')
        for row, label in [(1, 'Mon'), (3, 'Wed'), (5, 'Fri')]:
            s.text(x+(5 if mobile else 25), gy+row*14.3+9, label, 10, MUTED)
    legend_y = y+(300 if mobile else 176)
    s.text(x+w-186, legend_y, 'Less', 11, MUTED)
    for index, color in enumerate(['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353', '#69f0a0']):
        s.rect(x+w-148+index*14, legend_y-9, 11, 11, color, 3)
    s.text(x+w-54, legend_y, 'More', 11, MUTED)
    s.line(x, legend_y+20, x+w)
    yy = legend_y+49
    s.text(x+26, yy, calendar['totalContributions'], 15, '#39d353', 'bold')
    s.text(x+64, yy, 'contributions in the last year', 12 if mobile else 15, MUTED)
    if days:
        s.text(x+w-26, yy+(20 if mobile else 0), f'{date_label(days[0]["date"])} → {date_label(days[-1]["date"])}',
               10 if mobile else 14, MUTED, extra='text-anchor="end"')
    if mobile:
        s.text(x+26, yy+43, f'Streak {current}d · Longest {longest}d · Best {best["contributionCount"] if best else 0}', 12, '#39d353')
    else:
        s.text(x+26, yy+29, 'current streak', 15, MUTED)
        s.text(x+168, yy+29, f'{current} days', 15, GREEN, 'bold')
        s.text(x+245, yy+29, '· longest', 15, MUTED)
        s.text(x+335, yy+29, f'{longest} days', 15, GREEN, 'bold')
        if best:
            s.text(x+w-26, yy+29, f'best day {best["contributionCount"]} on {date_label(best["date"])}',
                   14, MUTED, extra='text-anchor="end"')

    word_y, word_x, word_width, line_step = (1258, 24, 432, 8) if mobile else (795, 76, 808, 14)
    for index, line in enumerate(config['wordmark']):
        s.text(word_x, word_y+index*line_step, line, 8 if mobile else 14, '#008e00',
               extra=f'xml:space="preserve" textLength="{word_width}" lengthAdjust="spacingAndGlyphs"')
    x, y, w, h = (24, 1324, 432, 170) if mobile else (58, 911, 835, 144)
    s.rect(x, y, w, h, stroke=BORDER)
    s.text(x+28, y+39, '[ GITHUB METRICS ]', 13, MUTED, extra='letter-spacing="2"')
    values = [('STARS', stars), ('REPOS', repos['totalCount']), ('FOLLOWERS', followers),
              ('FOLLOWING', data['following']['totalCount']), ('FORKS', forks), ('GISTS', data['gists']['totalCount'])]
    for index, (label, value) in enumerate(values):
        column, row = (index%3, index//3) if mobile else (index, 0)
        xx, yy = x+28+column*(136 if mobile else 130), y+(72 if mobile else 90)+row*59
        s.text(xx, yy, value, 25 if mobile else 34, METRIC)
        s.text(xx, yy+20, label, 10 if mobile else 12, MUTED, extra='letter-spacing="2"')

    x, y, w = (24, 1518, 432) if mobile else (68, 1102, 825)
    s.rect(x, y, w, 62, '#10161c', 10, BORDER)
    s.parts.append(f'<defs><clipPath id="tools"><rect x="{x}" y="{y}" width="{w}" height="62" rx="10"/></clipPath></defs>')
    s.parts.append('<g clip-path="url(#tools)"><g class="ticker">')
    names = {'ts':'TypeScript','js':'JavaScript','nodejs':'Node.js','nextjs':'Next.js',
             'vscode':'VS Code','postgres':'PostgreSQL','py':'Python','python':'Python',
             'react':'React','figma':'Figma','postman':'Postman','html':'HTML','css':'CSS'}
    ordered = ['figma','postman','vscode','cloudflare','npm','blender','notion'] + config['tools']
    labels = list(dict.fromkeys(names.get(key, key) for key in ordered))
    period = sum(len(label)*7.2+36 for label in labels)
    cursor = x-10
    for label in labels*2:
        pill_width = len(label)*7.2+24
        s.rect(round(cursor, 1), y+16, round(pill_width, 1), 30, '#0c241e', 15, '#005c3b')
        s.text(round(cursor+12, 1), y+36, label, 12, '#d5e9e4')
        cursor += pill_width+12
    s.parts.append('</g></g>')
    return s.output().replace('VAR', str(round(period, 1)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='Fetch public data from GitHub first')
    args = parser.parse_args()
    config = json.loads((ROOT/'profile/config.json').read_text())
    data_path = ROOT/'profile/github-data.json'
    data = fetch(config['username']) if args.refresh else json.loads(data_path.read_text())
    if data['login'].lower() != config['username'].lower():
        raise RuntimeError('Cached username differs from profile/config.json; refresh the data.')
    desktop, mobile = render(config, data), render(config, data, mobile=True)
    (ROOT/'assets').mkdir(exist_ok=True)
    if args.refresh:
        data_path.write_text(json.dumps(data, indent=2)+'\n')
    (ROOT/'assets/profile.svg').write_text(desktop)
    (ROOT/'assets/profile-mobile.svg').write_text(mobile)
    print('Rendered assets/profile.svg and assets/profile-mobile.svg')


if __name__ == '__main__':
    main()
