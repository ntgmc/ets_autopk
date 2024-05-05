# README  
## 准备工作  
1. 安装MUMU12模拟器(其他模拟器未测试)，安装易听说中学  
2. 设置PK单元为XSJ必修三U1  
3. [安装PaddleOCR](https://gitee.com/paddlepaddle/PaddleOCR/blob/release/2.6/doc/doc_ch/quickstart.md)
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
- 获取窗口句柄并截取屏幕截图。  
- 使用 pytesseract 进行 OCR 识别，识别出问题和答案。  
- 根据识别结果进行逻辑判断：  
- - 如果识别结果为 "恭喜你!" 或 "PK结果提交失败"，则模拟点击一些按钮。  
- - 否则，通过模糊匹配和相似度评分找到最匹配的答案，并模拟点击该答案所在的位置。  
- 记录识别结果日志，如果识别结果不准确，则记录到日志文件中。  