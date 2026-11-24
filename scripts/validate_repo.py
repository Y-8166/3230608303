#!/usr/bin/env python3
"""校验信息图形研究库的结构、链接与图片放置，不依赖第三方包。

用法：python scripts/validate_repo.py
通过时返回 0；发现问题返回 1 并逐条打印。
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
LOGIC = ROOT / '01-信息图形数据逻辑'
CASES = ROOT / '02-信息图形类型案例'
RECORDS = CASES / '案例记录'
IMAGES = CASES / '案例图'
DATASETS = CASES / '案例数据'
GESTALT = ROOT / '04-格式塔知觉规则'

IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp'}
REQUIRED_SECTIONS = ('## A ', '## B ', '## C ', '## D ', '## E ')
REQUIRED_GESTALT_SECTIONS = ('## A ', '## B ', '## C ', '## D ', '## E ', '## F ', '## G ')
GESTALT_RULE_COUNT = 14
# 类型文档 01–18：课件 16 项 + 词云 + ISOTYPE
TYPE_DOC_COUNT = 18
REQUIRED_CASE_DOCS = (
    '00-类型总览.md',
    '01-混合型信息图形-Mixed-Charts.md',
    '02-文字型与列表型信息图形-Informational-List.md',
    '03-时间轴型信息图形-Timeline.md',
    '案例索引.md',
    '案例分析模板.md',
    '数据表规范.md',
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

# ---- 3b. 数据表（V3 规范）----
DATASET_STATUS = {'complete', 'partial', 'none'}
CSV_HEAD_FORBIDDEN = set('$% ()（）')


def parse_front(text: str, key: str) -> str:
    m = re.search(rf'^{key}:\s*(.*?)\s*$', text, flags=re.MULTILINE)
    return m.group(1).strip().strip('"\'') if m else ''


pending_dict: list[str] = []

for f in case_files:
    text = f.read_text('utf-8')
    status = parse_front(text, 'dataset_status')
    if not status:
        # 第 2 批待办：存量案例补 none 字典后即纳入强制校验
        pending_dict.append(f.name[:9])
        continue
    if status not in DATASET_STATUS:
        issues.append(f'{rel(f)} 的 dataset_status 非法：{status!r}')
        continue

    ddict = parse_front(text, 'dataset_dict')
    if not ddict:
        issues.append(f'{rel(f)} 缺少 dataset_dict（任何状态都必须有数据字典）')
    else:
        t = (f.parent / ddict).resolve()
        if not t.is_file():
            issues.append(f'{rel(f)} 指向的数据字典不存在：{ddict}')
        else:
            dtext = t.read_text('utf-8')
            for need in ('不可推断', '复算'):
                if need not in dtext:
                    issues.append(f'{rel(t)} 缺少「{need}」内容')

    dpath = parse_front(text, 'dataset_path')
    if status in ('complete', 'partial') and not dpath:
        issues.append(f'{rel(f)} 状态为 {status} 但缺少 dataset_path')
    if dpath:
        t = (f.parent / dpath).resolve()
        if not t.is_file():
            issues.append(f'{rel(f)} 指向的基础数据集不存在：{dpath}')

if not DATASETS.is_dir():
    issues.append('02/ 缺少 案例数据/ 目录')
else:
    for csvf in sorted(DATASETS.glob('CASE-*.csv')):
        if csvf.stem[:9] not in case_ids:
            issues.append(f'数据表 {rel(csvf)} 没有对应的案例记录')
        with csvf.open(encoding='utf-8-sig', newline='') as fh:
            rows = list(csv.reader(fh))
        if not rows or not rows[0]:
            issues.append(f'{rel(csvf)} 缺少表头')
            continue
        head = rows[0]
        for col in head:
            if not col or col != col.strip() or ' ' in col:
                issues.append(f'{rel(csvf)} 表头列名含空格或为空：{col!r}')
            if CSV_HEAD_FORBIDDEN & set(col):
                issues.append(f'{rel(csvf)} 表头列名含单位或特殊字符：{col}')
        for lineno, row in enumerate(rows[1:], start=2):
            if len(row) != len(head):
                issues.append(
                    f'{rel(csvf)} 第 {lineno} 行列数 {len(row)} ≠ 表头 {len(head)}'
                )
                break

    for d in sorted(DATASETS.glob('CASE-*-数据字典.md')):
        if d.name[:9] not in case_ids:
            issues.append(f'数据字典 {rel(d)} 没有对应的案例记录')

# ---- 4. 04 层：14 条原则各一份，A–G 齐全 ----
gestalt_files = sorted(GESTALT.glob('*.md'))
expected_rules = [f'{i:02d}-' for i in range(1, GESTALT_RULE_COUNT + 1)]
rule_docs = [p for p in gestalt_files if p.name[:3] in expected_rules]

if len(rule_docs) != GESTALT_RULE_COUNT:
    issues.append(
        f'04/ 应有 {GESTALT_RULE_COUNT} 份原则文档（01–14），实有 {len(rule_docs)}'
    )
for prefix in expected_rules:
    if not any(p.name.startswith(prefix) for p in gestalt_files):
        issues.append(f'04/ 缺少编号为 {prefix[:-1]} 的原则文档')

if not (GESTALT / '00-总览与索引.md').is_file():
    issues.append('04/ 缺少 00-总览与索引.md')

for f in rule_docs:
    text = f.read_text('utf-8')
    for name in REQUIRED_GESTALT_SECTIONS:
        if name not in text:
            issues.append(f'{rel(f)} 缺少段落「{name.strip()}」')
    if '概念定义（课程口径）' not in text:
        issues.append(f'{rel(f)} 缺少「概念定义（课程口径）」逐字引用')
    if '信息图形设计示例（课程口径）' not in text:
        issues.append(f'{rel(f)} 缺少「信息图形设计示例（课程口径）」逐字引用')
    log = re.search(r'^order:\s*(\d+)', text, flags=re.MULTILINE)
    if not log or f'{int(log.group(1)):02d}' != f.name[:2]:
        issues.append(f'{rel(f)} 的 front matter order 与文件名编号不一致')

# ---- 5. 图片放置范围 ----
for path in ROOT.rglob('*'):
    if '.git' in path.parts or '.workbuddy' in path.parts:
        continue
    if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
        if path.parent.resolve() not in IMAGE_ALLOWED_DIRS:
            issues.append(f'图片只能放在 02-信息图形类型案例/案例图/：{rel(path)}')

# ---- 6. 全库相对链接与跨文档锚点 ----
LINK = re.compile(r'!?\[[^\]\n]*\]\(([^)\n]+)\)')
HEADING = re.compile(r'^#{1,6}\s+(.+?)\s*$', re.MULTILINE)


def gh_slug(text: str) -> str:
    """近似 GitHub 的标题锚点规则：小写、去标点、空格转连字符。"""
    s = text.strip().lower()
    s = ''.join(ch for ch in s if ch.isalnum() or ch in ' -_')
    return s.replace(' ', '-')


def anchors_of(path: Path) -> set[str]:
    text = path.read_text('utf-8')
    text = re.sub(r'^\s*(```|~~~)[\s\S]*?^\s*\1[^\n]*(?:\n|$)', '', text, flags=re.MULTILINE)
    return {gh_slug(h) for h in HEADING.findall(text)}


anchor_cache: dict[Path, set[str]] = {}
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
        anchor = unquote(link.split('#', 1)[1]) if '#' in link else ''
        if not pure:
            continue
        target = (f.parent / pure).resolve()
        if not str(target).startswith(str(ROOT.resolve())):
            issues.append(f'链接越出仓库：{rel(f)} -> {link}')
        elif not target.exists():
            issues.append(f'断链：{rel(f)} -> {link}')
        elif anchor and target.suffix.lower() == '.md':
            if target not in anchor_cache:
                anchor_cache[target] = anchors_of(target)
            if anchor.lower() not in anchor_cache[target]:
                issues.append(f'锚点不存在：{rel(f)} -> {link}')

# ---- 7. 案例索引与记录数一致 ----
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

if pending_dict:
    print(
        f'WARNING: {len(pending_dict)} 条存量案例尚未声明 dataset_status，'
        f'按规范 §10 留待第 2 批补 none 字典：' + '、'.join(pending_dict)
    )

print(
    f'OK: {len(md_files)} 份 Markdown、{len(logic_files)} 份逻辑定义、'
    f'{len(type_docs)} 份类型文档、{len(case_files)} 条案例记录、'
    f'{len(rule_docs)} 条格式塔原则、'
    f'{len(list(DATASETS.glob("CASE-*.csv")))} 张 CSV、'
    f'{len(list(DATASETS.glob("CASE-*-数据字典.md")))} 份数据字典；'
    '相对链接与锚点全部有效，01/ 无图片，图版命名与配对一致，数据表状态与结构自洽。'
)
