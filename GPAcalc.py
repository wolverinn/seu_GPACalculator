import requests
import os
from bs4 import BeautifulSoup

url="http://xk.urp.seu.edu.cn/studentService/system/login.action"                                  #登录网址
url2="http://xk.urp.seu.edu.cn/studentService/cs/stuServe/studentExamResultQuery.action"                   #成绩查询网址
info_url="http://xk.urp.seu.edu.cn/jw_service/service/stuCurriculum.action"                          #个人信息获取网址
#验证码获取网址（其中的时间貌似就是一个摆设，任意一个时间都可以获取到最新的验证码）
imgurl="http://xk.urp.seu.edu.cn/studentService/getCheckCode?now=Tue%20Feb%2013%202018%2011:51:54%20GMT+0800%20(%D6%D0%B9%FA%B1%EA%D7%BC%CA%B1%BC%E4)"
credit=[]                       #记录学分
scores=[]                       #记录成绩一栏
scor=[]                         #将成绩换算成对应的绩点

username=input("程序自动登陆时请将图片中的验证码输入程序\n输入一卡通号：")
password=input("输入统一身份认证密码：")

#下载验证码图片并手动读取,使用session保持cookie
ses=requests.Session()
image=ses.get(imgurl)
f = open('code.jpg','wb')
f.write(image.content)
f.close()
os.system("code.jpg")
vercode=input('输入验证码:')

#构造提交的表单数据
#貌似不需要提交headers
# headers={
#     'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#     'Accept-Encoding':'gzip, deflate',
#     'Accept-Language':'zh-CN,zh;q=0.9',
#     'Cache-Control':'max-age=0',
#     'Connection':'keep-alive',
#     'Content-Type':'application/x-www-form-urlencoded',
#     # 'Cookie':cookie,
#     'Host':'xk.urp.seu.edu.cn',
#     'Origin':'http://xk.urp.seu.edu.cn',
#     'Referer':'http://xk.urp.seu.edu.cn/studentService/system/showLogin.action',
#     'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
# }
data={
    'userName':username,
    'password':password,
    'vercode':vercode,
    'x':'16',                            #别管
    'y':'7'                              #别管
}
#模拟登录
# wb_data=ses.post(url,data=data,headers=headers)
wb_data=ses.post(url,data=data)
gpapage=ses.get(url2)
if gpapage.url=="http://xk.urp.seu.edu.cn/studentService/cs/stuServe/studentExamResultQuery.action":pass
else:
    print("登录失败，检查用户名，密码和验证码")
    exit(1)
#获取学分和成绩
soup=BeautifulSoup(gpapage.text,'lxml')
trs=soup.find('table',attrs={'id':'table2'}).find_all('tr')
i=-1
for tr in trs:
    n=-1
    tds=tr.find_all('td')
    i+=1
    if i==0:continue
    else:
        for td in tds:
            n+=1
            if n==4:credit.append(float(td.string))
            if n==5:scores.append(td.string.strip('\xa0'))
            if n==7 and td.string!=" ":
                credit.pop()
                scores.pop()

#查询个人信息
info_data={
    'returnStr':'',
    'queryStudentId':username,
    'queryAcademicYear':'17-18-3'
}
wb_info=requests.post(info_url,data=info_data).text
info_soup=BeautifulSoup(wb_info,'html.parser')
prop=info_soup.find_all('td',attrs={'width':'20%','align':'left'})
for i in prop:
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
os.system("pause")