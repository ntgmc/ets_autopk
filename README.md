# README  
## 脚本原理
- 使用Fiddler抓包，获取单词题目和答案
- 使用PaddeOCR识别题目和答案
- 使用difflib匹配相似度最高的答案
- 使用pyautogui模拟鼠标点击
## 准备工作  
1. 安装MUMU12模拟器(其他模拟器未测试)，安装易听说中学  
2. 安装Fiddler, Python3.11, [安装PaddleOCR](https://gitee.com/paddlepaddle/PaddleOCR/blob/release/2.6/doc/doc_ch/quickstart.md)
3. 安装Python模块
4. Fiddler设置开启HTTPS抓包
5. FiddlerScript设置, 替换成自己的路径
    ```javascript
    static function OnBeforeResponse(oSession: Session) {
            if (m_Hide304s && oSession.responseCode == 304) {
                oSession["ui-hide"] = "true";
            }
            // if (oSession.fullUrl.Contains("baidu.com")){
            if (oSession.fullUrl.Contains("https://api.ets100.com/g/word/struct")){
                oSession.utilDecodeResponse();//消除保存的请求可能存在乱码的情况
                var jsonString = oSession.GetResponseBodyAsString();
                var responseJSON = Fiddler.WebFormats.JSON.JsonDecode(jsonString);
                if((responseJSON.JSONObject=='System.Collections.ArrayList' || responseJSON.JSONObject=='System.Collections.Hashtable')&&jsonString!='[]'&&jsonString!='{}'){
                    // 判断是否是json数据 然后保存
                    var str='{}';//构造自己的JSON http请求的信息及返回的结果
                    var data = Fiddler.WebFormats.JSON.JsonDecode(str);
                    data.JSONObject["request_method"] = oSession.RequestMethod;
                    var requestString = oSession.GetRequestBodyAsString();
                    data.JSONObject["request_body"]= requestString;
                    data.JSONObject["response_data"] = responseJSON.JSONObject;
                    data.JSONObject["url"] = oSession.fullUrl;
                    data.JSONObject["response_code"] = oSession.responseCode;
                    jsonString = Fiddler.WebFormats.JSON.JsonEncode(data.JSONObject)
                    // 保存文件到本地
                    var fso;
                    var file;
                    fso = new ActiveXObject("Scripting.FileSystemObject");
                    // 替换成自己的路径
                    file = fso.OpenTextFile("E:\\spider_img\\Sessions.dat",8 ,true, true);
                    file.writeLine(jsonString);
                    file.writeLine("\n");
                    file.close();
                    // 数据通过post请求发送自己的后台服务保存 
                    FiddlerObject.log('2222222222222222'+jsonString); 
                    // methods
                    var method = "POST";
                    var myUrl = 'http://localhost:8000/fiddler'
                    var url = myUrl+'?data='+Utilities.UrlEncode(jsonString);
                    var protocol = "HTTP/1.1";
                    var raw="";
                    var selected: Session = oSession;
                    raw += method + " " + url + " " + protocol + "\r\n";
                    raw +="Host:localhost:8000\r\n";
                    raw +="Connection: keep-alive\r\n";
                    raw +="Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n";
                    raw +="User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36\r\n";
                    raw +="Accept-Encoding: gzip,deflate,sdch\r\n";
                    raw +="Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4\r\n";
                    raw +="Content-Type: application/json\r\n";
                    var body= "jsondata=''";
                    raw += "\r\n" + body;
                    FiddlerObject.utilIssueRequest(raw);
                }
            }
        }
    ```
6. 模拟器网络设置代理, 本地IP:端口(默认8888), 可通过ipconfig查看本地IP

## 使用方法
1. 修改[main.py](https://github.com/ntgmc/ets_autopk/blob/main/main.py)
    - get_all_windows()  
        `mumu_hwnd = win32gui.FindWindow("Qt5156QWindowIcon", "Z")`  
    - get_info()  
        `file_path = r"E:\spider_img\Sessions.dat"`  
2. 安装所需模块，运行[download.bat](https://github.com/ntgmc/ets_autopk/blob/main/download.bat)  
3. 确保模拟器没有最小化  
4. 打开Fiddler
5. 运行main.py
6. 缓存过大时运行[clear.bat](https://github.com/ntgmc/ets_autopk/blob/main/clear.bat)，自动删除缓存
