import re

def replace_ye_with_miao(text):
    return text.replace("也", "喵")

def replace_animals_with_cat(text):
    # 简化的动物列表
    animals = ["狗", "猪", "鸟", "马", "鱼", "兔", "猴", "牛", "羊", "鸡", "鹿", "蛇", "僧"]
    animal_pattern = "|".join(animals)  # 创建正则表达式
    # 使用re.sub来替换所有匹配的动物名称为“猫”
    text = re.sub(animal_pattern, "猫", text)
    return text

# 喵func
def miao_text(text):
    text = replace_ye_with_miao(text)
    text = replace_animals_with_cat(text)
    return text

# 由于在PCI中不能执行示例调用，这里注释掉了函数调用的例子
# 示例文本: "这里有猪、马和狗，它们也在一起玩耍。"

if __name__ == "__main__":
    text = ('环滁皆山也。其西南诸峰，林壑尤美，望之蔚然而深秀者，琅琊也。山行六七里，渐闻水声潺潺，'
            '而泻出于两峰之间者，酿泉也。峰回路转，有亭翼然临于泉上者，醉翁亭也。作亭者谁？山之僧智仙也。'
            '名之者谁？太守自谓也。太守与客来饮于此，饮少辄醉，而年又最高，故自号曰醉翁也。醉翁之意不在酒，'
            '在乎山水之间也。山水之乐，得之心而寓之酒也。')
    print(miao_text(text))
