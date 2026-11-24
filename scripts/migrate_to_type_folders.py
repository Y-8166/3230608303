#!/usr/bin/env python3
"""把 02 层迁移为「类型文件夹 + 一案例一目录」结构（照 fengbaifan 库）。

用法：
    python scripts/migrate_to_type_folders.py --dry   # 只打印映射，不动文件
    python scripts/migrate_to_type_folders.py         # 执行
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / '02-信息图形类型案例'
RECORDS = CASES / '案例记录'
IMAGES = CASES / '案例图'
DATASETS = CASES / '案例数据'

DRY = '--dry' in sys.argv

TYPE_MAP = [
    ('01-混合型信息图形-Mixed-Charts.md', '01-混合型-Mixed-Charts'),
    ('02-文字型与列表型信息图形-Informational-List.md', '02-文字型列表型-Informational-List'),
    ('03-时间轴型信息图形-Timeline.md', '03-时间轴型-Timeline'),
    ('04-示意图型-How-to.md', '04-示意图型-How-to'),
    ('05-流程图型-Process.md', '05-流程图型-Process'),
    ('06-比较型-Comparison.md', '06-比较型-Comparison'),
    ('07-地标型-Location.md', '07-地标型-Location'),
    ('08-图片式-Photographic.md', '08-图片式-Photo-graphic'),
    ('09-层级表现型-Hierarchical.md', '09-层级表现型-Hierarchical'),
    ('10-单一图表型-Single-Chart.md', '10-单一图表型-Single-Chart'),
    ('11-可视化文本型-Visualized-Text.md', '11-文字可视化-Visualized-Text'),
    ('12-解剖剖析型-Anatomical.md', '12-解剖型-Anatomical'),
    ('13-可视化简历型-Visual-Resume.md', '13-视觉简历-Visual-Resume'),
    ('14-手稿型-Sketch.md', '14-手稿型-Sketch'),
    ('15-编年编目混合图-Chronological-Catalog.md', '15-编年编目复合型-Hybrid'),
    ('16-三维信息图形-3D.md', '16-三维型-3D'),
    ('17-词云信息图-Word-Cloud-Infographic.md', '17-词云信息图-Word-Cloud'),
    ('18-ISOTYPE-基础设计方法.md', '18-ISOTYPE-基础设计方法'),
]

CASE_TYPE = {
    'CASE-0001': '03-时间轴型-Timeline',
    'CASE-0002': '09-层级表现型-Hierarchical',
    'CASE-0003': '07-地标型-Location',
    'CASE-0004': '01-混合型-Mixed-Charts',
    'CASE-0005': '02-文字型列表型-Informational-List',
    'CASE-0006': '07-地标型-Location',
    'CASE-0007': '01-混合型-Mixed-Charts',
    'CASE-0008': '02-文字型列表型-Informational-List',
    'CASE-0009': '03-时间轴型-Timeline',
    'CASE-0010': '04-示意图型-How-to',
    'CASE-0011': '05-流程图型-Process',
    'CASE-0012': '06-比较型-Comparison',
    'CASE-0013': '07-地标型-Location',
    'CASE-0014': '08-图片式-Photo-graphic',
    'CASE-0015': '15-编年编目复合型-Hybrid',
    'CASE-0016': '16-三维型-3D',
}

STATUS_ZH = {'complete': '完整', 'partial': '部分', 'none': '无'}

rename: dict[Path, Path] = {}

for old_name, folder in TYPE_MAP:
    rename[CASES / old_name] = CASES / folder / '00-标签说明.md'

for rec in sorted(RECORDS.glob('CASE-*.md')):
    cid = rec.name[:9]
    folder = CASE_TYPE.get(cid)
    if not folder:
        print(f'!! {cid} 未登记类型，跳过')
        continue
    cdir = CASES / folder / '案例' / rec.stem
    rename[rec] = cdir / '分析.md'
    img = IMAGES / f'{cid}-课件图例.webp'
    if img.is_file():
        rename[img] = cdir / '原图.webp'
    for data in sorted(DATASETS.glob(f'{cid}-*')):
        rename[data] = cdir / data.name[len(cid) + 1:]

rename[RECORDS / 'README.md'] = CASES / '案例写作规范.md'

print('=== 重命名映射 ===')
for old, new in sorted(rename.items()):
    print(f'{old.relative_to(ROOT)}  ->  {new.relative_to(ROOT)}')
print(f'共 {len(rename)} 项')

if DRY:
    missing = [p for p in rename if not p.exists()]
    print(f'\n源文件缺失 {len(missing)} 项')
    for p in missing:
        print('  !!', p.relative_to(ROOT))
    sys.exit(0)

# ---------- 执行 ----------
LINK = re.compile(r'(!?\[[^\]\n]*\]\()([^)\n]+)(\))')
IMGTAG = re.compile(r'(<img[^>]*\bsrc=")([^"]+)(")')

texts: dict[Path, str] = {}
for f in sorted(ROOT.rglob('*.md')):
    if '.git' in f.parts or '.workbuddy' in f.parts:
        continue
    texts[f] = f.read_text('utf-8')

for old, new in rename.items():
    new.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'mv', str(old), str(new)], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)

n_links = 0


def rewrite(link: str, old_base: Path, new_base: Path) -> str | None:
    """把一条相对链接从旧基准重算到新基准；目录链接与站外链接不动。"""
    raw = link.strip()
    wrapped = raw.startswith('<') and raw.endswith('>')
    if wrapped:
        raw = raw[1:-1]
    if not raw or raw.startswith('#') or urlparse(raw).scheme or raw.startswith('//'):
        return None
    pure, sep, anchor = raw.partition('#')
    qs = ''
    if '?' in pure:
        pure, _, qs = pure.partition('?')
    if not pure:
        return None
    target = (old_base / unquote(pure)).resolve()
    if target in rename:
        tgt_new = rename[target]
    elif target.is_file():
        tgt_new = target
    else:
        return None
    if old_base == new_base and tgt_new == target:
        return None
    rel_path = os.path.relpath(tgt_new, new_base).replace(os.sep, '/')
    out = rel_path + (('#' + anchor) if sep else '') + (('?' + qs) if qs else '')
    return f'<{out}>' if wrapped else out


for old_path, text in texts.items():
    new_path = rename.get(old_path, old_path)
    base_old, base_new = old_path.parent, new_path.parent

    def sub(m: re.Match) -> str:
        global n_links
        got = rewrite(m.group(2), base_old, base_new)
        if got is None:
            return m.group(0)
        n_links += 1
        return m.group(1) + got + m.group(3)

    new_text = LINK.sub(sub, text)
    new_text = IMGTAG.sub(sub, new_text)

    new_path.parent.mkdir(parents=True, exist_ok=True)
    new_path.write_text(new_text, 'utf-8')

# ---------- 后处理：image_path、README、原图来源 ----------
n_readme = 0
for rec in sorted(CASES.glob('*/案例/CASE-*/分析.md')):
    cdir = rec.parent
    text = rec.read_text('utf-8')
    if 'image_path:' in text:
        text = re.sub(r'^image_path:.*$', 'image_path: "原图.webp"', text, flags=re.MULTILINE)
        rec.write_text(text, 'utf-8')
    if new_cfg := re.search(r'^dataset_path:\s*"([^"]+)"', text, flags=re.MULTILINE):
        text = re.sub(r'^dataset_path:.*$', 'dataset_path: "基础数据集.csv"', text, flags=re.MULTILINE)
    if re.search(r'^dataset_dict:', text, flags=re.MULTILINE):
        text = re.sub(r'^dataset_dict:.*$', 'dataset_dict: "数据字典.md"', text, flags=re.MULTILINE)
    rec.write_text(text, 'utf-8')

    def fm(key: str) -> str:
        m = re.search(rf'^{key}:\s*(.*)$', text, flags=re.MULTILINE)
        return m.group(1).strip().strip('"\'') if m else ''

    m_status = re.search(r'^dataset_status:\s*(\w+)', text, flags=re.MULTILINE)
    status = STATUS_ZH.get(m_status.group(1), '未声明') if m_status else '未声明'
    title_m = re.search(r'^# (.+)$', text, flags=re.MULTILINE)
    title = title_m.group(1).strip() if title_m else cdir.name

    folder = cdir.parent.parent.name
    img = cdir / '原图.webp'
    size = ''
    if img.is_file():
        w, h = Image.open(img).size
        size = f'{w}×{h}'

    files = [('分析.md', '观测事实、A–E 五维、分类与核验')]
    if img.is_file():
        files.append(('原图.webp', f'课件研究缩略图（{size}）'))
    files.append(('原图来源.md', '出处、页码、权利状态'))
    for extra, desc in (('基础数据集.csv', '基础数据表'), ('辅助指标.csv', '图例刻度与画布事实'),
                        ('数据字典.md', '字段、粒度、缺失清单、复算式')):
        if (cdir / extra).is_file():
            files.append((extra, desc))
    rows = '\n'.join(f'| [{a}]({a}) | {b} |' for a, b in files)

    (cdir / 'README.md').write_text(f'''# {title}

| 项 | 内容 |
|---|---|
| 表现类型 | [{folder}](../../00-标签说明.md) |
| 数据表状态 | {status} |
| 课件页码 | {fm("source_page") or "—"} |

## 文件

| 文件 | 内容 |
|---|---|
{rows}

← 返回 [案例索引](../../../案例索引.md) ｜ [类型说明](../../00-标签说明.md) ｜ [数据表规范](../../../数据表规范.md)
''', 'utf-8')

    (cdir / '原图来源.md').write_text(f'''# 原图来源｜{title}

| 项 | 内容 |
|---|---|
| 作品名／作者 | 待核实（课件未标注） |
| 出处 | 用户上传课件《{fm("source")}》第 {fm("source_page") or "?"} 页 |
| 图版文件 | `原图.webp`{f"（{size}）" if size else ""}，由课件内嵌图提取 |
| 权利状态 | 使用许可不明；仅限本库研究对照，对外再传播前须核实原作者与出版方 |
| 入库日期 | 2026-11-19 |

> 本文件只记录出处与权利状态，不替代原作者信息。拿到高清原作后，替换 `原图.webp` 并补全作者、出版方与授权方式。
''', 'utf-8')
    n_readme += 1

# 删除已并入规范的旧说明，清理空目录
readme_data = DATASETS / 'README.md'
if readme_data.is_file():
    subprocess.run(['git', 'rm', '-f', '-q', str(readme_data)], cwd=ROOT, check=False)
for d in (IMAGES, RECORDS, DATASETS):
    if d.is_dir():
        try:
            d.rmdir()
        except OSError:
            pass

print(f'\n完成：移动 {len(rename)} 项，重写 {n_links} 条链接，生成案例卡片 {n_readme} 份')
