import json

def save_to_json(dictionary, file_path):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(dictionary, json_file, ensure_ascii=False, indent=2)
    print(f"Dictionary saved to {file_path}")
file_path = r"C:\Users\Administrator.Arknights-WZXKT\Desktop\python\ocr\ques.txt"
json_file_path = r"C:\Users\Administrator.Arknights-WZXKT\Desktop\python\ocr\ques.json"
# 打开文件并读取每一行
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 移除每行末尾的换行符，并创建数组
array_of_lines = [line.strip() for line in lines]
save_to_json(array_of_lines, json_file_path)
# 输出数组
print(array_of_lines)
