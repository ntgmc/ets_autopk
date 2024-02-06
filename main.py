from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import *
import pytesseract
from PIL import Image
import json
import time
from fuzzywuzzy import process
import threading
import os
import win32api, win32gui, win32con
import sys
mumu_hwnd, mumu_child_hwnd = 0,0
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

def enumerate_child_windows(parent_hwnd):
    def callback(hwnd, windows):
        windows.append(hwnd)
        return True
    child_windows = []
    win32gui.EnumChildWindows(parent_hwnd, callback, child_windows)
    return child_windows
def get_all_windows():
    global mumu_hwnd, mumu_child_hwnd
    # 获取窗口句柄
    mumu_hwnd = win32gui.FindWindow("Qt5156QWindowIcon", "Z")
    mumu_child_hwnd = enumerate_child_windows(mumu_hwnd)[0]
    print(mumu_child_hwnd)
def split_qimage(qimage, x, y, width, height):
    # 创建一个子图像
    sub_image = qimage.copy(int(x), int(y), int(width), int(height))
    return sub_image
def capture_screenshot():
    window_rect = win32gui.GetWindowRect(mumu_child_hwnd)
    global scale_width, scale_height
    scale_width, scale_height = (window_rect[2] - window_rect[0]) / 524, (window_rect[3] - window_rect[1])/ 932
    q_x, q_y, q_width, q_height = 60 * scale_width, 300 * scale_height, 370 * scale_width, 80 * scale_height # 相对坐标
    a_x, a_width, a_height = 40 * scale_width, 453 * scale_width, 74 # 相对坐标
    a1_y, a2_y, a3_y, a4_y = 440 * scale_height, 535 * scale_height, 627 * scale_height, 727 * scale_height # 相对坐标
    regions = [(q_x, q_y, q_width, q_height), (a_x, a1_y, a_width, a_height), (a_x, a2_y, a_width, a_height), (a_x, a3_y, a_width, a_height), (a_x, a4_y, a_width, a_height)]

    save_path = []
    app = QApplication(sys.argv)
    # 截取窗口的屏幕截图
    screen = QApplication.primaryScreen()
    screenshot = screen.grabWindow(mumu_child_hwnd).toImage()
    for i, region in enumerate(regions):
        x, y, w, h = region
        # 分割图像
        cropped_img = split_qimage(screenshot, x, y, w, h)
        now_save_path = os.path.join(USER_PATH, "png", f"region_{i}.png")
        # 保存截图到指定目录
        cropped_img.save(now_save_path)
        save_path.append(now_save_path)
    screenshot.save(os.path.join(USER_PATH, "png", f"screenshot.png"))
    return save_path



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
    return autoreplace(text)

def ocr_thread(image_path, custom_dict_path, result_dict, i):
    text = ocr_with_custom_dict(image_path, custom_dict_path)
    if i == 4 and text == "":
        text = "n. 防腐剂"
    result_dict.update({i: text})

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
    get_all_windows()
    # 截图窗口
    while True:
        screenshot_path_list = capture_screenshot()
        result_text = []
        ques = ""
        ans = ""
        i = 0

        # 使用字典存储线程结果
        result_dict = {}

        threads = []

        for screenshot_path in screenshot_path_list:
            if screenshot_path:
                # 创建线程
                if i == 0:
                    thread = threading.Thread(target=ocr_thread, args=(screenshot_path, ques_path, result_dict, i))
                else:
                    thread = threading.Thread(target=ocr_thread, args=(screenshot_path, ans_path, result_dict, i))
                threads.append(thread)
                i += 1

        # 启动所有线程
        for thread in threads:
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 从队列中获取结果
        if result_dict:
            result_text = [result_dict[key] for key in sorted(result_dict.keys())]

        # 输出识别结果
        print(result_text)
        if result_text[1] == "恭喜你!":
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(int(260 * scale_width), int(610 * scale_height)))
            win32api.PostMessage(mumu_child_hwnd,win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(int(260 * scale_width), int(610 * scale_height)))
            time.sleep(0.5)
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(int(400 * scale_width), int(840 * scale_height)))
            win32api.PostMessage(mumu_child_hwnd,win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(int(400 * scale_width), int(840 * scale_height)))
            time.sleep(4.8)
        elif result_text[1] == "PK结果提交失败":
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(int(260 * scale_width), int(540 * scale_height)))
            win32api.PostMessage(mumu_child_hwnd,win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(int(260 * scale_width), int(540 * scale_height)))
            time.sleep(0.5)
        elif result_text[3].find("世界各地的饮食") != -1: # 找到字符
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(int(260 * scale_width), int(840 * scale_height)))
            win32api.PostMessage(mumu_child_hwnd,win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(int(260 * scale_width), int(840 * scale_height)))
            time.sleep(4.8)
        else:
            new_list = result_text[1:]
            ques = process.extractOne(result_text[0].lower(), ques_list)
            ques_str = ques[0]
            ans = words.get(ques_str)
            print(f"Ques:{ques_str}. Ans:{ans}")
            ex_ans = process.extractOne(ans, new_list)
            ex_ans_str = ex_ans[0]
            locate = new_list.index(ex_ans_str) # 答案位置
            print("Chooce：", ex_ans_str, locate)
            if ex_ans_str != ans: # 非精确匹配时才输出log           
                with open(log_file_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(str(result_text) + '\n')
            targety = [520, 612, 704, 796] # 答案相对y坐标
            target_y = int((targety[locate] - 40) * scale_height)
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(int(260 * scale_width), target_y))
            win32api.PostMessage(mumu_child_hwnd,win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(int(260 * scale_width), target_y))
            time.sleep(1.1)