"""Shared Markdown rendering for published content and proposal preflight checks."""
import html
from pathlib import Path
import re
from urllib.parse import quote, unquote, urlsplit

import mistune
from public_files import is_public


def link_resolver(root, source_path, extra_files=()):
    root = Path(root).resolve()
    source_path = Path(source_path)
    source = (root / source_path).resolve()
    extra_files = {(root / path).resolve() for path in extra_files}

    def exists(path):
        return path.is_relative_to(root) and (path.is_file() or path in extra_files)

    def resolve(link):
        url = urlsplit(link)
        if url.scheme or url.netloc or not url.path:
            return link
        path = unquote(url.path)
        # A leading slash selects the repository root; all other paths are
        # relative to the source document, independent of which files exist.
        target = ((root if path.startswith('/') else source.parent) / path.lstrip('/')).resolve()
        if not exists(target):
            raise ValueError(f'{source_path}: missing local link {link}')
        relative = target.relative_to(root)
        parts = relative.parts
        if len(parts) == 3 and parts[0] == 'data' and parts[2] == 'why.md':
            return '#case/' + quote(parts[1])
        # Markdown and Lean sources open on GitHub for reading. Published data
        # and media use a site URL, regardless of how the source link was written.
        base = (
            '/' if is_public(relative.as_posix()) and target.suffix not in {'.md', '.lean'}
            else 'https://github.com/hodge-computer/sextics/blob/main/'
        )
        result = base + quote(relative.as_posix())
        if url.query:
            result += '?' + url.query
        if url.fragment:
            result += '#' + url.fragment
        return result
    return resolve


def slug(text):
    return re.sub(r'[^\w\s-]', '', text.lower()).strip().replace(' ', '-')

class Renderer(mistune.HTMLRenderer):
    def link(self, link, text=None, title=None):
        return super().link(self.resolve_link(link), text, title)

    def heading(self, text, level):
        return f'<h{level} id="{html.escape(slug(re.sub("<[^>]*>", "", text)))}">{text}</h{level}>\n'

def render(source, *, root=None, source_path=None, extra_files=()):
    renderer = Renderer(escape=True)
    renderer.resolve_link = link_resolver(root, source_path, extra_files) if source_path else lambda link: link
    markdown = mistune.create_markdown(renderer=renderer, plugins=['table', 'strikethrough'])
    # Protect TeX before Markdown interprets underscores, backslashes, or table bars.
    formulas = []
    def keep(match):
        raw = match.group(0)
        display = raw.startswith('$$') or raw.startswith('\\[')
        tex = raw[2:-2].strip()
        formulas.append((tex, display))
        token = f'HODGEMATHTOKEN{len(formulas)-1}END'
        return '\n\n' + token + '\n\n' if display else token
    source = re.sub(r'\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)', keep, source)
    result = markdown(source)
    # Heading links must depend on the formula, not its position in the document.
    def heading_id(match):
        identifier = re.sub(r'hodgemathtoken(\d+)end',
                            lambda token: slug(formulas[int(token[1])][0]), match[1])
        return f'id="{identifier}"'
    result = re.sub(r'id="([^"]*)"', heading_id, result)
    for i, (tex, display) in enumerate(formulas):
        token = f'HODGEMATHTOKEN{i}END'
        tag = 'div' if display else 'span'
        node = f'<{tag} class="{"page-equation" if display else "inline-math"}" data-math{" data-display" if display else ""}>{html.escape(tex)}</{tag}>'
        result = result.replace(f'<p>{token}</p>', node) if display else result
        result = result.replace(token, node)
    return result

