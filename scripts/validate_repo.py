#!/usr/bin/env python3
"""校验信息图形研究库的结构、链接与图片放置，不依赖第三方包。

结构（v3.2.0，六层板块 + docs/ 治理 + scripts/ 校验；02 层照 fengbaifan 库的「类型文件夹 + 一案例一目录」）：

    01…06-<板块>/README.md          ← 六个板块各有统一入口
    02-信息图形类型案例/
    ├─ <NN>-<类型名>/00-标签说明.md
    ├─ <NN>-<类型名>/案例/
    │  └─ README.md 或 CASE-xxxx-名/
    │     ├─ README.md  分析.md  原图.webp  原图来源.md  数据字典.md
    │     └─ 基础数据集.csv  辅助指标.csv
    └─ 00-类型总览.md 案例索引.md 案例分析模板.md 数据表规范.md …
    docs/                            ← 治理文档；根目录不另放 Markdown
    scripts/validate_repo.py         ← 常驻；archive/ 为一次性脚本存档

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
GESTALT = ROOT / '05-格式塔知觉规则'
ISOTYPE = ROOT / '03-ISOTYPE信息图'
STYLE = ROOT / '04-信息可视化风格'
THEME = ROOT / '06-主题信息图形设计'

IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp'}
REQUIRED_SECTIONS = ('## A ', '## B ', '## C ', '## D ', '## E ')
CASE_SECTIONS = ('## A', '## B', '## C', '## D', '## E')
REQUIRED_GESTALT_SECTIONS = ('## A ', '## B ', '## C ', '## D ', '## E ', '## F ', '## G ')
GESTALT_RULE_COUNT = 14
TYPE_FOLDER_COUNT = 17
REQUIRED_CASE_DOCS = (
    'README.md',
    '00-类型总览.md',
    '案例索引.md',
    '案例分析模板.md',
    '数据表规范.md',
    '案例写作规范.md',
    '课件来源与分类核验.md',
    '设计准则与评价方法.md',
    '计数结构筛查.md',
)
CASE_CORE_FILES = ('分析.md', 'README.md', '原图来源.md', '数据字典.md')
DATASET_STATUS = {'complete', 'partial', 'none'}
CSV_HEAD_FORBIDDEN = set('$% ()（）')

issues: list[str] = []


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


# ---- 1. 01 层：恰好 5 份、含 A–E、无图 ----
logic_files = sorted(p for p in LOGIC.glob('*.md') if p.name != 'README.md')
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

# ---- 1b. 顶层六层齐全，03 层三份文档到位 ----
for d in (LOGIC, CASES, ISOTYPE, STYLE, GESTALT, THEME):
    if not d.is_dir():
        issues.append(f'缺少顶层目录：{d.name}')

for name in ('README.md', '00-ISOTYPE概念与方法.md', '01-图符语言与视觉编码.md'):
    if not (ISOTYPE / name).is_file():
        issues.append(f'03/ 缺少文档：{name}')

# 03 层不得放图片，与 01 层同规则
for path in ISOTYPE.rglob('*'):
    if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
        issues.append(f'03/ 内不放图片：{rel(path)}')

# 02 层不得再出现 ISOTYPE 类型文件夹（已升为 03）
if any(p.name.startswith('18-ISOTYPE') for p in CASES.iterdir() if p.is_dir()):
    issues.append('02/ 仍有 18-ISOTYPE 文件夹，应已迁至顶层 03')

# ---- 1c. v3.2.0 结构约定：统一入口 / 案例目录 / 阶段 / 根目录 / 脚本 ----
LAYER_DIRS = (LOGIC, CASES, ISOTYPE, STYLE, GESTALT, THEME)

for d in LAYER_DIRS:
    if d.is_dir() and not (d / 'README.md').is_file():
        issues.append(f'板块缺少统一入口 README.md：{d.name}')

# 17 个类型文件夹各有 00-标签说明.md 与「非空」的 案例/ 子目录
for td in sorted(CASES.glob('*/00-标签说明.md')):
    cdir = td.parent / '案例'
    if not cdir.is_dir():
        issues.append(f'类型文件夹缺少 案例/ 子目录：{td.parent.name}')
    elif not any(cdir.iterdir()):
        issues.append(f'案例/ 为空且无占位说明：{rel(cdir)}')

if not (STYLE / '图表与视觉编码.md').is_file():
    issues.append('04/ 缺少 图表与视觉编码.md')

for i in range(1, 9):
    if not list(THEME.glob(f'{i:02d}-*/README.md')):
        issues.append(f'06/ 缺少第 {i:02d} 阶段目录的 README.md')

# 根目录只保留 README.md；治理文档集中在 docs/
root_mds = sorted(p.name for p in ROOT.glob('*.md'))
if root_mds != ['README.md']:
    issues.append(f'根目录应只保留 README.md，实有：{root_mds}')
for name in ('README.md', '导入与更新指南.md', '仓库对比分析-fengbaifan信息图形风格库.md'):
    if not (ROOT / 'docs' / name).is_file():
        issues.append(f'docs/ 缺少文档：{name}')

# scripts/ 只留常驻校验，一次性脚本归 archive/
if not (ROOT / 'scripts' / 'validate_repo.py').is_file():
    issues.append('scripts/ 缺少常驻校验 validate_repo.py')
if not (ROOT / 'scripts' / 'archive' / 'README.md').is_file():
    issues.append('scripts/archive/ 缺少存档说明 README.md')
for p in sorted((ROOT / 'scripts').glob('*.py')):
    if p.name != 'validate_repo.py':
        issues.append(f'scripts/ 下的一次性脚本应归入 archive/：{p.name}')

# ---- 2. 02 层：17 个类型文件夹 + 必备规范文档 ----
type_docs = sorted(CASES.glob('*/00-标签说明.md'))
if len(type_docs) != TYPE_FOLDER_COUNT:
    issues.append(
        f'02/ 类型文件夹应为 {TYPE_FOLDER_COUNT} 个（*/00-标签说明.md），实有 {len(type_docs)}'
    )

for name in REQUIRED_CASE_DOCS:
    if not (CASES / name).is_file():
        issues.append(f'02/ 缺少必备文档：{name}')

# ---- 3. 案例目录：一案例一目录，核心文件齐全 ----
case_dirs = sorted(p for p in CASES.glob('*/案例/CASE-*') if p.is_dir())
case_ids = {d.name[:9] for d in case_dirs}

for d in case_dirs:
    for need in CASE_CORE_FILES:
        if not (d / need).is_file():
            issues.append(f'{rel(d)} 缺少 {need}')
    ana = d / '分析.md'
    if not ana.is_file():
        continue
    text = ana.read_text('utf-8')
    if 'case_id:' not in text:
        issues.append(f'{rel(ana)} 缺少 front matter 字段 case_id')
    for name in CASE_SECTIONS:
        if name not in text:
            issues.append(f'{rel(ana)} 缺少段落「{name}」')
    m = re.search(r'image_path:\s*"([^"]+)"', text)
    if m:
        target = (ana.parent / unquote(m.group(1))).resolve()
        if not target.is_file():
            issues.append(f'{rel(ana)} 指向的图版不存在：{m.group(1)}')
        elif target.parent != d.resolve():
            issues.append(f'{rel(ana)} 的图版不在同一案例目录内：{m.group(1)}')

# 图片必须落在 CASE 目录内
for path in ROOT.rglob('*'):
    if '.git' in path.parts or '.workbuddy' in path.parts:
        continue
    if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
        if not (path.parent.name.startswith('CASE-') and path.parent.parent.name == '案例'):
            issues.append(f'图片只能放在 02/…/案例/CASE-xxxx/ 内：{rel(path)}')

# ---- 3b. 数据表（V3 规范）----
pending_dict: list[str] = []


def parse_front(text: str, key: str) -> str:
    m = re.search(rf'^{key}:\s*(.*?)\s*$', text, flags=re.MULTILINE)
    return m.group(1).strip().strip('"\'') if m else ''


for d in case_dirs:
    ana = d / '分析.md'
    if not ana.is_file():
        continue
    text = ana.read_text('utf-8')
    status = parse_front(text, 'dataset_status')
    if not status:
        issues.append(f'{rel(ana)} 缺少 dataset_status（三档之一，必填）')
        continue
    if status not in DATASET_STATUS:
        issues.append(f'{rel(ana)} 的 dataset_status 非法：{status!r}')
        continue

    ddict = parse_front(text, 'dataset_dict')
    if not ddict:
        issues.append(f'{rel(ana)} 缺少 dataset_dict（任何状态都必须有数据字典）')
    else:
        t = (ana.parent / ddict).resolve()
        if not t.is_file():
            issues.append(f'{rel(ana)} 指向的数据字典不存在：{ddict}')
        else:
            dtext = t.read_text('utf-8')
            for need in ('不可推断', '复算', '计数结构'):
                if need not in dtext:
                    issues.append(f'{rel(t)} 缺少「{need}」内容')

    dpath = parse_front(text, 'dataset_path')
    if status in ('complete', 'partial') and not dpath:
        issues.append(f'{rel(ana)} 状态为 {status} 但缺少 dataset_path')
    if dpath:
        t = (ana.parent / dpath).resolve()
        if not t.is_file():
            issues.append(f'{rel(ana)} 指向的基础数据集不存在：{dpath}')

    for csvf in sorted(d.glob('*.csv')):
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
                issues.append(f'{rel(csvf)} 第 {lineno} 行列数 {len(row)} ≠ 表头 {len(head)}')
                break

# ---- 4. 05 层：14 条原则各一份，A–G 齐全 ----
gestalt_files = sorted(GESTALT.glob('*.md'))
expected_rules = [f'{i:02d}-' for i in range(1, GESTALT_RULE_COUNT + 1)]
rule_docs = [p for p in gestalt_files if p.name[:3] in expected_rules]

if len(rule_docs) != GESTALT_RULE_COUNT:
    issues.append(f'05/ 应有 {GESTALT_RULE_COUNT} 份原则文档（01–14），实有 {len(rule_docs)}')
for prefix in expected_rules:
    if not any(p.name.startswith(prefix) for p in gestalt_files):
        issues.append(f'05/ 缺少编号为 {prefix[:-1]} 的原则文档')

if not (GESTALT / '00-总览与索引.md').is_file():
    issues.append('05/ 缺少 00-总览与索引.md')

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

# ---- 5. 全库相对链接与跨文档锚点 ----
LINK = re.compile(r'!?\[[^\]\n]*\]\(([^)\n]+)\)')
HEADING = re.compile(r'^#{1,6}\s+(.+?)\s*$', re.MULTILINE)


def gh_slug(text: str) -> str:
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

# ---- 6. 案例索引覆盖全部案例 ----
index = CASES / '案例索引.md'
if index.is_file():
    n_index = len(re.findall(r'CASE-\d{4}', index.read_text('utf-8')))
    if n_index < len(case_ids):
        issues.append(f'案例索引只提到 {n_index} 次 CASE 编号，少于案例目录数 {len(case_ids)}')

if issues:
    for i in issues:
        print('ERROR:', i)
    print(f'\n共 {len(issues)} 个问题')
    sys.exit(1)

n_csv = len(list(CASES.glob('*/案例/CASE-*/*.csv')))
n_dict = len(list(CASES.glob('*/案例/CASE-*/数据字典.md')))
n_entry = sum(1 for d in LAYER_DIRS if (d / 'README.md').is_file())
n_case_sub = sum(1 for td in CASES.glob('*/00-标签说明.md') if (td.parent / '案例').is_dir())
print(
    f'OK: {len(md_files)} 份 Markdown、{len(logic_files)} 份逻辑定义、'
    f'{n_entry}/6 个板块入口、{len(type_docs)} 个类型文件夹（{n_case_sub} 个含 案例/）、'
    f'{len(case_dirs)} 个案例目录、{len(rule_docs)} 条格式塔原则、'
    f'{n_csv} 张 CSV、{n_dict} 份数据字典；'
    '相对链接与锚点全部有效，01/ 无图片，图片均在案例目录内，'
    '六层结构、docs/ 与 scripts/ 归档、数据表状态均自洽。'
)
