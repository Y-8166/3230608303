"""为 CASE-0012 / CASE-0014 生成数据表（UTF-8 with BOM，LF）。

数值来源与置信度见各案例目录内的数据字典：
- 0012：顶部三组百分比逐字可辨（high）；年龄组与指标行数值不可辨（留空 + not_readable）。
- 0014：三组柱图数值大量可辨（mid）；NHS 分项不可辨。
"""
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASES = os.path.join(ROOT, '02-信息图形类型案例')


def write(path, header, rows):
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(header)
        w.writerows(rows)
    print(os.path.relpath(path, ROOT), len(rows), '行')


# ---------- CASE-0012 ----------
d12 = os.path.join(CASES, '06-比较型-Comparison', '案例', 'CASE-0012-体育人物比较')
h12 = ['metric_id', 'section', 'indicator_es', 'indicator_zh', 'value_1975', 'value_2014',
       'unit', 'evidence_level', 'confidence', 'value_status', 'note']
rows12 = [
    ['H01', '顶部三组百分比', '', '顶部指标 1（图标为拄杖人形，标签不可辨）', 83, 100, 'pct',
     '图面转录', '', 'reported', '两值均在圆内大字印刷，可逐字读取；语义不可辨，不做猜测'],
    ['H02', '顶部三组百分比', '', '顶部指标 2（图标为站立人形，标签不可辨）', 28, 53, 'pct',
     '图面转录', '', 'reported', '同上；1975 侧为蓝、2014 侧为红，色彩承载年份而非类别'],
    ['H03', '顶部三组百分比', '', '顶部指标 3（图标为持物人形，标签不可辨）', 26, 22, 'pct',
     '图面转录', '', 'reported', '唯一下降的一项；降幅 4 个百分点为三者中唯一负值'],
    ['M01', '中部同心圆', 'Renta por capital', '人均收入（标签形似，未确认）', '', '', 'EUR',
     '缺失', '', 'not_readable', '同心圆三层，数值与单位均不可辨，仅登记标签占位'],
    ['M02', '中部同心圆', 'Población', '人口（标签形似，未确认）', '', '', 'person',
     '缺失', '', 'not_readable', '同上'],
    ['M03', '中部同心圆', 'PIB', '国内生产总值（标签形似，未确认）', '', '', 'EUR',
     '缺失', '', 'not_readable', '同上；三圆为等比同心而非部分—整体，不构成饼图'],
    ['L01', '国家指标行', 'Esperanza de vida', '预期寿命', 73.3, 82.8, 'year',
     '图面可辨', 'mid', 'reported', '小数位清晰；单位「años」在图右侧'],
    ['L02', '国家指标行', 'PIB por habitante', '人均 GDP', '', '', 'EUR',
     '缺失', '', 'not_readable', '条形端点数字粘连'],
    ['A00', '年龄组', '0 a 4 años', '0–4 岁', '', '', 'person',
     '缺失', '', 'not_readable', '首行标签被年份刻度带压住，按序位推断为 0–4，未确认'],
    ['A01', '年龄组', '5 a 9 años', '5–9 岁', '', '', 'person', '缺失', '', 'not_readable', '条形端点数字形似 1,301,100'],
    ['A02', '年龄组', '10 a 14 años', '10–14 岁', '', '', 'person', '缺失', '', 'not_readable', '数字形似 3,251,900'],
    ['A03', '年龄组', '15 a 24 años', '15–24 岁', '', '', 'person', '缺失', '', 'not_readable', '数字形似 6,020,200'],
    ['A04', '年龄组', '25 a 34 años', '25–34 岁', '', '', 'person', '缺失', '', 'not_readable', '数字形似 5,254,300'],
    ['A05', '年龄组', '35 a 44 años', '35–44 岁', '', '', 'person', '缺失', '', 'not_readable', '数字形似 4,231,600'],
    ['A06', '年龄组', '45 a 54 años', '45–54 岁', '', '', 'person', '缺失', '', 'not_readable', '数字形似 4,715,300'],
    ['A07', '年龄组', '55 a 64 años', '55–64 岁', '', '', 'person', '缺失', '', 'not_readable', '数字形似 2,885,900'],
    ['A08', '年龄组', '65 y más años', '65 岁以上', '', '', 'person', '缺失', '', 'not_readable', '数字形似 3,250,400'],
    ['I01', '社会指标行', 'Inmigrantes censados', '登记在册移民', '', '', 'person',
     '缺失', '', 'not_readable', '数字形似 828,603；仅右侧有值，左侧空白'],
    ['I02', '社会指标行', 'Desempleados', '失业人口', '', '', 'person',
     '缺失', '', 'not_readable', '数字形似 5,035,000'],
    ['I03', '社会指标行', 'Empleados en el sector público', '公共部门雇员', '', '', 'person',
     '缺失', '', 'not_readable', '条形过长，端点数字被裁'],
    ['I04', '社会指标行', 'Universitarios', '大学生', '', '', 'person',
     '缺失', '', 'not_readable', '数字形似 1,254,000'],
    ['I05', '社会指标行', 'Matrimonios celebrados', '登记结婚数', '', '', 'count',
     '缺失', '', 'not_readable', '数字形似 271,548'],
    ['I06', '社会指标行', 'Efectivos del ejército', '军队员额', '', '', 'person',
     '缺失', '', 'not_readable', '数字形似 121,000'],
    ['I07', '社会指标行', 'Población reclusa', '在押人数', '', '', 'person',
     '缺失', '', 'not_readable', '两值形似 60,000 与 44,764，方向异常，待高清核对'],
]
write(os.path.join(d12, '基础数据集.csv'), h12, rows12)

