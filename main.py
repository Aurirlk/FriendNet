"""社交网络分析工具箱 - 带持久化存储版本"""

import json
import os
from coverage import as_set, besties_coverage
from prediction import friendly_prediction
from relationships import friend_besties, friend_second_besties

# ---------- 数据管理 ----------
DATA_FILE = "data.json"

class DataManager:
    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        self.data = {"people": {}}
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.save()

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get_all_people(self):
        return list(self.data["people"].keys())

    def add_person(self, name, features=None, friends=None):
        if name in self.data["people"]:
            print(f"人物 {name} 已存在，如需修改请使用修改功能。")
            return False
        self.data["people"][name] = {
            "features": features or {},
            "friends": friends or []
        }
        # 确保好友关系双向
        for friend in self.data["people"][name]["friends"]:
            if friend in self.data["people"] and name not in self.data["people"][friend]["friends"]:
                self.data["people"][friend]["friends"].append(name)
        self.save()
        print(f"人物 {name} 创建成功。")
        return True

    def update_person(self, name, features=None, add_friends=None, remove_friends=None):
        if name not in self.data["people"]:
            print(f"人物 {name} 不存在。")
            return False
        # 更新特征
        if features is not None:
            self.data["people"][name]["features"].update(features)
        # 添加好友（双向）
        if add_friends:
            for f in add_friends:
                if f == name:
                    continue
                if f not in self.data["people"]:
                    print(f"警告：{f} 不存在，无法添加为好友。")
                    continue
                if f not in self.data["people"][name]["friends"]:
                    self.data["people"][name]["friends"].append(f)
                if name not in self.data["people"][f]["friends"]:
                    self.data["people"][f]["friends"].append(name)
        # 删除好友（双向）
        if remove_friends:
            for f in remove_friends:
                if f in self.data["people"][name]["friends"]:
                    self.data["people"][name]["friends"].remove(f)
                if name in self.data["people"].get(f, {}).get("friends", []):
                    self.data["people"][f]["friends"].remove(name)
        self.save()
        print(f"人物 {name} 更新成功。")
        return True

    def delete_person(self, name):
        if name not in self.data["people"]:
            print(f"人物 {name} 不存在。")
            return False
        # 从所有人的好友列表中移除该人
        for other in self.data["people"]:
            if name in self.data["people"][other]["friends"]:
                self.data["people"][other]["friends"].remove(name)
        del self.data["people"][name]
        self.save()
        print(f"人物 {name} 已删除。")
        return True

    def get_friendly_dict(self):
        """构建 {人名: set(好友)} 用于原有函数"""
        fd = {}
        for name, info in self.data["people"].items():
            fd[name] = set(info["friends"])
        return fd

    def get_features_dict(self):
        """构建 {人名: {特征名: 值}} 用于预测"""
        fd = {}
        for name, info in self.data["people"].items():
            fd[name] = info["features"].copy()
        return fd

# ---------- UI 交互辅助 ----------
def input_features_interactive():
    """交互式输入特征，返回字典"""
    print("请输入特征（键=值），每行一个，空行结束：")
    feats = {}
    while True:
        line = input().strip()
        if not line:
            break
        if '=' in line:
            k, v = line.split('=', 1)
            feats[k.strip()] = v.strip()
        else:
            print("格式错误，请使用 键=值 格式")
    return feats

def input_friends_interactive():
    """交互式输入好友列表（人名，可多行），返回列表"""
    print("请输入好友的人名，每行一个，空行结束：")
    friends = []
    while True:
        line = input().strip()
        if not line:
            break
        friends.append(line)
    return friends

def select_person(prompt, dm):
    """从已有人员中选择一个，返回人名（若无则空）"""
    people = dm.get_all_people()
    if not people:
        print("当前没有任何人物，请先创建。")
        return None
    print("现有人员:", ", ".join(people))
    name = input(prompt).strip()
    if name not in people:
        print(f"人物 {name} 不存在。")
        return None
    return name

