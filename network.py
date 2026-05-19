"""从边列表构建无向好友图。"""


def get_friendly_dict(friend_list):
    """
    将互为好友的配对列表转换为邻接字典。

    每个键代表一个人；每个值是他们直接好友的集合。
    """
    graph = {}
    for a, b in friend_list:
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set()).add(a)
    return graph