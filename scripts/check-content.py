#!/usr/bin/env python3
"""Check rendered math, chapter navigation, and local links without a browser."""
from html.parser import HTMLParser
import argparse
from pathlib import Path
from public_files import is_public
import json
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--explanation', type=Path, help='Also check a proposed, rendered explanation before acceptance')
args = parser.parse_args()

def label(path):
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else path.name

class Content(HTMLParser):
    def __init__(self, path):
        super().__init__(); self.path=path; self.math=[]; self.links=[]; self.ids=set(); self.current=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'data-math' in a: self.current=[]
        if tag=='a': self.links.append(a.get('href',''))
        if 'id' in a: self.ids.add(a['id'])
    def handle_endtag(self,tag):
        if self.current is not None and tag in ('span','div'):
            self.math.append({'file':label(self.path), 'tex':''.join(self.current)})
            self.current=None
    def handle_data(self,text):
        if self.current is not None: self.current.append(text)

index=json.loads((ROOT/'docs/index.json').read_text())
pages={p['id']:p for p in index['pages']}
files=list((ROOT/'data').glob('*/*.html'))+list((ROOT/'docs').glob('*.html'))+[ROOT/'index.html']
if args.explanation:
    files.append(args.explanation.resolve())
contents={}
for p in files:
    c=Content(p);c.feed(p.read_text());contents[p]=c
errors=[];math=[]
for p,c in contents.items():
    math.extend(c.math)
    for link in c.links:
        if p.parent == ROOT/'docs' and link and not link.startswith('#'):
            url = urlsplit(link)
            suffix = Path(unquote(url.path)).suffix.lower()
            if (not url.scheme or url.hostname == 'raw.githubusercontent.com'
                    or suffix in {'.md', '.markdown', '.rst', '.txt', '.py', '.lean', '.rec', '.json', '.zip'}):
                errors.append(f'{p.name}: raw file link {link}; use a rendered chapter route or a published reference')
                continue
        if link.startswith(('http://','https://','mailto:')):continue
        if link.startswith('#technical-information/'):
            parts=link[1:].split('/');page=pages.get(parts[1])
            if not page: errors.append(f'{p.name}: unknown chapter {link}')
            elif len(parts)>2 and '/'.join(parts[2:]) not in contents[ROOT/page['content']].ids:errors.append(f'{p.name}: missing chapter heading {link}')
        elif link.startswith('#') or not link:continue
        elif not is_public(link.split('#')[0].lstrip('/')) or not (ROOT/link.split('#')[0].lstrip('/')).is_file():errors.append(f'{p.name}: missing local link {link}')
for p in (ROOT/'data').glob('*/record.json'):
    record=json.loads(p.read_text())
    for name in ('F','A','D'):
        if name in record and record[name].get('latex'):math.append({'file':str(p.relative_to(ROOT))+':'+name,'tex':record[name]['latex']})
    for tex in record.get('displayDefinitions',[]):math.append({'file':str(p.relative_to(ROOT))+':definition','tex':tex})
node=r'''
const fs=require('fs'),katex=require('./assets/vendor/katex.min.js');const formulas=JSON.parse(fs.readFileSync(0,'utf8'));let errors=[];
for(const f of formulas){try{katex.renderToString(f.tex,{throwOnError:true,strict:'error',trust:false});}catch(e){errors.push(`${f.file}: ${e.message}`);}}
if(errors.length){console.error(errors.join('\n'));process.exit(1);}console.log(`Rendered ${formulas.length} formulas with bundled KaTeX.`);
'''
result=subprocess.run(['node','-e',node],input=json.dumps(math),text=True,cwd=ROOT,capture_output=True)
if result.returncode:errors.append(result.stderr)
if errors:raise SystemExit('\n'.join(errors))
print(result.stdout.strip())
print(f'Checked local links and chapter routes in {len(files)} HTML files.')
