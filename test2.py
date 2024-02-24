import json

# 读取文件内容
file_path = r"E:\spider_img\Sessions.dat"

with open(file_path, "r", encoding="utf-16-le") as file:
    lines = file.readlines()

# 去除空行和空格
last_line = None
for line in reversed(lines):
    line = line.strip()
    if line:
        last_line = line
        break

# 输出最后一行数据
if last_line:
    print("Last Line:", last_line)
    
    # 尝试解析 JSON 数据
    try:
        # 移除 UTF-8 BOM（字节顺序标记）
        last_line = last_line.encode('utf-8').decode('utf-8-sig')

        data = json.loads(last_line)
        # 提取答案
        answers = []
        for item in data["response_data"][0]["body"]["opponent"]["score"]["detail"]:
            # 将答案转换为数字
            answer = item["answer"]
            if answer == "A":
                answers.append(1)
            elif answer == "B":
                answers.append(2)
            elif answer == "C":
                answers.append(3)
            elif answer == "D":
                answers.append(4)

        # 输出数字数组答案
        print("答案数组为:", answers)
    except json.JSONDecodeError as e:
        print("JSON 解码错误:", e)
else:
    print("文件没有有效数据行。")
