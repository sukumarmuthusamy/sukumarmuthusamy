"""Derive a reduced-motion calendar from Platane/snk's generated SVG."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
ASSETS = Path(__file__).resolve().parents[1] / 'assets'

for theme in ('light', 'dark'):
    source = ET.parse(ASSETS / f'github-snake-{theme}.svg').getroot()
    css = ''.join(source.find(f'{{{NS}}}style').itertext())
    palette = dict(re.findall(r'--([\w-]+):([^;}]+)', css))
    classes = dict(re.findall(r'\.c\.(\w+)\{fill:var\(--([\w-]+)\)', css))
    output = ET.Element(f'{{{NS}}}svg', {'viewBox': '-16 -16 880 144', 'width': '880', 'height': '144'})
    ET.SubElement(output, f'{{{NS}}}title').text = 'Public GitHub contribution calendar'
    cells = 0
    for cell in source.findall(f'{{{NS}}}rect'):
        tokens = cell.get('class', '').split()
        if 'c' not in tokens:
            continue
        color_key = next((classes[t] for t in tokens if t in classes), 'ce')
        attrs = {k: cell.get(k, '0') for k in ('x', 'y', 'rx', 'ry')}
        attrs.update(width='12', height='12', fill=palette[color_key], stroke=palette['cb'], **{'stroke-width': '1'})
        ET.SubElement(output, f'{{{NS}}}rect', attrs)
        cells += 1
    if cells < 350:
        raise ValueError(f'Unexpected calendar structure: {cells} cells')
    ET.ElementTree(output).write(ASSETS / f'github-calendar-{theme}.svg', encoding='unicode')
    print(f'{theme}: {cells} calendar cells')
