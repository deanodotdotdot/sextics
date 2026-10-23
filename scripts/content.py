"""Shared Markdown rendering for published content and proposal preflight checks."""
import html
from pathlib import Path
import re
from urllib.parse import quote, unquote, urlsplit

import mistune
from mistune.scanner import Matcher
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


class MathMatcher(Matcher):
    # A display equation starts a block even without a preceding blank line.
    PARAGRAPH_END = re.compile(Matcher.PARAGRAPH_END.pattern + r'|(?:\n {0,3}(?:\\\[|\$\$))')


def math_plugin(markdown):
    markdown.block.scanner_cls = MathMatcher
    markdown.block.register_rule(
        'display_math', re.compile(r' {0,3}(?:\\\[([\s\S]*?)\\\]|\$\$([\s\S]*?)\$\$)[ \t]*(?:\n|$)'),
        lambda parser, match, state: {'type': 'display_math', 'raw': (match[1] or match[2] or '').strip()})
    for rules in (markdown.block.rules, markdown.block.block_quote_rules, markdown.block.list_rules):
        rules.insert(0, 'display_math')
    markdown.inline.register_rule(
        'inline_math', r'\\\([\s\S]*?\\\)',
        lambda parser, match, state: ('inline_math', match[0][2:-2].strip()))
    for rules in (markdown.inline.rules, markdown.inline.ref_link_rules):
        rules.insert(0, 'inline_math')


class Renderer(mistune.HTMLRenderer):
    def link(self, link, text=None, title=None):
        return super().link(self.resolve_link(link), text, title)

    def heading(self, text, level):
        identifier = slug(html.unescape(re.sub('<[^>]*>', '', text)))
        return f'<h{level} id="{html.escape(identifier)}">{text}</h{level}>\n'

    def inline_math(self, text):
        return f'<span class="inline-math" data-math>{html.escape(text)}</span>'

    def display_math(self, text):
        return f'<div class="page-equation" data-math data-display>{html.escape(text)}</div>\n'

def render(source, *, root=None, source_path=None, extra_files=()):
    renderer = Renderer(escape=True)
    renderer.resolve_link = link_resolver(root, source_path, extra_files) if source_path else lambda link: link
    markdown = mistune.create_markdown(renderer=renderer, plugins=['table', 'strikethrough', math_plugin])
    return markdown(source)