# ---------- 文件导入函数 ----------
def import_people_from_file(filepath, dm):
    """
    从文件批量导入人物。每行格式：
    姓名: 特征1=值1,特征2=值2; 好友1,好友2
    示例：
    张三: university=南东大学,hobby=reading; 李四,王五
    李四: university=清北大学; 张三
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # 解析姓名和剩余部分
        if ':' not in line:
            print(f"第{line_num}行格式错误（缺少冒号），跳过：{line}")
            continue
        name, rest = line.split(':', 1)
        name = name.strip()
        if not name:
            print(f"第{line_num}行为空姓名，跳过")
            continue

        # 分割特征和好友（用分号分隔）
        features_str = ""
        friends_str = ""
        if ';' in rest:
            parts = rest.split(';', 1)
            features_str = parts[0].strip()
            friends_str = parts[1].strip() if len(parts) > 1 else ""
        else:
            features_str = rest.strip()

        # 解析特征：键=值，用逗号分隔
        features = {}
        if features_str:
            for item in features_str.split(','):
                item = item.strip()
                if '=' in item:
                    k, v = item.split('=', 1)
                    features[k.strip()] = v.strip()
                else:
                    print(f"第{line_num}行特征格式错误（缺少等号），忽略：{item}")

        # 解析好友列表：用逗号分隔
        friends = []
        if friends_str:
            for f in friends_str.split(','):
                f = f.strip()
                if f:
                    friends.append(f)

        # 添加人物（若已存在则跳过并提示）
        if name in dm.get_all_people():
            print(f"人物 {name} 已存在，跳过")
            continue
        dm.add_person(name, features, friends)
        print(f"已添加人物: {name}")

# ---------- 菜单功能 ----------
def menu_create_person(dm):
    print("\n--- 创建人物 (create_person) ---")
    choice = input("选择输入方式：1-手动输入  2-从txt/markdown文件批量读取: ")
    if choice == '1':
        name = input("请输入人物姓名: ").strip()
        if name in dm.get_all_people():
            print("人物已存在，请使用修改功能。")
            return
        print("现在输入该人物的特征（可选）：")
        features = input_features_interactive()
        print("现在输入该人物的好友列表（可选）：")
        friends = input_friends_interactive()
        dm.add_person(name, features, friends)
    elif choice == '2':
        filepath = input("请输入txt或markdown文件路径: ").strip()
        try:
            import_people_from_file(filepath, dm)
        except Exception as e:
            print(f"读取文件失败: {e}")
    else:
        print("无效选择")

def menu_update_person(dm):
    print("\n--- 修改人物 (update_person) ---")
    name = select_person("请输入要修改的人物姓名: ", dm)
    if not name:
        return
    print("当前特征:", dm.data["people"][name]["features"])
    print("当前好友:", dm.data["people"][name]["friends"])
    print("选择要修改的内容：1-添加/修改特征  2-添加好友  3-删除好友")
    choice = input("请选择 (1/2/3): ").strip()
    if choice == '1':
        print("输入要添加或修改的特征（键=值），每行一个，空行结束：")
        new_feats = input_features_interactive()
        dm.update_person(name, features=new_feats)
    elif choice == '2':
        print("输入要添加的好友人名，每行一个，空行结束：")
        add_friends = input_friends_interactive()
        dm.update_person(name, add_friends=add_friends)
    elif choice == '3':
        print("当前好友:", dm.data["people"][name]["friends"])
        print("输入要删除的好友人名，每行一个，空行结束：")
        remove_friends = input_friends_interactive()
        dm.update_person(name, remove_friends=remove_friends)
    else:
        print("无效选择")

def menu_delete_person(dm):
    print("\n--- 删除人物 (delete_person) ---")
    name = select_person("请输入要删除的人物姓名: ", dm)
    if name:
        dm.delete_person(name)

def menu_friend_besties(dm):
    print("\n--- 查找直接好友 (friend_besties) ---")
    name = select_person("请输入人物姓名: ", dm)
    if not name:
        return
    fd = dm.get_friendly_dict()
    result = friend_besties(name, fd)
    print(f"{name} 的直接好友: {result}")

def menu_friend_second_besties(dm):
    print("\n--- 查找二度好友 (friend_second_besties) ---")
    name = select_person("请输入人物姓名: ", dm)
    if not name:
        return
    fd = dm.get_friendly_dict()
    result = friend_second_besties(name, fd)
    print(f"{name} 的二度好友: {result}")

def menu_besties_coverage(dm):
    print("\n--- 计算覆盖率 (besties_coverage) ---")
    persons_str = input("请输入测试集人物（用中文逗号分隔）: ")
    persons = [p.strip() for p in persons_str.split(',') if p.strip()]
    if not persons:
        print("测试集为空")
        return
    fd = dm.get_friendly_dict()
    print("预测函数可选：0-无  1-仅直接好友  2-仅二度好友  3-两者组合")
    func_choice = input("请选择: ")
    funcs = []
    if func_choice in ('1', '3'):
        funcs.append(as_set(friend_besties))
    if func_choice in ('2', '3'):
        # 包装 friend_second_besties 为返回 set
        funcs.append(lambda p: set(friend_second_besties(p, fd)))
    cov = besties_coverage(persons, fd, funcs)
    print(f"覆盖率: {cov}")

def menu_friendly_prediction(dm):
    print("\n--- 预测特征 (friendly_prediction) ---")
    name = select_person("请输入目标人物: ", dm)
    if not name:
        return
    features_str = input("请输入要预测的特征集合（逗号分隔）: ")
    features = {f.strip() for f in features_str.split(',') if f.strip()}
    if not features:
        print("特征集合为空")
        return
    fd = dm.get_friendly_dict()
    feat_dict = dm.get_features_dict()
    result = friendly_prediction(name, features, fd, feat_dict)
    print("预测结果:")
    for k, v in result.items():
        print(f"  {k}: {v}")

# ---------- 主菜单 ----------
def print_menu():
    print("\n" + "=" * 50)
    print(" 社交网络分析工具箱（持久化版本）")
    print("=" * 50)
    print("1. 创建人物字典 (create_person)")
    print("2. 修改人物字典 (update_person)")
    print("3. 删除人物字典 (delete_person)")
    print("4. 查找直接好友 (friend_besties)")
    print("5. 查找二度好友 (friend_second_besties)")
    print("6. 计算覆盖率 (besties_coverage)")
    print("7. 预测特征 (friendly_prediction)")
    print("0. 退出程序")
    print("=" * 50)

def main():
    dm = DataManager()
    while True:
        print_menu()
        choice = input("请输入数字选择: ").strip()
        if choice == '1':
            menu_create_person(dm)
        elif choice == '2':
            menu_update_person(dm)
        elif choice == '3':
            menu_delete_person(dm)
        elif choice == '4':
            menu_friend_besties(dm)
        elif choice == '5':
            menu_friend_second_besties(dm)
        elif choice == '6':
            menu_besties_coverage(dm)
        elif choice == '7':
            menu_friendly_prediction(dm)
        elif choice == '0':
            print("再见！")
            break
        else:
            print("无效输入，请重新选择。")
        input("\n按回车键继续...")

if __name__ == "__main__":
    main()