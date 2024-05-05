from PyQt5.QtWidgets import QApplication
import pytesseract
from PIL import Image
import json
import time
from fuzzywuzzy import process
import threading
import os
import win32api, win32gui, win32con
import sys
import re
import cv2

mumu_hwnd, mumu_child_hwnd = 0, 0
USER_PATH = os.path.dirname(os.path.abspath(__file__))
ques_path = os.path.join(USER_PATH, "ocr_custom", "ques.txt")
ans_path = os.path.join(USER_PATH, "ocr_custom", "anss.txt")
json_words_path = os.path.join(USER_PATH, "json", "words.json")
json_ques_path = os.path.join(USER_PATH, "json", "ques.json")
json_ans_path = os.path.join(USER_PATH, "json", "ans.json")
json_replace_path = os.path.join(USER_PATH, "json", "replace.json")
log_file_path = os.path.join(USER_PATH, "log", "ocr.log")
folder_list = ["log", "png"]
scale_width, scale_height = 0, 0


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


def split_image_with_cv2(image, x, y, width, height):
    # Convert the arguments to integers
    x = int(x)
    y = int(y)
    width = int(width)
    height = int(height)
    # Slice the image
    sub_image = image[y:y+height, x:x+width]
    return sub_image


def get_pixel_color(image_path, x, y):
    # 打开截图
    image = Image.open(image_path)
    # 获取像素颜色
    pixel_color = image.getpixel((x, y))
    return pixel_color


def capture_screenshot():
    window_rect = win32gui.GetWindowRect(mumu_child_hwnd)
    global scale_width, scale_height
    scale_width, scale_height = (window_rect[2] - window_rect[0]) / 552, (window_rect[3] - window_rect[1]) / 979
    q_x, q_y, q_weight, q_height = 165 * scale_width, 295 * scale_height, 215 * scale_width, 45 * scale_height  # 相对坐标
    a_x, a_weight, a_height = 92 * scale_width, 385 * scale_width, 50 * scale_width # 相对坐标
    a1_y, a2_y, a3_y, a4_y = 458 * scale_height, 540 * scale_height, 622 * scale_height, 702 * scale_height  # 相对坐标
    regions = [(q_x, q_y, q_weight, q_height), (a_x, a1_y, a_weight, a_height), (a_x, a2_y, a_weight, a_height),
               (a_x, a3_y, a_weight, a_height), (a_x, a4_y, a_weight, a_height)]
    save_path = []
    app = QApplication(sys.argv)
    # 截取窗口的屏幕截图
    image_path = os.path.join(USER_PATH, "png", "screenshot.png")
    screen = QApplication.primaryScreen()
    screenshot = screen.grabWindow(mumu_child_hwnd).toImage()
    screenshot.save(image_path)
    while get_pixel_color(image_path, 316 * scale_height, 346 * scale_height) == (160, 219, 115):
        time.sleep(0.2)
        screenshot = screen.grabWindow(mumu_child_hwnd).toImage()
        screenshot.save(image_path)
    image = cv2.imread(image_path)
    # 转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    for i, region in enumerate(regions):
        x, y, w, h = region
        # 分割图像
        cropped_img = split_image_with_cv2(gray, x, y, w, h)
        now_save_path = os.path.join(USER_PATH, "png", f"region_{i}.png")
        # 保存截图到指定目录
        cv2.imwrite(now_save_path, cropped_img)
        save_path.append(now_save_path)
    return save_path


def ocr_image_chi(image_path):
    # 使用Tesseract进行OCR识别
    image = cv2.imread(image_path)

    text = pytesseract.image_to_string(image, lang='chi_sim')
    if text.replace("\n", "").replace(" ", "") == "":
        text = pytesseract.image_to_string(image, lang='chi_sim')  # 多给一次机会
    return text.replace("\n", "")


def ocr_image_eng(image_path):
    # 使用Tesseract进行OCR识别
    image = cv2.imread(image_path)

    text = pytesseract.image_to_string(image, lang='eng')

    return text.replace("\n", "")


