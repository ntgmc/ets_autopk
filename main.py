import pygetwindow as gw
import pyautogui
import pytesseract
from PIL import Image
import json
import time
from fuzzywuzzy import process
import threading
from queue import Queue
import os
mumu_x, mumu_y, mumu_width, mumu_height = 0,0,0,0
USER_PATH = os.path.dirname(os.path.abspath(__file__))
ques_path = os.path.join(USER_PATH, "ocr_custom", "ques.txt")
ans_path = os.path.join(USER_PATH, "ocr_custom", "anss.txt")
json_words_path = os.path.join(USER_PATH, "json", "words.json")
json_ques_path = os.path.join(USER_PATH, "json", "ques.json")
json_ans_path = os.path.join(USER_PATH, "json", "ans.json")
json_replace_path = os.path.join(USER_PATH, "json", "replace.json")
log_file_path = os.path.join(USER_PATH, "log", "ocr.log")
folder_list = ["log", "png"]
scale_width, scale_height = 0,0
def load_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data

# 设置 Tesseract OCR 引擎路径（根据你的安装路径进行修改）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def capture_screenshot():
    global mumu_x, mumu_y, mumu_width, mumu_height
    # 获取窗口对象
    mumu_window = gw.getWindowsWithTitle("Z") # 在这里填写模拟器标题
    save_path = []
    if mumu_window:
        mumu_window = mumu_window[0]  # 如果有多个相同标题的窗口，选择第一个
        mumu_x, mumu_y, mumu_width, mumu_height = mumu_window.left, mumu_window.top, mumu_window.width, mumu_window.height
        global scale_width, scale_height
        scale_width, scale_height = mumu_window.width / 532, mumu_window.height / 972
        q_x, q_y, q_width, q_height = 60 * scale_width, 339 * scale_height, 370 * scale_width, 80 * scale_height # 相对坐标
        a_x, a_width, a_height = 40 * scale_width, 453 * scale_width, 74 # 相对坐标
        a1_y, a2_y, a3_y, a4_y = 480 * scale_height, 575 * scale_height, 667 * scale_height, 757 * scale_height # 相对坐标
        regions = [(q_x, q_y, q_width, q_height), (a_x, a1_y, a_width, a_height), (a_x, a2_y, a_width, a_height), (a_x, a3_y, a_width, a_height), (a_x, a4_y, a_width, a_height)]
        # 截取窗口的屏幕截图
        screenshot = pyautogui.screenshot(region=(mumu_x, mumu_y, mumu_width, mumu_height))
        nowtime = time.time()
        for i, region in enumerate(regions):
            x, y, w, h = region

            # 分割图像
            cropped_img = screenshot.crop((x, y, x+w, y+h))
            now_save_path = os.path.join(USER_PATH, "png", f"region_{i}.png")
            # 保存截图到指定目录
            screenshot.save(os.path.join(USER_PATH, "png", f"screenshot.png"))
            cropped_img.save(now_save_path)
            save_path.append(now_save_path)

        return save_path
    else:
        print("Window with title not found.")
        return None

def ocr_image_chi(image_path):
    # 使用Tesseract进行OCR识别
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='chi_sim')
    if text == "":
        text = pytesseract.image_to_string(image, lang='chi_sim') # 多给一次机会
    return text.replace("\n", "")

def ocr_image_eng(image_path):
    # 使用Tesseract进行OCR识别
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='eng')
    
    return text.replace("\n", "")

def ocr_with_custom_dict(image_path, custom_dict_path):
    # 读取自定义词库
    with open(custom_dict_path, 'r', encoding='utf-8') as f:
        custom_words = [line.strip() for line in f.readlines()]

    # 运行 OCR
    custom_config = f'--user-words {",".join(custom_words)}'
    text = pytesseract.image_to_string(Image.open(image_path), config=custom_config, lang='chi_sim')
    if text == "":
        text = pytesseract.image_to_string(Image.open(image_path), config=custom_config, lang='chi_sim')
    return autoreplace(text.replace("\n", ""))

def ocr_thread(image_path, custom_dict_path, result_queue, i):
    text = ocr_with_custom_dict(image_path, custom_dict_path)
    result_queue.update({i: text})

replace_list = load_from_json(json_replace_path)
def autoreplace(text):
    for key, value in replace_list.items():
        text = text.replace(key, value)
    return text

if __name__ == "__main__":
    words = load_from_json(json_words_path)
    ques_list = load_from_json(json_ques_path)
    ans_list = load_from_json(json_ans_path)
    for folder in folder_list:
        create_folder_if_not_exists(os.path.join(USER_PATH, folder))
    # 截图窗口
    while True:
        screenshot_path_list = capture_screenshot()
        result_text = []
        ques = ""
        ans = ""
        i = 0

        # 使用字典存储线程结果
        result_queue = {}

        threads = []

        for screenshot_path in screenshot_path_list:
            if screenshot_path:
                # 创建线程
                if i == 0:
                    thread = threading.Thread(target=ocr_thread, args=(screenshot_path, ques_path, result_queue, i))
                else:
                    thread = threading.Thread(target=ocr_thread, args=(screenshot_path, ans_path, result_queue, i))
                threads.append(thread)
                i += 1

        # 启动所有线程
        for thread in threads:
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 从队列中获取结果
        if result_queue:
            result_text = [result_queue[key] for key in sorted(result_queue.keys())]

        # 输出识别结果
        print(result_text)
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(str(result_text) + '\n')
        if result_text[1] != "恭喜你!":
            new_list = result_text[1:]
            ques = process.extractOne(result_text[0].lower(), ques_list)
            ques_str = ques[0]
            ans = words.get(ques_str)
            print(f"Ques:{ques_str}. Ans:{ans}")
            ex_ans = process.extractOne(ans, new_list)
            ex_ans_str = ex_ans[0]
            locate = new_list.index(ex_ans_str) # 答案位置
            print(ex_ans_str, locate)
            targety = [520, 612, 704, 796] # 答案相对坐标
            target_y = targety[locate] * scale_height
            pyautogui.click(mumu_x + 260 * scale_width, mumu_y + target_y)
            time.sleep(0.9)
        else:
            pyautogui.click(mumu_x + 260 * scale_width, mumu_y + 650 * scale_height)
            time.sleep(0.9)
            pyautogui.click(mumu_x + 400 * scale_width, mumu_y + 880 * scale_height)
            time.sleep(5)