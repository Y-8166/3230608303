"""更新案例索引：13 条补字典路径与状态、汇总计数、加计数结构列。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
idx = ROOT / '02-信息图形类型案例' / '案例索引.md'
text = idx.read_text('utf-8')

STATUS = {
    'CASE-0001': '无', 'CASE-0002': '无', 'CASE-0004': '无', 'CASE-0005': '无',
    'CASE-0006': '无', 'CASE-0008': '无', 'CASE-0010': '无', 'CASE-0011': '无',
    'CASE-0013': '无', 'CASE-0015': '无', 'CASE-0016': '无',
    'CASE-0012': '部分', 'CASE-0014': '部分',
}
PATHS = {
    'CASE-0001': '03-时间轴型-Timeline/案例/CASE-0001-编年曲线',
    'CASE-0002': '09-层级表现型-Hierarchical/案例/CASE-0002-进化层级图',
    'CASE-0004': '01-混合型-Mixed-Charts/案例/CASE-0004-绘画编目',
    'CASE-0005': '02-文字型列表型-Informational-List/案例/CASE-0005-电路符号图鉴',
    'CASE-0006': '07-地标型-Location/案例/CASE-0006-城市空间规划图',
    'CASE-0008': '02-文字型列表型-Informational-List/案例/CASE-0008-人物文字列表',
    'CASE-0010': '04-示意图型-How-to/案例/CASE-0010-分层三明治',
    'CASE-0011': '05-流程图型-Process/案例/CASE-0011-城市流程路线',
    'CASE-0012': '06-比较型-Comparison/案例/CASE-0012-体育人物比较',
    'CASE-0013': '07-地标型-Location/案例/CASE-0013-轨道交通网络',
    'CASE-0014': '08-图片式-Photo-graphic/案例/CASE-0014-摄影嵌入图表',
    'CASE-0015': '15-编年编目复合型-Hybrid/案例/CASE-0015-宇宙旅程混合图',
    'CASE-0016': '16-三维型-3D/案例/CASE-0016-轴测分层生态图',
}
# 计数结构判定（与 计数结构筛查.md 一致）
KIND = {
    'CASE-0001': '非计数', 'CASE-0002': '非计数', 'CASE-0003': '分级色阶', 'CASE-0004': '一线一画',
    'CASE-0005': '枚举栅格', 'CASE-0006': '拓扑', 'CASE-0007': '混合统计', 'CASE-0008': '重复出镜',
    'CASE-0009': '环形编年', 'CASE-0010': '层序', 'CASE-0011': '流程版式',
    'CASE-0012': '双列对照', 'CASE-0013': '节点—连线', 'CASE-0014': '柱图', 'CASE-0015': '有刻度无单位',
    'CASE-0016': '装饰性重复',
}

lines = text.split('\n')
out = []
for ln in lines:
    if ln.startswith('|') and 'CASE-' in ln and '数据表 |' not in ln:
        cid = ln.split('CASE-')[1][:4]
        key = 'CASE-' + cid
        cells = ln.split(' | ')
        if key in STATUS and len(cells) >= 7:
            cells[-1] = f'[{STATUS[key]}]({PATHS[key]}/数据字典.md)' if STATUS[key] != '无' \
                else f'[无]({PATHS[key]}/数据字典.md)'
            ln = ' | '.join(cells)
        # 追加计数结构列（表头稍后单独补）
        if key in KIND:
            ln = ln.rstrip(' |') + f' | {KIND[key]} |'
    out.append(ln)
text = '\n'.join(out)

text = text.replace(
    '| 图例缩略图 | ID | 来源页 | 案例 | 主要逻辑 | 主要表现 | 数据表 |',
    '| 图例缩略图 | ID | 来源页 | 案例 | 主要逻辑 | 主要表现 | 数据表 | 计数结构 |')
text = text.replace(
    '| --- | --- | --- | --- | --- | --- | --- |',
    '| --- | --- | --- | --- | --- | --- | --- | --- |')

text = text.replace(
    '**数据表状态**（口径见 [数据表规范](数据表规范.md)）：`完整` 0 例 · `部分` 3 例（CASE-0003、CASE-0007、CASE-0009）· `无` 14 例（仅待建字典）。`无` 不等于免做，须在字典里写明"为何无值"。',
    '**数据表状态**（口径见 [数据表规范](数据表规范.md)）：`完整` 0 例 · `部分` 5 例（CASE-0003、CASE-0007、CASE-0009、CASE-0012、CASE-0014）· `无` 11 例（均已有字典）。'
    '**16 案已全部建字典**，`无` 不等于免做——字典里写明"为何无值"与"禁止推断清单"，并按 [计数结构筛查](计数结构筛查.md) 逐案判定能否还原数据。')

text = text.replace(
    '**数据表提醒**：`部分` 三例的 CSV 里有相当比例的格子是空的',
    '**数据表提醒**：`部分` 五例的 CSV 里有相当比例的格子是空的')

text = text.replace(
    '[课件核验](课件来源与分类核验.md) · [设计准则](设计准则与评价方法.md) · [案例模板](案例分析模板.md) · [数据表规范](数据表规范.md)',
    '[课件核验](课件来源与分类核验.md) · [设计准则](设计准则与评价方法.md) · [案例模板](案例分析模板.md) · [数据表规范](数据表规范.md) · [计数结构筛查](计数结构筛查.md)')

idx.write_text(text, 'utf-8')
print('索引已更新')

# 校验行数与列数是否一致
rows = [l for l in text.split('\n') if l.startswith('| <img') or l.startswith('| *暂无')]
print('案例行数', len(rows))
for r in rows[:3]:
    print(len(r.split(' | ')), '列')
