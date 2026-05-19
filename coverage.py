"""计算种子在一个群体中的覆盖率。"""

from __future__ import annotations


def besties_coverage(
    individuals: list[str],
    bestie_dict: dict[str, set[str]],
    relationship_list: list,
) -> float:
    """
    被覆盖的唯一人数与总人口（bestie_dict 中的键）的比例。

    被覆盖的人数 = 种子节点 加上 将 relationship_list 中的每个关系函数
    应用于每个种子后返回的所有节点（函数接收 person 和 bestie_dict 作为参数）。
    """
    population = len(bestie_dict)
    if population == 0:
        return 0.0

    covered: set[str] = set(individuals)
    for person in individuals:
        for rel_fn in relationship_list:
            found = rel_fn(person, bestie_dict)
            if isinstance(found, set):
                covered.update(found)
            else:
                covered.update(found)

    return len(covered) / population


def as_set(rel_fn):
    """包装一个返回列表的关系函数，以便覆盖率计算可以获得一个集合视图。"""

    def wrapped(person, bestie_dict):
        return set(rel_fn(person, bestie_dict))

    return wrapped