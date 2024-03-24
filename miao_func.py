import re
animals = ["狗", "猪", "鸟", "马", "鱼", "兔", "猴", "牛", "羊", "鸡", "鹿", "蛇", "僧"]

def _replace_ye_with_miao(text):
    return text.replace("也", "喵")


def _replace_animals_with_cat(text):
    animal_pattern = "|".join(animals) 
    # 使用re.sub来替换所有匹配的动物名称为“猫”
    text = re.sub(animal_pattern, "猫", text)
    return text


def _should_miao_text(text, min_limit=0):
    # 检查文本长度是否超过140字符
    if len(text) <= 140:
        return 0

    # 统计“也”和动物的出现次数
    ye_count = text.count("也")
    animal_pattern = "|".join(animals)
    animal_counts = len(re.findall(animal_pattern, text))
    total_replacements = ye_count + animal_counts

    # 判断是否满足最小替换次数限制
    if total_replacements<min_limit:
        return 0
    else:
        return total_replacements


def _miao_text(text):
    text = _replace_ye_with_miao(text)
    text = _replace_animals_with_cat(text)
    return text


# 喵func
def miao_main(text, min_limit=3):
    replaced_num = _should_miao_text(text, min_limit)
    if replaced_num > 0:
        replaced_text = _miao_text(text)
        return replaced_text, replaced_num
    else:
        return "", 0


if __name__ == "__main__":
    text = ('环滁皆山也。其西南诸峰，林壑尤美，望之蔚然而深秀者，琅琊也。山行六七里，渐闻水声潺潺，'
            '而泻出于两峰之间者，酿泉也。峰回路转，有亭翼然临于泉上者，醉翁亭也。作亭者谁？山之僧智仙也。'
            '名之者谁？太守自谓也。太守与客来饮于此，饮少辄醉，而年又最高，故自号曰醉翁也。醉翁之意不在酒，'
            '在乎山水之间也。山水之乐，得之心而寓之酒也。')
    # text = ('环滁皆山也。其西南诸峰，林壑尤美，望之蔚然而深秀者，琅琊也。山行六七里，渐闻水声潺潺，')
    new_text, replaced_num = miao_main(text)
    print(f'New text: {new_text}\nReplaced_num: {replaced_num}')
