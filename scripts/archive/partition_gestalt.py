"""
一次性脚本：05 格式塔层按 fengbaifan 五分区重构后的链接重算。

背景：14 份原则文档由 `05-格式塔知觉规则/` 层根移入 `01-规则库/`。
- 规则文档之间互相链接为同目录相对路径，保持不变；
- 规则文档指向层根 README/00/99 的链接需上跳一级；
- 规则文档指向其他板块的链接需上跳两级；
- 层根三份文档指向 14 份原则的链接需加 `01-规则库/` 前缀；
- 跨层文档（如 CASE 数据字典）里带完整层名的链接需插入 `01-规则库/`。

不可重复运行：已处理过的文档再次运行会把 `](../` 继续叠成 `](../../`。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GESTALT = ROOT / '05-格式塔知觉规则'
RULE_DIR = GESTALT / '01-规则库'
ROOT_DOCS = ('README.md', '00-总览与索引.md', '99-证据分级与待办.md')
RULES = sorted(p.name for p in RULE_DIR.glob('*.md'))
assert len(RULES) == 14, f'期望 14 份原则文档，实有 {len(RULES)}'

changed = []


def save(path, old, new):
    if new != old:
        path.write_text(new, encoding='utf-8')
        changed.append(str(path.relative_to(ROOT)))


# 1. 规则文档内部：先跨层上跳，再补层根文档的一级上跳
for p in sorted(RULE_DIR.glob('*.md')):
    t = p.read_text(encoding='utf-8')
    orig = t
    t = t.replace('](../', '](../../')
    for doc in ROOT_DOCS:
        t = t.replace('](' + doc, '](../' + doc)
    save(p, orig, t)

# 2. 层根三份文档：指向 14 份原则的链接加前缀
for name in ROOT_DOCS:
    p = GESTALT / name
    t = p.read_text(encoding='utf-8')
    orig = t
    for r in RULES:
        t = t.replace('](' + r, '](01-规则库/' + r)
    save(p, orig, t)

# 3. 全库其余 Markdown：带完整层名的链接插入 01-规则库/
for p in sorted(ROOT.rglob('*.md')):
    s = str(p)
    if '.git' in s or '.workbuddy' in s or p.is_relative_to(GESTALT):
        continue
    t = p.read_text(encoding='utf-8')
    orig = t
    for r in RULES:
        t = t.replace('05-格式塔知觉规则/' + r, '05-格式塔知觉规则/01-规则库/' + r)
    save(p, orig, t)

print(f'链接重算完成，修改 {len(changed)} 份文档：')
for c in changed:
    print('  ' + c)
