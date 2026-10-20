"""Human-readable Markdown reports; source text is rendered as literal code."""
import json
import re


def code_span(value):
    fence = '`' * (max([len(run) for run in re.findall(r'`+', value)] + [0]) + 1)
    return fence + ' ' + value + ' ' + fence


def markdown_report(query, results):
    lines = ['# Local Search Report', '', 'Query:', '', '    ' + json.dumps(query, ensure_ascii=False), '',
             f'{len(results)} matching line(s) returned.', '',
             'Coverage is the fraction of distinct query words matched on a line, not a confidence score.', '']
    if not results:
        lines += ['No matching lines. Try fewer or different words.', '']
    for number, result in enumerate(results, 1):
        coverage = result['score'] * 100
        citation = json.dumps(result['source'], ensure_ascii=False) + ':' + str(result['line'])
        lines += [f'## Result {number} — {coverage:.0f}% query-word coverage', '',
                  'Source: ' + code_span(citation), '', 'Excerpt:', '']
        # Indented code prevents document text from becoming active HTML or Markdown.
        lines += ['    ' + line for line in result['excerpt'].splitlines() or ['']]
        lines += ['']
    return '\n'.join(lines)

