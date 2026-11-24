"""重建 13 条案例的 README 卡片：补数据表状态、文件清单与计数结构一行。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / '02-信息图形类型案例'

STATUS_ZH = {'complete': '完整', 'partial': '部分', 'none': '无'}

# 一行摘要：这条图的计数结构判成了什么
SUMMARY = {
    'CASE-0001': '按期间分段的螺旋路径，段外放射线无刻度；段 6 与标签 6 一一对应',
    'CASE-0002': '谱系示意，纵轴非等时标度；15 个地质期、9 条注记可数，带宽无量纲',
    'CASE-0004': '一线一画的等宽排布，理论上可数、缩图不可数；图例 9 行 ≠ 期间 6 格',
    'CASE-0005': '8 列栅格枚举，符号 ≈112 个；等大、可数，但无固定单位',
    'CASE-0006': '环形都城的拓扑图，环 4、扇区 6、外挂节点 3；无比例尺、无数量编码',
    'CASE-0008': '含饼图与 TOP10 条形，数值全糊化；中部等大小像为重复出镜，非计数单元',
    'CASE-0010': '爆炸分层 9 层、配料 8 种；层厚是形态需要，不是用量',
    'CASE-0011': '路牌 6 = 板块 6；4 条条形只给次序不给差距',
    'CASE-0012': '1975 vs 2014 双列对照 24 行，7 个值可逐字读；年龄组端点数字不可辨',
    'CASE-0013': '线网拓扑，无客流无站距；行政区分区 5 个完整',
    'CASE-0014': '三组柱图 25 个国别值 + NHS 总数与增幅；增幅 30.35% 与印刷值互证',
    'CASE-0015': '轨迹 5、图标 6、天体 8；底部刻线 >100 但无标签，有刻度 ≠ 有单位',
    'CASE-0016': '轴测 6 层、注记 8；满图树鸟企鹅为装饰性重复，改数字不会变',
}


def main():
    n = 0
    for ana in sorted(CASES.glob('*/案例/CASE-*/分析.md')):
        cdir = ana.parent
        cid = '-'.join(cdir.name.split('-')[:2])
        if cid not in SUMMARY:
            continue
        text = ana.read_text('utf-8')
        status = 'none'
        for ln in text.split('\n'):
            if ln.startswith('dataset_status:'):
                status = ln.split(':', 1)[1].strip()
                break
        title = cdir.name.split('-', 2)[2] if cdir.name.count('-') >= 2 else cdir.name
        title = cdir.name[10:]

        folder = cdir.parent.parent.name
        num = folder.split('-', 1)[0]
        type_link = f'[{folder}](../../00-标签说明.md)'
        img = cdir / '原图.webp'
        size = ''
        if img.is_file():
            from PIL import Image
            w, h = Image.open(img).size
            size = f'{w}×{h}'

        files = [('分析.md', '观测事实、A–E 五维、分类与核验')]
        if img.is_file():
            files.append(('原图.webp', f'课件研究缩略图（{size}）'))
        files.append(('原图来源.md', '出处、页码、权利状态'))
        for extra, desc in (('基础数据集.csv', '基础数据表'), ('辅助指标.csv', '图例刻度与画布事实'),
                            ('数据字典.md', '字段、计数结构、缺口清单、复算式')):
            if (cdir / extra).is_file():
                files.append((extra, desc))

        rows = '\n'.join(f'| [{a}]({a}) | {b} |' for a, b in files)
        page = ''
        for ln in text.split('\n'):
            if ln.startswith('source_page:'):
                page = ln.split(':', 1)[1].strip()

        md = f'''# {cid} {title}

| 项 | 内容 |
|---|---|
| 表现类型 | {type_link} |
| 数据表状态 | {STATUS_ZH.get(status, status)}（`{status}`） |
| 计数结构 | {SUMMARY[cid]} |
| 课件页码 | {page} |

## 文件

| 文件 | 内容 |
|---|---|
{rows}

← 返回 [案例索引](../../../案例索引.md) ｜ [类型说明](../../00-标签说明.md) ｜ [数据表规范](../../../数据表规范.md) ｜ [计数结构筛查](../../../计数结构筛查.md)
'''
        (cdir / 'README.md').write_text(md, 'utf-8')
        n += 1
        print('重建', cid, status)
    print('共', n, '份')


if __name__ == '__main__':
    main()
