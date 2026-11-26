# scripts/archive · 一次性迁移脚本存档

> 这些脚本用于 2026-11-24 的结构迁移与批量补表、以及 2026-11-26 的 05 层分区重排，**已经跑完，不再运行**。
> 常驻脚本只有上级目录的 [validate_repo.py](../validate_repo.py)，GitHub Actions 每次 push / PR 只调它。

| 脚本 | 当时的作用 |
|---|---|
| `migrate_to_type_folders.py` | 扁平类型文档 → 类型文件夹 + 一案例一目录；按新旧映射重算全库相对链接 |
| `make_case_tables.py` | 为 CASE-0003／0007 试点生成 CSV 与数据字典 |
| `fill_case_datasets.py` | 其余 13 案补数据字典、CASE-0012／0014 升 `partial` |
| `refresh_case_cards.py` | 刷新各案例 `README.md` 的一屏卡片 |
| `update_case_index.py` | 刷新 `案例索引.md` 的「数据表」「计数结构」两列 |
| `fix_dict_links.py` | 按路径尾部唯一匹配，修正新字典跨目录的层级写错的链接 |
| `add_counting_sections.py` | 为各案例 `分析.md` 的 B 节补「计数结构」段 |
| `partition_gestalt.py` | 2026-11-26：05 层五分区重构后，重算 14 份规则文档、层根三份文档与跨层字典共 19 份链接 |

## 不可直接重跑

脚本里的 `ROOT = Path(__file__).resolve().parent.parent` 假定自身位于 `scripts/` **一级**；归档到 `scripts/archive/` 后，`ROOT` 会指向 `scripts/` 而不是仓库根，直接执行会读写错位置。

**例外**：`partition_gestalt.py` 用的是 `parents[2]`，在本目录位置下路径是对的；但它仍是**一次性**脚本——重复运行会把 `](../` 继续叠成 `](../../`，同样不可重跑。

如确需复用其中某段逻辑：先把该脚本移回 `scripts/`，或把 `ROOT` 改为 `Path(__file__).resolve().parents[2]`，并在临时副本上验证，不要对现有内容直接跑。

## 保留理由

它们是「结构怎么变成现在这样」的可追溯依据（尤其 `migrate_to_type_folders.py` 的新旧路径映射表），删掉之后将来做同类迁移得重新推一遍。放在 `archive/` 既保住历史，又不污染 `scripts/` 的常规入口。
