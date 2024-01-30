# README  
## 使用方法
1. 修改[main.py](https://github.com/ntgmc/ets_autopk/blob/main/main.py)中的  

（1）设置 Tesseract OCR 引擎路径（根据你的安装路径进行修改）  
`pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`  

（2）填写模拟器标题  
`mumu_window = gw.getWindowsWithTitle("Z") `  

2. 安装所需模块，运行[download.bat](https://github.com/ntgmc/ets_autopk/blob/main/download.bat)  

3. 确保没有程序挡在模拟器前  

4. 点击开始pk后运行main.py  

5. 如想更换其他单元单词，请按格式修改  
`json\words.json, json\ans.json, json\ques.json`  

6. ocr-custom中为ocr词库，更换单词建议按格式修改

7. 缓存过大时运行[clear.bat](https://github.com/ntgmc/ets_autopk/blob/main/clear.bat)，自动删除缓存  
## 错误纠正方法  
修改[json\replace.json](https://github.com/ntgmc/ets_autopk/blob/main/json/replace.json)  

格式为：`"要替换的词": "替换后的词",`  