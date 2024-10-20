import difflib
import gc
import json
import os
import random
import re
import sys
import time

import cv2
import numpy as np
import win32api
import win32con
import win32gui
from PyQt5.QtWidgets import QApplication
from paddleocr import PaddleOCR

scale_width, scale_height = 0, 0
target_y_list = [490, 575, 657, 745]  # 答案相对y坐标
ocr_time = 0.00


def normalize_text(text):
    # Remove spaces and punctuation
    return re.sub(r'\W+', '', text).lower()


def enumerate_child_windows(parent_hwnd):
    def callback(hwnd, windows):
        windows.append(hwnd)
        return True

    child_windows = []
    win32gui.EnumChildWindows(parent_hwnd, callback, child_windows)
    return child_windows


def get_all_windows():
    # 获取窗口句柄
    _mumu_hwnd = win32gui.FindWindow("Qt5156QWindowIcon", "Z")
    _mumu_child_hwnd = enumerate_child_windows(_mumu_hwnd)[0]
    print("mumu_child_hwnd: ", _mumu_child_hwnd)
    return _mumu_hwnd, _mumu_child_hwnd


def capture_screenshot(save_path):
    img_rgb = capture_screenshot_no_save()
    cv2.imwrite(save_path, img_rgb)
    return


def capture_screenshot_no_save():
    window_rect = win32gui.GetWindowRect(mumu_child_hwnd)
    global scale_width, scale_height
    scale_width, scale_height = (window_rect[2] - window_rect[0]) / 561, (window_rect[3] - window_rect[1]) / 997
    app = QApplication(sys.argv)
    # 截取窗口的屏幕截图
    screen = QApplication.primaryScreen()
    screenshot = screen.grabWindow(mumu_child_hwnd).toImage()

    # Ensure the image format is correct
    screenshot = screenshot.convertToFormat(4)  # QImage.Format_RGBA8888

    width = screenshot.width()
    height = screenshot.height()
    ptr = screenshot.bits()
    ptr.setsize(screenshot.byteCount())
    img = np.array(ptr).reshape(height, width, 4)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    return img_rgb


def click(x, y):
    x = int(x)
    y = int(y)
    print("Click:", x, y)
    win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(int(x), int(y)))
    win32api.PostMessage(mumu_child_hwnd, win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(int(x), int(y)))
    return


def full_ocr(img_path):
    global ocr_time
    # Read the image
    img = cv2.imread(img_path)
    height, width, _ = img.shape
    w_x1, w_y1, w_x2, w_y2 = (int(48 * scale_width), int(359 * scale_height), int(522 * scale_width), int(402 * scale_height))
    img[w_y1:w_y2, w_x1:w_x2] = (255, 255, 255)
    cv2.imwrite(img_path, img)

    # Define the regions for A and B based on image resolution
    # These coordinates need to be adjusted based on your specific image
    a_region_coords = (int(0.07 * width), int(0.28 * height), int(0.93 * width), int(0.36 * height))  # (x1, y1, x2, y2)
    b_region_coords = (int(0.12 * width), int(0.45 * height), int(0.91 * width), int(0.78 * height))  # (x1, y1, x2, y2)

    start_time = time.time()
    # Perform OCR on the entire image
    ocr_result = ocr.ocr(img_path)

    if ocr_time <= 0.5:
        ocr_time = time.time() - start_time
    print("OCR Time:", ocr_time)

    # Filter OCR results based on the specified regions
    def filter_ocr_results(ocr_results, region_coords):
        x1, y1, x2, y2 = region_coords
        filtered_results = []
        for li in ocr_results:
            current_line = []
            for word_info in li:
                word_bbox = word_info[0]
                word_x1, word_y1 = word_bbox[0]
                word_x2, word_y2 = word_bbox[2]
                if word_x1 >= x1 and word_y1 >= y1 and word_x2 <= x2 and word_y2 <= y2:
                    if current_line and abs(current_line[-1][0][0][1] - word_y1) > 50:
                        # Merge current line into a single result
                        merged_text = ''.join([info[1][0] for info in current_line])
                        filtered_results.append((current_line[0][0], [merged_text]))
                        current_line = []
                    current_line.append(word_info)
            if current_line:
                # Merge the last line
                merged_text = ''.join([info[1][0] for info in current_line])
                filtered_results.append((current_line[0][0], [merged_text]))
        return filtered_results

    a_result = filter_ocr_results(ocr_result, a_region_coords)
    b_result = filter_ocr_results(ocr_result, b_region_coords)

    # Extract text from the OCR result
    ques = [word_info[1][0] for word_info in a_result]
    ans1234 = [word_info[1][0] for word_info in b_result]

    # if no question detected, move the image to error folder
    if not ques and not os.path.exists(f"error/no_ques/{os.path.basename(img_path)}"):
        if not np.array_equal(get_pixel_color_path(img_path, 282 * scale_width, 678 * scale_width), (255, 143, 54)) and not np.array_equal(get_pixel_color_path(img_path, 367 * scale_width, 920 * scale_width), (255, 143, 54)):
            os.link(img_path, f"error/no_ques/{os.path.basename(img_path)}")
            with open(f"error/no_ques/{os.path.splitext(os.path.basename(img_path))[0]}.log", "w", encoding='utf-8') as f:
                f.write(f"ques: {ques}\nans: {ans1234}\nocr_result: {ocr_result}")

    # Print the results
    print("Ques:", ques)
    print("Ans1234:", ans1234)
    return ques, ans1234


