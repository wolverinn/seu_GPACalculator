import requests
import os
from bs4 import BeautifulSoup
import re
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
import numpy as np

# 识别验证码的神经网络模型
class ConvNet(nn.Module):
    def __init__(self):
        super().__init__()
        # (1,100,210)
        self.conv1=nn.Conv2d(1,10,5,padding=2) # (10,96,200)
        self.conv2=nn.Conv2d(10,16,3,padding=1) # (16,48,100)
        self.conv3=nn.Conv2d(16,32,3,padding=1) # (32,24,50)
        self.fc1 = nn.Linear(32*12*25,1000) # (32,12,25)
        self.fc2 = nn.Linear(1000,40)
        self.dropout = nn.Dropout(0.25)
    def forward(self,x):
        in_size = x.size(0)
        out = self.conv1(x)
        out = F.relu(out)
        out = F.max_pool2d(out, 2, 2)
        out = self.conv2(out)
        out = F.relu(out)
        out = F.max_pool2d(out,2,2)
        out = F.relu(self.conv3(out))
        out = F.max_pool2d(out,2,2)
        out = out.view(in_size,-1) # 扁平化flat然后传入全连接层
        out = self.fc1(out)
        out = F.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        return out

# 此函数用于调用模型识别验证码
def recog(model):
    model.eval()
    with torch.no_grad():
        img = Image.open("code.jpg").convert('L')
        img = img.crop((5,0,205,96))
        data = transforms.ToTensor()(img).unsqueeze(0)
        data = data.to('cpu')
        output = model(data)
        pred_0 = int(torch.argmax(output[0,0:9]))
        pred_1 = int(torch.argmax(output[0,10:19]))
        pred_2 = int(torch.argmax(output[0,20:29]))
        pred_3 = int(torch.argmax(output[0,30:39]))
        vercode = str(pred_0) + str(pred_1) + str(pred_2) + str(pred_3)
        return vercode

url="http://xk.urp.seu.edu.cn/studentService/system/login.action"                                  #登录网址
url2="http://xk.urp.seu.edu.cn/studentService/cs/stuServe/studentExamResultQuery.action"                   #成绩查询网址
info_url="http://xk.urp.seu.edu.cn/jw_service/service/stuCurriculum.action"                          #个人信息获取网址
#验证码获取网址（其中的时间貌似就是一个摆设，任意一个时间都可以获取到最新的验证码）
imgurl="http://xk.urp.seu.edu.cn/studentService/getCheckCode?now=Tue%20Feb%2013%202018%2011:51:54%20GMT+0800%20(%D6%D0%B9%FA%B1%EA%D7%BC%CA%B1%BC%E4)"
credit=[]                       #记录学分
scores=[]                       #记录成绩一栏
scor=[]                         #将成绩换算成对应的绩点
pscor=[]                        #P值
enable_P=0                      #计算P值的标识符

username=input("输入一卡通号：")
password=input("输入统一身份认证密码：")

ses=requests.Session()
verify_ok="0"

# 加载深度学习模型
model = ConvNet().to('cpu')
model.load_state_dict(torch.load('jwc_model.pt',map_location='cpu'))

#尝试自动识别验证码十次
print("尝试自动登陆中，如自动登陆不成功请手动打开图片输入验证码...")
for i in range(10):
    image = ses.get(imgurl)
    if image.status_code != 200:
        print("检查网络连接")
        os.system("pause")
        exit(1)
    f = open('code.jpg', 'wb')
    f.write(image.content)
    f.close()
    vercode = recog(model)
    data = {
        'userName': username,
        'password': password,
        'vercode': vercode,
        'x': '16',  # 别管
        'y': '7'  # 别管
    }
    # 模拟登录
    # wb_data=ses.post(url,data=data,headers=headers)
    wb_data = ses.post(url, data=data)
    gpapage = ses.get(url2)
    if gpapage.url == "http://xk.urp.seu.edu.cn/studentService/cs/stuServe/studentExamResultQuery.action":
        verify_ok="1"
        break
    else:
        pass