def ocr_with_custom_dict(image_path, custom_dict_path):
    # 读取自定义词库
    with open(custom_dict_path, 'r', encoding='utf-8') as f:
        custom_words = [line.strip() for line in f.readlines()]
    image = cv2.imread(image_path)

    # 运行 OCR
    custom_config = f'--user-words {",".join(custom_words)}'
    text = pytesseract.image_to_string(image, config=custom_config, lang='chi_sim')
    if text.replace("\n", "").replace(" ", "") == "":
        text = pytesseract.image_to_string(image, config=custom_config, lang='chi_sim')
    return auto_replace(text)


def ocr_thread(image_path, custom_dict_path, result_dict, i):
    text = ocr_with_custom_dict(image_path, custom_dict_path)
    result_dict.update({i: text})


replace_list = load_from_json(json_replace_path)


def auto_replace(text):
    text = text.replace("\n", "").replace(" ", "")
    if text == "":
        return "Finalchoice"
    for rule in replace_list:
        if re.search(rule['pattern'], text):
            text = rule['replacement']
            return text
    return text


def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def similarity_score(s1, s2):
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0
    distance = levenshtein_distance(s1, s2)
    return 1.0 - (distance / max_len)


if __name__ == "__main__":
    words = load_from_json(json_words_path)
    ques_list = load_from_json(json_ques_path)
    ans_list = load_from_json(json_ans_path)
    for folder in folder_list:
        create_folder_if_not_exists(os.path.join(USER_PATH, folder))
    get_all_windows()  # 获取窗口句柄
    while True:
        screenshot_path_list = capture_screenshot()  # 截图窗口
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
        # 从字典中获取结果
        if result_dict:
            result_text = [result_dict[key] for key in sorted(result_dict.keys())]
        # 输出识别结果
        print(f"[{time.time()}]{result_text}")
        if get_pixel_color(os.path.join(USER_PATH, "png", "screenshot.png"), 276 * scale_width, 622 * scale_width) == (54, 143, 255):
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON,
                                 win32api.MAKELONG(int(276 * scale_width), int(622 * scale_height)))
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONUP, 0,
                                 win32api.MAKELONG(int(276 * scale_width), int(622 * scale_height)))
            time.sleep(0.5)
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON,
                                 win32api.MAKELONG(int(350 * scale_width), int(900 * scale_height)))
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONUP, 0,
                                 win32api.MAKELONG(int(350 * scale_width), int(900 * scale_height)))
            time.sleep(4.8)
        elif result_text[1] == "PK结果提交失败":
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON,
                                 win32api.MAKELONG(int(260 * scale_width), int(540 * scale_height)))
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONUP, 0,
                                 win32api.MAKELONG(int(260 * scale_width), int(540 * scale_height)))
            time.sleep(0.5)
        elif get_pixel_color(os.path.join(USER_PATH, "png", "screenshot.png"), 350 * scale_width, 900 * scale_width) == (54, 143, 255):  # 蓝色
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON,
                                 win32api.MAKELONG(int(350 * scale_width), int(900 * scale_height)))
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONUP, 0,
                                 win32api.MAKELONG(int(350 * scale_width), int(900 * scale_height)))
            time.sleep(4.8)
        else:
            new_list = result_text[1:]
            ques = process.extractOne(result_text[0].lower(), ques_list)
            ques_str = ques[0]
            ans = words.get(ques_str)
            print(f"Ques:{ques_str}. Ans:{ans}")
            ex_ans = process.extractOne(ans, new_list)
            score = similarity_score(ex_ans[0], ans)
            if score < 0.8 and "Finalchoice" in new_list:  # 匹配分数低于0.8且存在Finalchoice就选择Finalchoice
                ex_ans_str = "Finalchoice"
            else:
                ex_ans_str = ex_ans[0]
            locate = new_list.index(ex_ans_str)  # 答案位置
            print("Chooce：", ex_ans_str, score, locate + 1)
            if ex_ans_str != ans:  # 非精确匹配时才输出log
                with open(log_file_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(f"[{time.time()}]{str(result_text)}\n")
            targety = [520, 612, 704, 796]  # 答案相对y坐标
            target_y = int((targety[locate] - 40) * scale_height)
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON,
                                 win32api.MAKELONG(int(260 * scale_width), target_y))
            win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON,
                                 win32api.MAKELONG(int(260 * scale_width), target_y))
            time.sleep(1.1)
