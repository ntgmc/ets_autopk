# README  
## 准备工作  

1. 安装MUMU12模拟器(其他模拟器未测试)，安装易听说中学  

2. 设置PK单元为XSJ必修三U1  
## 使用方法
1. 修改[main.py](https://github.com/ntgmc/ets_autopk/blob/main/main.py)中的  

（1）设置 Tesseract OCR 引擎路径（根据你的安装路径进行修改）  
`pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`  

（2）填写模拟器标题  
`mumu_hwnd = win32gui.FindWindow("Qt5156QWindowIcon", "Z")`  

2. 安装所需模块，运行[download.bat](https://github.com/ntgmc/ets_autopk/blob/main/download.bat)  

3. 确保模拟器没有最小化  

4. 运行main.py  

5. 默认为XSJ必修三U1，如想更换其他单元单词，请按格式修改  
`json\words.json, json\ans.json, json\ques.json`  

6. ocr-custom中为ocr词库，更换单词建议按格式修改

7. 缓存过大时运行[clear.bat](https://github.com/ntgmc/ets_autopk/blob/main/clear.bat)，自动删除缓存  
## 错误纠正方法  
修改[json\replace.json](https://github.com/ntgmc/ets_autopk/blob/main/json/replace.json)  

格式为：`"要替换的词": "替换后的词",`  
## 脚本原理
- 使用Tesseract-OCR进行本地OCR  
- 使用win32gui获取模拟器窗口及其子窗口句柄  
- 使用PyQt及窗口句柄进行截图  
- 使用threading进行多线程OCR  
- 使用fuzzywuzzy进行模糊匹配  
- 使用win32api及win32con模拟鼠标点击  