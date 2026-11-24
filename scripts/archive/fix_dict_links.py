"""修正数据字典里的相对链接：按"路径尾部唯一匹配"重算相对路径。

用于 13 份新建字典中跨目录引用写错层深的情况（案例目录深 3 层，指向 02 层根或
其他类型目录时常少写或多写一级 ../）。
"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r'\]\(([^)]+)\)')


def resolve_suffix(link):
    """把断链按尾部片段在仓库里找唯一目标。"""
    parts = [p for p in link.split('/') if p not in ('..', '.')]
    # 从最长后缀开始尝试：先找 3 段，再 2 段，再 1 段（文件名）
    for start in range(0, max(1, len(parts) - 1)):
        tail = parts[start:]
        cands = [p for p in ROOT.rglob(tail[-1]) if p.is_file()]
        # 用尾部路径片段过滤
        keep = []
        for c in cands:
            rel_parts = c.relative_to(ROOT).parts
            if len(rel_parts) >= len(tail) and list(rel_parts[-len(tail):]) == tail:
                keep.append(c)
        if len(keep) == 1:
            return keep[0]
    return None


fixed = 0
for p in sorted((ROOT / '02-信息图形类型案例').glob('*/案例/CASE-*/数据字典.md')):
    text = p.read_text('utf-8')
    orig = text

    def repl(m):
        global fixed
        link = m.group(1)
        if link.startswith(('http', '#', 'mailto')):
            return m.group(0)
        pure = link.split('#', 1)[0]
        target = (p.parent / pure).resolve()
        if target.exists():
            return m.group(0)
        tgt = resolve_suffix(pure)
        if not tgt:
            print('未能修复', p.parent.name, link)
            return m.group(0)
        new = os.path.relpath(tgt, p.parent).replace('\\', '/')
        if '#' in link:
            new += '#' + link.split('#', 1)[1]
        print(f'{p.parent.name}: {link}  ->  {new}')
        fixed += 1
        return '](' + new + ')'

    text = LINK.sub(repl, text)
    if text != orig:
        p.write_text(text, 'utf-8')

print('修复链接', fixed, '处')