def get_info():
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
            _answers = []
            for item in data["response_data"][0]["body"]["data"]:
                # 将答案转换为数字
                question = item["content"]
                ans = json.loads(item["question"][0]["option"])
                answer = item["question"][0]["answer"]
                option_value = ""
                if answer == "A":
                    option_value = ans[0]["option_value"]
                elif answer == "B":
                    option_value = ans[1]["option_value"]
                elif answer == "C":
                    option_value = ans[2]["option_value"]
                elif answer == "D":
                    option_value = ans[3]["option_value"]
                _answers.append({"question": question, "answer": option_value})
            # print("答案数组为:", answers)
            return _answers
        except json.JSONDecodeError as e:
            print("JSON 解码错误:", e)
    else:
        print("文件没有有效数据行。")
    return None


def find_best_match(ques, ans1234, _answers):
    # Find the closest match for the given question
    closest_ques = difflib.get_close_matches(ques, [item['question'] for item in _answers], n=1, cutoff=0.6)
    if not closest_ques:
        if "zip" in [item['question'] for item in _answers]:
            closest_ques = ["zip"]
        else:
            return None

    # Find the correct answer for the closest question
    correct_answer = None
    for item in _answers:
        if item['question'].lower() == closest_ques[0].lower():
            correct_answer = item['answer']
            break

    if not correct_answer:
        return None

    # Normalize the correct answer
    normalized_correct_answer = normalize_text(correct_answer)

    best_match = None
    highest_ratio = 0
    # Find the best match for the answers
    for ans in ans1234:
        normalized_ans = normalize_text(ans)
        ratio = difflib.SequenceMatcher(None, normalized_correct_answer, normalized_ans).ratio()
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = ans
    return best_match


def perform_ocr_and_click(img_path):
    # Perform OCR on the screenshot
    ocr_result = ocr.ocr(img_path)

    # Check if "开始PK" is in the OCR results
    for line in ocr_result:
        for word_info in line:
            if "开始PK" or "继续PK" in word_info[0]:
                print("Found '开始PK', clicking...")
                click(393 * scale_width, 925 * scale_height)
                return


def get_pixel_color(image, x, y):
    x = int(x)
    y = int(y)
    # 获取像素颜色
    pixel_color = image[y, x]
    return pixel_color


def get_pixel_color_path(path, x, y):
    image = cv2.imread(path)
    x = int(x)
    y = int(y)
    # 获取像素颜色
    pixel_color = image[y, x]
    return pixel_color


def get_pixel_colors(path, coordinates):
    """
    获取多个坐标的RGB颜色

    :param path: 图像路径
    :param coordinates: 坐标列表，格式为 [(x1, y1), (x2, y2), ...]
    :return: 颜色列表，格式为 [(r1, g1, b1), (r2, g2, b2), ...]
    """
    image = cv2.imread(path)
    colors = []
    for (x, y) in coordinates:
        x = int(x)
        y = int(y)
        # 获取像素颜色
        pixel_color = image[y, x]
        colors.append(tuple(pixel_color))
    return colors


