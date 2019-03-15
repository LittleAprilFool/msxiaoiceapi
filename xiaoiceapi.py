import requests
import json
import time
import sys
from bs4 import BeautifulSoup
from flask import Flask,request,jsonify
import re

class xiaoiceApi():
    
    def __init__(self):
        self.headers = {}
        self.loadheaders()

    def loadheaders(self):
        '''
            导入headers
        '''
        with open("./headers.txt") as headers:
            line = headers.readline().strip()
            while line:
                key = line.split(":")[0]
                #firefox里的原始头冒号后面会多出一个空格，需除去
                self.headers[key] = line[len(key)+1:].strip()
                line = headers.readline().strip()            

    def chat(self, input_strs):
        '''
        聊天
        
            args (str):   
                input_strs  问题  
            return (dict):  
                status      状态  
                text        内容        
        '''
        if not self.headers:
            return self.dicts("error", "请打开浏览器 复制并将headers放入headers.txt中")
        data = {
            'location':'msgdialog',
            'module':'msgissue',
            'style_id':1,
            'text':input_strs,
            'uid':5175429989,
            'tovfids':'',
            'fids':'',
            'el':'[object HTMLDivElement]',
            '_t':0,
        }
        
        try:
            #原http的api已改为https的api
            url = 'https://www.weibo.com/aj/message/add?ajwvr=6&__rnd=1552674414345'
            page = requests.post(url, data=data, headers=self.headers)
            self.savePage(page.text, "./tmp/postpage.txt")
            print("yeah!!")
            print(page.json()['msg'])
            if page.json()['code'] == '100000':
                code, text, res_type = self.loop(input_strs)
                return self.dicts(code, res_type, text)
            else:
                return self.dicts("500", "failed", page.json()['msg'])
        except Exception as e:
            return self.dicts("500", "error", e)
    
    def dicts(self, status, res_type, text):
        '''
            包装return
        '''
        return {"status":status, "type":res_type, "text":text}

    def loop(self, input_strs):
        '''  
            刷新直到获取到回答
        '''
        print('Debugging Loop')
        times = 1
        while times <= 20:
            times += 1
            #同上，原http的api已改为https的api,另外headers用全反而无法获取页面，(只需用到cookies
            url = "https://api.weibo.com/webim/2/direct_messages/conversation.json?convert_emoji=1&count=15&max_id=0&uid=5175429989&is_include_group=0&source=209678993&t=1552675488336"
            cookie_tmp = "_ga=GA1.2.1323135797.1543259526; __gads=ID=11890c9343039e44:T=1543259536:S=ALNI_MZBb4oaTQKSpskNyLlcY340PO2ohA; SINAGLOBAL=6434364709577.638.1543259530639; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5A9K8pQGjruGwwS51kqfs25JpX5KMhUgL.FoeR1hnRSKMpeKM2dJLoIXnLxKBLBonL12BLxK-L1-zL1--LxK-LBKBLBoBLxKML1-2L1hBLxKqLB.2LB.2LxKqLBo5LBoBLxK-LBo5L12qLxKqLBK2L1het; wvr=6; UOR=,,login.sina.com.cn; ALF=1584210310; SSOLoginState=1552674314; SCF=Ah59PAAKLGytl5ESxKQPQjwd6mgIPW_Sgnc0xxh2Iv2CPP0BOnJIB2bX3SGHbD_yw_NS1U0Fg3k1hBDEdSdHoMA.; SUB=_2A25xj55aDeRhGeVG41oZ9SnNyjuIHXVS_IiSrDV8PUNbmtBeLUvckW9NT5xkMXeApWs4OVjFPi5z4GeJwm8qs6G5; SUHB=0laV4-3uQHGA91; _s_tentry=-; Apache=7654896415260.557.1552674402963; ULV=1552674402979:6:2:2:7654896415260.557.1552674402963:1552359921146; webim_unReadCount=%7B%22time%22%3A1552675474252%2C%22dm_pub_total%22%3A0%2C%22chat_group_pc%22%3A0%2C%22allcountNum%22%3A0%2C%22msgbox%22%3A0%7D"
            response = requests.get(url, headers={"Cookie":cookie_tmp, "Referer": "https://api.weibo.com/chat/"})
            self.savePage(response.text, "./tmp/response.txt")
            res_text = response.json()['direct_messages']
            message = res_text[0]
            text = message['text']
            if text:
                 if text == input_strs:
                     time.sleep(0.3)
                     continue
            return 200, text, "text"
        text = "错误： 已达到最大重试次数"
        return 500, text, "failed"
            
    def savePage(self, text, file):
        with open(file, "w") as f:
            f.write(text)
    
    def api(self):
        app = Flask(__name__)

        @app.route("/")
        def index():
            que = request.args.get("que")
            ans = self.chat(que)
            return jsonify(ans)
        app.run()

if __name__ == '__main__':
    xb = xiaoiceApi()
    xb.api()