if verify_ok=="0":
    image = ses.get(imgurl)
    if image.status_code != 200:
        print("检查网络连接")
        os.system("pause")
        exit(1)
    f = open('code.jpg', 'wb')
    f.write(image.content)
    f.close()
    os.system("code.jpg")
    vercode = input('输入验证码:')
    # 构造提交的表单数据
    # 貌似不需要提交headers
    # headers={
    #     'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    #     'Accept-Encoding':'gzip, deflate',
    #     'Accept-Language':'zh-CN,zh;q=0.9',
    #     'Cache-Control':'max-age=0',
    #     'Connection':'keep-alive',
    #     'Content-Type':'application/x-www-form-urlencoded',
    #     'Host':'xk.urp.seu.edu.cn',
    #     'Origin':'http://xk.urp.seu.edu.cn',
    #     'Referer':'http://xk.urp.seu.edu.cn/studentService/system/showLogin.action',
    #     'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    # }
    data = {
        'userName': username,
        'password': password,
        'vercode': vercode,
        'x': '16',  # 别管
        'y': '7'  # 别管
    }
    # 模拟登录
    # wb_data=ses.post(url,data=data,headers=headers)
    wb_data = ses.post(url, data=data)
    gpapage = ses.get(url2)
    if gpapage.url == "http://xk.urp.seu.edu.cn/studentService/cs/stuServe/studentExamResultQuery.action":
        pass
    else:
        print("登录失败，检查用户名，密码和验证码")
        os.system("pause")
        exit(1)
else:
    print("自动登陆成功，开始计算绩点...")

#获取学分和成绩
gpapage = ses.get(url2)
soup=BeautifulSoup(gpapage.text,'lxml')
trs=soup.find('table',attrs={'id':'table2'}).find_all('tr')
i=-1 # 剔除标题
jump = 0
for tr in trs:
    n=-1
    tds=tr.find_all('td')
    i+=1
    if i==0:continue # 剔除标题
    else:
        for td in tds:
            n+=1
            if n==0:
                jump = 0
            if n==3 and td.string=="不修的课程\xa0": # 剔除不修
                jump = 1
            if n==4:credit.append(float(td.string))
            if n==5:scores.append(td.string.strip('\xa0'))
            if n==7 and td.string!="\xa0" or jump==1: # 剔除选修
                credit.pop()
                scores.pop()

#查询个人信息
info_data={
    'returnStr':'',
    'queryStudentId':username
}
wb_info=requests.post(info_url,data=info_data).text
info_soup=BeautifulSoup(wb_info,'html.parser')
prop=info_soup.find_all('td',attrs={'width':'20%','align':'left'})
for i in prop:
    if i.string=="院系:[100202]信息科学与工程学院":
        enable_P=1
    print(i.string)

#计算绩点
gpa=0.0
all_credit=0.0
for i in range(0,len(scores)):
    if scores[i]=="优":scor.append(4.8)
    elif scores[i]=="良":scor.append(3.8)
    elif scores[i]=="中":scor.append(2.8)
    elif scores[i]=="通过" or scores[i]=="及格":scor.append(1.8)
    elif scores[i]=="不及格" or scores[i]=="不合格":scor.append(0)
    else:
        if float(scores[i])>=96:scor.append(4.8)
        elif float(scores[i])>=93:scor.append(4.5)
        elif float(scores[i])>=90:scor.append(4)
        elif float(scores[i])>=86:scor.append(3.8)
        elif float(scores[i])>=83:scor.append(3.5)
        elif float(scores[i])>=80:scor.append(3)
        elif float(scores[i])>=76:scor.append(2.8)
        elif float(scores[i])>=73:scor.append(2.5)
        elif float(scores[i])>=70:scor.append(2)
        elif float(scores[i])>=66:scor.append(1.8)
        elif float(scores[i])>=63:scor.append(1.5)
        elif float(scores[i])>=60:scor.append(1)
        else:scor.append(0)
    gpa=gpa+scor[i]*credit[i]
    all_credit=credit[i]+all_credit

print("平均绩点：",gpa/all_credit)
if enable_P==1:
    p=0.0
    for i in range(0,len(scores)):
        if scores[i]=="优":pscor.append(95)
        elif scores[i]=="良":pscor.append(85)
        elif scores[i]=="中":pscor.append(75)
        elif scores[i]=="通过" or scores[i]=="及格":pscor.append(60)
        elif scores[i]=="不及格" or scores[i]=="不合格":pscor.append(0)
        else:pscor.append(float(scores[i]))
        p=p+pscor[i]*credit[i]

    print("信息学院的P值：",p/all_credit)
os.system("pause")