def wait_for_next_word():
    while True:
        img = capture_screenshot_no_save()
        if np.array_equal(get_pixel_color(img, 284 * scale_width, 471 * scale_height), (251, 245, 242)):
            break
        if np.array_equal(get_pixel_color(img, 282 * scale_width, 678 * scale_height), (255, 143, 54)):
            break
        if np.array_equal(get_pixel_color(img, 367 * scale_width, 920 * scale_height), (255, 143, 54)):
            break
        time.sleep(0.2)
    return


def main():
    global answers

    def click_answer(_locate):
        # Add a random offset around the center
        offset_x = random.randint(-10, 10)
        offset_y = random.randint(-10, 10)
        click((287 + offset_x) * scale_width, (target_y_list[_locate] + offset_y) * scale_height)
        return

    last_answer = answers

    # 1. 如果存在则点击开始PK
    path = "png/" + str(int(time.time() * 100)) + ".png"
    capture_screenshot(path)
    perform_ocr_and_click(path)

    # 2. 延迟0.5s，直到读取文件内容
    while answers == last_answer:
        time.sleep(0.5)
        last_answer = answers
        answers = get_info()

    print("Answers updated.")

    i = 0
    while True:
        # 5. 判断下一个词
        wait_for_next_word()  # 等待直到词可用
        time.sleep(0.2)
        print("Next word is available.")

        # 3. full_ocr
        path = "png/" + str(int(time.time() * 100)) + ".png"
        capture_screenshot(path)
        ques, ans1234 = full_ocr(path)

        if np.array_equal(get_pixel_color_path(path, 282 * scale_width, 678 * scale_width), (255, 143, 54)):
            # 执行下一局
            click(276 * scale_width, 678 * scale_height)
            time.sleep(0.5)
            break

        if np.array_equal(get_pixel_color_path(path, 367 * scale_width, 920 * scale_width), (255, 143, 54)):
            # 执行下一局
            time.sleep(0.5)
            break

        # 4. 解析并选择答案
        if len(ques) > 0:
            i = 0
            best_match = find_best_match(ques[0], ans1234, answers)
            if best_match:
                print("Best Match:", best_match)
                locate = ans1234.index(best_match)
                if locate > 3:
                    locate = 3
                    os.link(path, f"error/out_of_locate/{os.path.basename(path)}")
                    with open(f"error/out_of_locate/{os.path.splitext(os.path.basename(path))[0]}.log", "w", encoding='utf-8') as f:
                        f.write(f"ques: {ques}\nans: {ans1234}\nanswers: {answers}\nbest_match: {best_match}\nlocate: {locate}")
                    print("No match found.")
                click_answer(locate)
            else:
                os.link(path, f"error/no_match/{os.path.basename(path)}")
                with open(f"error/no_match/{os.path.splitext(os.path.basename(path))[0]}.log", "w", encoding='utf-8') as f:
                    f.write(f"ques: {ques}\nans: {ans1234}\nanswers: {answers}\nbest_match: {best_match}")
                print("No match found.")
        else:
            i += 1
            if i < 3:
                print(f"No question detected. Retry {i} times.")
                continue
            else:
                print("No question detected. Rand click.")
                locate = random.randint(0, 3)
                click_answer(locate)
        time.sleep(0.3)


def makedirs():
    os.makedirs("png", exist_ok=True)
    os.makedirs("error", exist_ok=True)
    os.makedirs("error/no_ques", exist_ok=True)
    os.makedirs("error/no_match", exist_ok=True)
    os.makedirs("error/out_of_locate", exist_ok=True)


makedirs()
answers = get_info()
# Initialize PaddleOCR
ocr = PaddleOCR()
mumu_hwnd, mumu_child_hwnd = get_all_windows()  # 获取窗口句柄
while True:
    main()
    gc.collect()  # 回收内存
    if ocr_time > 0.5:  # 如果OCR时间超过0.5秒，重新初始化OCR
        ocr = PaddleOCR()
        ocr_time = 0.00
        print("OCR reinitialized.")
