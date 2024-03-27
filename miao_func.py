import re
import os
import random
animals = ["狗", "猪", "鸟", "马", "鱼", "兔", "猴",
           "牛", "羊", "鸡", "鹿", "蛇", "僧", "鬼", 
           "鹤", "犬", "鲤"]

def _remove_brackets(text):
    return re.sub(r'<.*?>', '', text)

def _replace_ye_with_miao(text):
    return text.replace("也", "喵")


def _replace_animals_with_cat(text):
    animal_pattern = "|".join(animals) 
    # 使用re.sub来替换所有匹配的动物名称为“猫”
    text = re.sub(animal_pattern, "猫", text)
    return text


def _should_miao_text(text, min_limit=0):
    # 检查文本长度是否超过140字符
    if len(text) >= 140:
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
    text = _remove_brackets(text)
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


def traverse_directory(base_dir):
    txt_paths = []
    
    # Collect all .txt file paths
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.txt'):
                txt_paths.append(os.path.join(root, file))
                
    # Shuffle the list to ensure random order
    random.shuffle(txt_paths)
    
    def process_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            paragraphs = content.split('\n')
            for paragraph in paragraphs:
                replaced_text, replaced_num = miao_main(paragraph)
                if replaced_num > 0:
                    # If condition is met, return the modified text and count
                    return replaced_text, replaced_num
        return False, False
    
    # Process each file in the shuffled list
    for file_path in txt_paths:
        replaced_text, replaced_num = process_file(file_path)
        if replaced_text:
            # If the condition is met in any file, return the information
            return file_path, replaced_text, replaced_num


if __name__ == "__main__":
    pass
