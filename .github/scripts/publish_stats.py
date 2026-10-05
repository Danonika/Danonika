"""Publish aggregate cards only after all four render successfully."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

NAMES = ('activity-light', 'activity-dark', 'languages-light', 'languages-dark')
for name in NAMES:
    path = Path('assets/stats') / (name + '.svg')
    svg = path.read_text()
    root = ET.fromstring(svg)
    if root.tag != '{http://www.w3.org/2000/svg}svg' or 'Something went wrong' in svg:
        raise ValueError(f'Invalid generated card: {path}')

block = '''<!-- STATS:START -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/stats/activity-dark.svg">
  <img src="assets/stats/activity-light.svg" alt="All-time GitHub activity, including accessible private contributions" width="480">
</picture>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/stats/languages-dark.svg">
  <img src="assets/stats/languages-light.svg" alt="Languages across accessible public and private repositories, weighted by repository count" width="480">
</picture>

<sub>Public + accessible private activity. Language shares are weighted by repository count. Updated daily via GitHub Actions. [Calendar artwork](calendar-art/README.md) is included in contribution totals.</sub>
<!-- STATS:END -->'''
readme = Path('README.md')
source = readme.read_text()
pattern = r'<!-- STATS:START -->[\s\S]*?<!-- STATS:END -->'
if len(re.findall(pattern, source)) != 1:
    raise ValueError('Expected exactly one marked stats block in README.md')
readme.write_text(re.sub(pattern, lambda _: block, source))
