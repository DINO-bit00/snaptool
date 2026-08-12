import glob

CSS_TAG = '  <link rel="stylesheet" href="/static/theme.css"/>'
JS_TAG  = '  <script src="/static/theme.js"></script>'

files = glob.glob('static/*.html')
updated = []

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    changed = False

    if 'theme.css' not in html:
        html = html.replace('</head>', CSS_TAG + '\n</head>', 1)
        changed = True

    if 'theme.js' not in html:
        html = html.replace('<body>', '<body>\n' + JS_TAG, 1)
        changed = True

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        updated.append(filepath)
        print(f'Updated: {filepath}')

print(f'Done. {len(updated)} files updated.')
