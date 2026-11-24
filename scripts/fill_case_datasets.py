"""为 13 条存量案例补 dataset_status 三字段，并把通用的 B 节换成按计数结构写的实证内容。

只用纯字符串操作，不用正则（运行环境会把反斜杠降级成斜杠）。
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / '02-信息图形类型案例'

NONE_B = """## B. 统计图形与计算

**图面有无统计量**：{has_value}

**可数结构**（逐项计数与判据见 [数据字典](数据字典.md) §3）：{countable}

**能算的与不能算的**：{recompute}

## C. 视觉编码"""

PARTIAL_B = """## B. 统计图形与计算

**数据表**：[基础数据集.csv](基础数据集.csv)（{rows}）× [辅助指标.csv](辅助指标.csv) ｜ 字典：[数据字典.md](数据字典.md)

{body}

**复算**：{recompute}

## C. 视觉编码"""

CASES_META = {
    'CASE-0001': dict(
        status='none', path='',
        has='没有。全图无一个数字，主体是按期间分段的螺旋路径，段外放射细线既无刻度也无基准。',
        countable='齿轮弧段 6 / 期间标签 6（1:1） / 色彩系 3 / 可辨期间端点 2 / 放射细线不可数。',
        recompute='段数 6 与标签数 6 相等，说明没有跨段合并；色彩系只有 3 种却跨 6 段使用，说明配色编码的是比"期间"更高一级的分组，而非逐段区分。除此之外无可算量。'),
    'CASE-0002': dict(
        status='none', path='',
        has='没有。左列为 15 个地质期名，中央为谱系带，右侧 9 条事件注记，全图无年代值、无比例、无物种数。',
        countable='地质期 15 / 事件注记 9 / 主谱系带 6 / 末级细支 17–20（估） / 带宽变化型 2 类。',
        recompute='纵轴不是时间标度：`JURASSIC` 栏目测约 30px、`RECENT` 栏约 12px，比值 2.5；而实际时长比约 4800 倍，差三个数量级。谱系带宽度因此也不能读成物种数——这是本图最该先排除的两种误读。'),
    'CASE-0004': dict(
        status='none', path='',
        has='有，但读不出。每幅画一根竖线（等宽，从同一基线长出），线上叠气泡（直径约 4 档、蓝红两色）；右上图例 9 行、底部期间面板 6 格。',
        countable='期间 6（可逐字读） / 图例行 9 / 气泡直径档 4 / 气泡色彩 2 / 竖线数百不可数 / 横轴年份不可读。',
        recompute='图例 9 行 ≠ 期间 6 格，说明图例至少含一个非期间维度；气泡色彩仅 2 系却要覆盖 6 个期间，说明色彩只承担二分。两条都是数出来的否定结论，用来排除"6 类图例 = 6 个时期"的误读。'),
    'CASE-0005': dict(
        status='none', path='',
        has='没有。整版是 8 列栅格，每格一个电路符号 + 一行英文名，全图零数值。',
        countable='列 8 / 行 14（按行距推算） / 符号总数 ≈112 / 可辨符号名 6 / 分组标题 0。',
        recompute='8 × 14 = 112；若末行为空则为 104。两值相差正好一行，说明列数是硬约束、行数是唯一不确定项，逐格点数得到 104 或 112 即可定案。'),
    'CASE-0006': dict(
        status='none', path='',
        has='没有。环形都城平面图，只有拓扑（谁挨着谁），无人口、面积、密度，也无比例尺。',
        countable='同心环 4 / 外环扇区 6（名称可辨 4） / 放射主路 6 / 外挂放大节点 3 / 比例尺 0。',
        recompute='扇区 6 = 主路 6，说明扇区完全由主路切分；外挂节点 3 < 扇区 6，说明只有半数扇区获得放大图——这是本图唯一的编辑权重证据，可数、可核。'),
    'CASE-0008': dict(
        status='none', path='',
        has='有，但读不出。含 1 张饼图（4 扇区）、1 张区域图、1 组 TOP 榜单条形（10 条），全部数值在缩图下糊化。',
        countable='成员卡 4 / 统计图 3 / 饼图扇区 4 / 榜单条 10 / 中部小像对 5 / 可辨数值 0。',
        recompute='饼图 4 扇 = 4 色，一一对应无重复用色，说明配色干净；榜单 10 条 = 标题里的 "TOP 10"，条数与标题自洽。两条都只验结构，不产生数值。'),
    'CASE-0010': dict(
        status='none', path='',
        has='没有。爆炸分层图，9 层食材、每层一枚标签，无克数、无卡路里、无比例。',
        countable='食材层 9 / 不同配料 8（白面包上下各一） / 重复配料 1 / 右侧配方行约 9 / 数值 0。',
        recompute='层 9 − 重复 1 = 配料 8，与右侧配方清单（约 8–9 行）吻合。层厚排序（面包 > 牛肉 > 番茄 > 洋葱 > 芝士 > 生菜 > 蛋黄酱）共 7 档，与"9 层"不等 → 层厚是形态需要，不是用量。'),
    'CASE-0011': dict(
        status='none', path='',
        has='有，但读不出。全图唯一的统计图形是 SPECIALITIES 右侧的 4 条小条形，长度递减，轴标签与端点数字均糊化。',
        countable='板块（路牌） 6 / 路牌与板块 1:1 / 小条形 4 / 人物插画 5 / 建筑道具 20+ / 可辨数值 0。',
        recompute='板块 6 = 路牌 6，说明流程入口无遗漏；4 条条形长度单调递减，可读出第 1 到第 4 的次序，但读不出差距——排序不等于数值。'),
    'CASE-0012': dict(
        status='partial', path='基础数据集.csv', rows='11 列 × 24 行',
        body='按区块分五段：顶部三组百分比（3 行，两值均可逐字读）、中部同心圆（3 行，仅存标签）、国家指标行（2 行）、年龄组（9 行）、社会指标行（7 行）。**可逐字读出的只有 7 个数**：83→100、28→53、26→22（三组百分比）与 73.3→82.8 年（预期寿命）。',
        recompute='H01 由 83 升至 100，增幅 20.5%；H02 由 28 升至 53，增幅 89.3%；H03 由 26 降至 22，降幅 15.4%——三者中只有 H02 接近翻倍，H03 是唯一下降项。预期寿命 82.8 − 73.3 = 9.5 年，38 年跨度内年均 +0.25 年。年龄组与 7 项社会指标因端点数字达 6–7 位、缩图下只能辨出前两位，一律留空标 `not_readable`，未做估读。'),
    'CASE-0013': dict(
        status='none', path='',
        has='没有。纽约地铁线网图，只有连通关系，无客流、无站距、无里程。',
        countable='行政区标 5 / 图例块 4 / 线路色 9–11 / 站点数百不可数 / 换乘站不可数 / 数值 0。',
        recompute='行政区标 5 = 纽约市 5 个区，图面分区完整，是本图唯一可核的完整性判据。图例 4 块中 3 块在页边、1 块（线路色标）嵌在网络内部——色标必须就近对照，这是功能性布置而非随意摆位。'),
    'CASE-0014': dict(
        status='partial', path='基础数据集.csv', rows='11 列 × 32 行',
        body='三组柱图分三段：老龄化 17 国（pct，2007）、肥胖率 8 国（pct，原图未标年份）、NHS 员工 7 项（1998 / 2008）。25 个国别值与 NHS 两个总数、一个增幅均可辨，只有 NHS 的医生与护理四个分项读不出，留空标 `not_readable`。',
        recompute='**NHS 增幅互证**：760,886 ÷ 583,742 − 1 = 30.35%，图上印刷形似 30.3%，差 0.05 个百分点 → 两个总数与增幅互证成立，反证读数正确。**老龄化均值**：17 国求和 315，除以 17 得 18.5%（非人口加权，不得当作"全球水平"）。**英美落差**：34.3 − 24.0 = 10.3 个百分点，英国为美国的 70.0%，其余六国集中在 8.1–13.6%。'),
    'CASE-0015': dict(
        status='none', path='',
        has='有，但读不出。底部有刻线带（目测 >100 条，偶有加高刻线），但无一条标签可辨，等于失去了标度。',
        countable='主轨迹 5 / 天体节点 8 / 航天器图标 6 / 底部刻线 >100 不可数 / 可辨数值 0。',
        recompute='轨迹 5 条 ≠ 图标 6 个，说明不是"一探测器一轨迹"（可能两图标共用一条路径，也可能有装饰性图标）。天体节点 8 个，若含太阳则行星 7 个，与"八大行星"口径不符——图面证据只支持"8 个圆盘"，不支持任何行星计数结论。'),
    'CASE-0016': dict(
        status='none', path='',
        has='没有。轴测爆炸图，6 层生态模块 + 8 条引线注记，无物种数、无面积、无个体数。',
        countable='生态层 6 / 引线注记 8 / 重复树形图标 40+（装饰） / 鸟 6 / 企鹅 4 / 数值 0。',
        recompute='层 6 < 注记 8 → 有 2 层各配 2 条注记，编辑把解释力集中在最需要说明的两层。动物图标共 10 个、层 6 层，平均 1.7 个/层，密度远低于计数型图符图应有的铺满状态——密度本身就是"布景而非计数"的判据。'),
}


