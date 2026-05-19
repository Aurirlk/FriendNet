# FriendNet — 社交网络分析工具箱

> 基于 Python 的社交网络分析工具，支持好友关系管理、图论好友推荐、同质性特征预测和网络覆盖率评估。
> A Python-based social network analysis toolbox for friend relationship management, graph-based friend recommendation, homophily-driven feature prediction, and network coverage evaluation.

---

## 功能 Feature

- **人物管理 Person Management** — 创建、修改、删除人物及其属性和好友关系（自动维护双向关系）。
- **好友查询 Friend Lookup** — 查找直接好友（一度）和二度好友（朋友的朋友）。
- **特征预测 Feature Prediction** — 基于好友网络中多数人的特征值，为目标人物预测缺失的特征（同质性原理）。
- **覆盖率计算 Coverage Calculation** — 评估某一类关系函数（直接好友 / 二度好友 / 组合）对目标群体的覆盖范围。

---

## 项目结构 Project Structure

| 文件 File | 说明 Description |
|---|---|
| `main.py` | 程序入口，提供控制台菜单、JSON 数据持久化、文件批量导入 |
| `network.py` | 从边列表构建无向好友图 (`get_friendly_dict`) |
| `relationships.py` | 查询一度好友和二度好友（含双向邻居查找） |
| `prediction.py` | 基于多数投票的特征预测算法（一度 → 二度回退） |
| `coverage.py` | 计算种子节点对总人口的覆盖率 |
| `data.json` | 自动生成的持久化文件，存储所有人物、特征、好友关系 |

---

## 快速开始 Quick Start

```bash
python main.py
```

### 主菜单 Main Menu

```
==================================================
 社交网络分析工具箱（持久化版本）
==================================================
1. 创建人物字典 (create_person)
2. 修改人物字典 (update_person)
3. 删除人物字典 (delete_person)
4. 查找直接好友 (friend_besties)
5. 查找二度好友 (friend_second_besties)
6. 计算覆盖率 (besties_coverage)
7. 预测特征 (friendly_prediction)
0. 退出程序
==================================================
```

### 批量导入格式 Batch Import Format

创建 `.txt` 文件，每行格式：

```
人名: 特征1=值1,特征2=值2; 好友1,好友2
```

示例：

```
张三: university=南东大学,hobby=阅读; 李四,王五
李四: university=清北大学; 张三
```

- 分号前为特征，分号后为好友（均可省略）
- `#` 开头的行为注释

---

## 环境要求 Requirements

- Python 3.8+
- 无需安装第三方库（仅使用标准库：`json`, `os`, `collections`）

---

## 许可证 License

MIT