h12a = ['metric_id', 'subject', 'category', 'metric', 'value', 'unit', 'evidence_level', 'confidence', 'value_status', 'note']
rows12a = [
    ['C01', 'image', 'canvas_fact', 'image_width_px', 420, 'px', '图面转录', '', 'reported', '课件缩略图宽度'],
    ['C02', 'image', 'canvas_fact', 'image_height_px', 564, 'px', '图面转录', '', 'reported', '课件缩略图高度'],
    ['C03', 'chart', 'structure', 'table_row_count', 18, 'count', '图面计算', '', 'reported', '3 组顶部百分比 + 3 项国家指标 + 9 段年龄组 + 7 项社会指标'],
    ['C04', 'chart', 'structure', 'series_count', 2, 'count', '图面转录', '', 'reported', '1975 蓝 / 2014 红，一左一右'],
    ['C05', 'chart', 'structure', 'concentric_circle_count', 3, 'count', '图面转录', '', 'reported', '中部同心圆三层'],
    ['C06', 'chart', 'structure', 'top_percentage_group_count', 3, 'count', '图面转录', '', 'reported', '每组一图标 + 两值'],
    ['C07', 'portrait', 'canvas_fact', 'portrait_count', 2, 'count', '图面转录', '', 'reported', '左右两位国家元首肖像，构成对比的叙事锚点'],
]
write(os.path.join(d12, '辅助指标.csv'), h12a, rows12a)

# ---------- CASE-0014 ----------
d14 = os.path.join(CASES, '08-图片式-Photo-graphic', '案例', 'CASE-0014-摄影嵌入图表')
h14 = ['metric_id', 'chart_section', 'entity_en', 'indicator_zh', 'value', 'unit', 'period',
       'evidence_level', 'confidence', 'value_status', 'note']
ageing = [
    ('Brazil', '巴西', 9), ('China', '中国', 11), ('Denmark', '丹麦', 22), ('France', '法国', 22),
    ('Germany', '德国', 25), ('India', '印度', 8), ('Ireland', '爱尔兰', 16), ('Italy', '意大利', 26),
    ('Japan', '日本', 28), ('Netherlands', '荷兰', 20), ('Poland', '波兰', 18), ('Russia', '俄罗斯', 17),
    ('Spain', '西班牙', 22), ('Sweden', '瑞典', 24), ('Turkey', '土耳其', 8), ('UK', '英国', 22),
    ('US', '美国', 17),
]
rows14 = []
for i, (en, zh, v) in enumerate(ageing, 1):
    rows14.append([f'A{i:02d}', 'aging', en, '60 岁以上人口占比', v, 'pct',
                   '2007', '图面可辨', 'mid', 'reported',
                   '柱顶数字与柱底国名逐柱对应；缩图下个别对齐待高清核对'])

