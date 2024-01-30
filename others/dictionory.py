import json

def save_to_json(dictionary, file_path):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(dictionary, json_file, ensure_ascii=False, indent=2)
    print(f"Dictionary saved to {file_path}")


json_file_path = r"C:\Users\Administrator.Arknights-WZXKT\Desktop\python\ocr\words.json"

# 输入的英文单词和对应翻译
word_translations = """
solid
n. 固体 …
ethnic
adj. 种族的; 民族的
immigrant
n. 移民
vast
adj. 广大的; 巨大的
well-being 
n. 健康，幸福
unprocessed 
adj. 未加工的
preservative 
n. 防腐剂
vegetarian 
n. 素食者
burger
n. （非正式用语） 汉堡包
pizza 
n. 比萨饼
rush
v. 匆忙地做</br>n. 冲进; 忙乱
california 
（美国） 加利福尼亚州
custom
n. 风俗，传统
lemon
n. 柠檬
roast
adj. 烤制的</br>v. 烤
steak
n.（供煎，烤等的）厚片的肉（尤指牛肉）
accidentally 
adv. 偶然地，意外地
preservation 
n. 保护，储藏
peel
v. 剥…的皮; 削.…的皮
stir
v. n. 搅拌，搅动
pasta 
n. 意大利面食 （包括通心粉及面条等）
flavourful 
adj. 美味的，可口的
sauce
n. 酱汁，调味汗
flavour
n. 风味，滋味
appetizer
n. （正餐前的）开胃菜
tortilla 
n.（尤指墨西哥人食用的）玉米薄饼
mold
v. 模制，铸造</br>n. 模子，铸型
fry
v. 油炸，油煎
spice
n. 香料，调味品
curry
n. 咖喱
horizon 
n. （知识，思想等的） 范围，视野；地平线
"""

# 处理输入并生成字典
def create_dictionary(word_translations):
    lines = word_translations.strip().split('\n')
    word_dict = {}

    for i in range(0, len(lines), 2):
        word = lines[i].strip()
        translation = lines[i + 1].strip()
        word_dict[word] = translation

    return word_dict

# 创建字典
words_and_translations_dict = create_dictionary(word_translations)
save_to_json(words_and_translations_dict, json_file_path)
# 输出字典
print("Dictionary:")
for word, translation in words_and_translations_dict.items():
    print(f"{word}: {translation}")