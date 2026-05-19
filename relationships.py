"""在 bestie_dict 图上进行一度和二度好友查询。"""

from __future__ import annotations


def _direct_friends(individual: str, bestie_dict: dict[str, set[str]]) -> set[str]:
    """直接邻居：正向邻接加上反向链接（用于处理不完整的图）。"""
    friends = set(bestie_dict.get(individual, set()))
    for person, besties in bestie_dict.items():
        if individual in besties:
            friends.add(person)
    return friends


def friend_besties(individual: str, bestie_dict: dict[str, set[str]]) -> list[str]:
    """一度好友的排序列表；如果该人不在字典的键中或没有好友则返回 []。"""
    if individual not in bestie_dict:
        return []
    return sorted(bestie_dict[individual])


def friend_second_besties(individual: str, bestie_dict: dict[str, set[str]]) -> list[str]:
    """
    二度好友（朋友的朋友）的排序名称列表：排除自己和直接好友。
    使用正向/反向邻接的并集，因此作为键缺失的节点仍然有效。
    """
    direct = _direct_friends(individual, bestie_dict)
    second: set[str] = set()
    for f in direct:
        second |= _direct_friends(f, bestie_dict)
    second.discard(individual)
    second -= direct
    return sorted(second)