def patch_front(text, status, path):
    """在 front matter 的 updated 行后插入三字段，并把 updated 改为今天。"""
    lines = text.split('\n')
    out, done = [], False
    for i, ln in enumerate(lines):
        if ln.startswith('updated:'):
            out.append('updated: 2026-11-24')
            out.append('dataset_status: ' + status)
            out.append('dataset_path: "' + path + '"')
            out.append('dataset_dict: "数据字典.md"')
            done = True
            continue
        out.append(ln)
    assert done, 'front matter 缺 updated 行'
    return '\n'.join(out)


def main():
    changed = 0
    for p in sorted(CASES.glob('*/案例/CASE-*/分析.md')):
        cid = p.parent.name.split('-', 1)[0] + '-' + p.parent.name.split('-', 1)[1][:4]
        cid = '-'.join(p.parent.name.split('-')[:2])
        meta = CASES_META.get(cid)
        if not meta:
            print('SKIP', p.parent.name)
            continue
        text = p.read_text('utf-8')
        if 'dataset_status' in text:
            print('已有字段，跳过', cid)
            continue
        text = patch_front(text, meta['status'], meta['path'])
        head, rest = text.split('## B. 统计图形与计算', 1)
        _, tail = rest.split('## C. 视觉编码', 1)
        if meta['status'] == 'partial':
            b = PARTIAL_B.format(rows=meta['rows'], body=meta['body'], recompute=meta['recompute'])
        else:
            b = NONE_B.format(has_value=meta['has'], countable=meta['countable'], recompute=meta['recompute'])
        new = head + b + '\n' + tail.lstrip('\n')
        p.write_text(new, 'utf-8')
        changed += 1
        print('改写', cid, meta['status'])
    print('共改写', changed, '份')


if __name__ == '__main__':
    main()
