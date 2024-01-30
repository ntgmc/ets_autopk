import win32gui
def get_window_properties(hwnd):
    window_title = win32gui.GetWindowText(hwnd)
    class_name = win32gui.GetClassName(hwnd)
    window_text = win32gui.GetWindowText(hwnd)
    window_rect = win32gui.GetWindowRect(hwnd)
    return window_title, class_name, window_text, window_rect
def enumerate_child_windows(parent_hwnd):
    def callback(hwnd, windows):
        windows.append(hwnd)
        return True
    child_windows = []
    win32gui.EnumChildWindows(parent_hwnd, callback, child_windows)
    return child_windows
def print_window_info(hwnd):
    window_title, class_name, window_text, window_rect = get_window_properties(hwnd)
    print('--'*60)
    print(f"窗口句柄：{hwnd}")
    print(f"标题：{window_title}")
    print(f"类名：{class_name}")
    print(f"文本内容：{window_text}") 
    print(f"坐标：{window_rect}")
parent_hwnd = win32gui.FindWindow("Qt5156QWindowIcon", "Z")
child_windows =enumerate_child_windows(parent_hwnd)
for child_hwnd in child_windows:
    print_window_info(child_hwnd)