obesity = [
    ('France', '法国', 10.5), ('Germany', '德国', 13.6), ('Italy', '意大利', 9.9),
    ('Netherlands', '荷兰', 11.2), ('Sweden', '瑞典', 10.2), ('Switzerland', '瑞士', 8.1),
    ('UK', '英国', 24.0), ('US', '美国', 34.3),
]
for i, (en, zh, v) in enumerate(obesity, 1):
    rows14.append([f'B{i:02d}', 'obesity', en, '成人肥胖率', v, 'pct',
                   '', '图面可辨', 'mid', 'reported', '统计年份原图未标，仅标为成年人群体'])

rows14 += [
    ['C01', 'nhs', 'NHS', '员工总数（1998）', 583742, 'person', '1998', '图面可辨', 'mid', 'reported',
     '红圆内 TOTAL 行；与 2008 值构成可复算对'],
    ['C02', 'nhs', 'NHS', '员工总数（2008）', 760886, 'person', '2008', '图面可辨', 'mid', 'reported',
     '同上；两圆之间印有增幅百分比'],
    ['C03', 'nhs', 'NHS', '员工增幅', 30.3, 'pct', '1998–2008', '图面可辨', 'low', 'reported',
     '形似 30.3%，与两总数复算值 30.35% 基本吻合，可反证读数'],
    ['C04', 'nhs', 'NHS', '医生数（1998）', '', 'person', '1998', '缺失', '', 'not_readable',
     '圆内 Doctors 行字高不足 5px，无法确认位数'],
    ['C05', 'nhs', 'NHS', '护理人员数（1998）', '', 'person', '1998', '缺失', '', 'not_readable', '同上'],
    ['C06', 'nhs', 'NHS', '医生数（2008）', '', 'person', '2008', '缺失', '', 'not_readable', '同上'],
    ['C07', 'nhs', 'NHS', '护理人员数（2008）', '', 'person', '2008', '缺失', '', 'not_readable', '同上'],
]
write(os.path.join(d14, '基础数据集.csv'), h14, rows14)

h14a = ['metric_id', 'subject', 'category', 'metric', 'value', 'unit', 'evidence_level', 'confidence', 'value_status', 'note']
rows14a = [
    ['S01', 'image', 'canvas_fact', 'image_width_px', 420, 'px', '图面转录', '', 'reported', '课件缩略图宽度'],
    ['S02', 'image', 'canvas_fact', 'image_height_px', 494, 'px', '图面转录', '', 'reported', '课件缩略图高度'],
    ['S03', 'chart', 'structure', 'chart_section_count', 3, 'count', '图面转录', '', 'reported', '老龄化 / 肥胖率 / NHS 员工增长，三组均为柱或圆'],
    ['S04', 'chart', 'structure', 'aging_bar_count', 17, 'count', '图面计算', '', 'reported', '由 A01–A17 计数'],
    ['S05', 'chart', 'structure', 'obesity_bar_count', 8, 'count', '图面计算', '', 'reported', '由 B01–B08 计数'],
    ['S06', 'chart', 'structure', 'photo_panel_count', 17, 'count', '图面可辨', 'mid', 'reported', '柱体内嵌人像照片，与老龄化柱一一对应'],
    ['S07', 'chart', 'structure', 'chart_type', '', '', '图面转录', '', 'reported', '全部为长度编码的柱形；NHS 段改用圆形面积 + 数字'],
    ['S08', 'aging', 'derived', 'aging_unweighted_mean', 18.5, 'pct', '图面计算', '', 'reported', '17 国取值算术平均；非人口加权，不得当作「全球水平」'],
]
write(os.path.join(d14, '辅助指标.csv'), h14a, rows14a)
