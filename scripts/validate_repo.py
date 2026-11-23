#!/usr/bin/env python3
"""校验信息图形研究库的结构、链接与图片放置，不依赖第三方包。

用法：python scripts/validate_repo.py
通过时返回 0；发现问题返回 1 并逐条打印。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
LOGIC = ROOT / '01-信息图形数据逻辑'
CASES = ROOT / '02-信息图形类型案例'
RECORDS = CASES / '案例记录'
IMAGES = CASES / '案例图'

IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp'}
REQUIRED_SECTIONS = ('## A ', '## B ', '## C ', '## D ', '## E ')
# 类型文档 01–18：课件 16 项 + 词云 + ISOTYPE
TYPE_DOC_COUNT = 18
REQUIRED_CASE_DOCS = (
    '00-类型总览.md',
    '01-混合型信息图形-Mixed-Charts.md',
    '02-文字型与列表型信息图形-Informational-List.md',
    '03-时间轴型信息图形-Timeline.md',
    '案例索引.md',
    '案例分析模板.md',
    '课件来源与分类核验.md',
)
# 图版只允许出现在这两个目录里
IMAGE_ALLOWED_DIRS = {IMAGES.resolve(), (CASES / '案例记录').resolve()}

issues: list[str] = []


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


# ---- 1. 01 层：恰好 5 份、含 A–E、无图 ----
logic_files = sorted(LOGIC.glob('*.md'))
if len(logic_files) != 5:
    issues.append(f'01/ 应恰好有 5 份 .md，实有 {len(logic_files)}')

for path in LOGIC.rglob('*'):
    if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
        issues.append(f'01/ 内禁止放图片：{rel(path)}')

for f in logic_files:
    text = f.read_text('utf-8')
    for name in REQUIRED_SECTIONS:
        if name not in text:
            issues.append(f'{rel(f)} 缺少段落「{name.strip()}」')
    if '../02-信息图形类型案例/' not in text:
        issues.append(f'{rel(f)} 缺少指向 02/ 的案例链接')

# ---- 2. 02 层：类型文档数量与必备文档 ----
type_docs = [p for p in CASES.glob('*.md') if re.match(r'^(0[1-9]|1[0-8])-', p.name)]
if len(type_docs) != TYPE_DOC_COUNT:
    issues.append(f'02/ 类型文档应为 {TYPE_DOC_COUNT} 份，实有 {len(type_docs)}')

for name in REQUIRED_CASE_DOCS:
    if not (CASES / name).is_file():
        issues.append(f'02/ 缺少必备文档：{name}')

# ---- 3. 案例记录与图版的配对 ----
case_files = sorted(RECORDS.glob('CASE-*.md'))
case_ids = {f.name[:9] for f in case_files}
for f in case_files:
    text = f.read_text('utf-8')
    if 'case_id:' not in text:
        issues.append(f'{rel(f)} 缺少 front matter 字段 case_id')
    m = re.search(r'image_path:\s*"([^"]+)"', text)
    if m:
        target = (f.parent / unquote(m.group(1))).resolve()
        if not target.is_file():
            issues.append(f'{rel(f)} 指向的图版不存在：{m.group(1)}')

for img in sorted(IMAGES.glob('*')):
    if img.suffix.lower() not in IMAGE_SUFFIXES:
        continue
    if img.stem[:9].startswith('CASE-'):
        if img.stem[:9] not in case_ids:
            issues.append(f'图版 {rel(img)} 没有对应的案例记录')
    else:
        issues.append(f'图版命名不符合 CASE-xxxx-名 规则：{rel(img)}')

# ---- 4. 图片放置范围 ----
for path in ROOT.rglob('*'):
    if '.git' in path.parts or '.workbuddy' in path.parts:
        continue
    if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
        if path.parent.resolve() not in IMAGE_ALLOWED_DIRS:
            issues.append(f'图片只能放在 02-信息图形类型案例/案例图/：{rel(path)}')

# ---- 5. 全库相对链接 ----
LINK = re.compile(r'!?\[[^\]\n]*\]\(([^)\n]+)\)')
md_files = sorted(ROOT.rglob('*.md'))
for f in md_files:
    if '.git' in f.parts or '.workbuddy' in f.parts:
        continue
    src = f.read_text('utf-8')
    # 代码块与行内代码里的示例链接不算真链接
    src = re.sub(r'^\s*(```|~~~)[\s\S]*?^\s*\1[^\n]*(?:\n|$)', '', src, flags=re.MULTILINE)
    src = re.sub(r'`[^`\n]*`', '', src)
    for link in LINK.findall(src):
        link = link.strip()
        if not link or link.startswith('#'):
            continue
        if link.startswith('<') and link.endswith('>'):
            link = link[1:-1]
        if urlparse(link).scheme or link.startswith('//') or link.startswith('mailto:'):
            continue
        pure = unquote(link.split('#', 1)[0].split('?', 1)[0])
        if not pure:
            continue
        target = (f.parent / pure).resolve()
        if not str(target).startswith(str(ROOT.resolve())):
            issues.append(f'链接越出仓库：{rel(f)} -> {link}')
        elif not target.exists():
            issues.append(f'断链：{rel(f)} -> {link}')

# ---- 6. 案例索引与记录数一致 ----
index = CASES / '案例索引.md'
if index.is_file():
    n_index = len(re.findall(r'CASE-\d{4}', index.read_text('utf-8')))
    if n_index < len(case_ids):
        issues.append(f'案例索引只提到 {n_index} 次 CASE 编号，少于记录数 {len(case_ids)}')

if issues:
    for i in issues:
        print('ERROR:', i)
    print(f'\n共 {len(issues)} 个问题')
    sys.exit(1)

print(
    f'OK: {len(md_files)} 份 Markdown、{len(logic_files)} 份逻辑定义、'
    f'{len(type_docs)} 份类型文档、{len(case_files)} 条案例记录；'
    '相对链接全部有效，01/ 无图片，图版命名与配对一致。'
)
