# seu_GPACalculator
automatically log in and calculate GPA for students in southeast university   

自动登录SEU教务处，计算除选修课的课程的平均绩点 

## 用法：  

我写了两个版本：一个版本需要手动输入验证码，另一个版本可以使用神经网络自动识别验证码

#### 不含验证码识别的版本

1. 下载[GPAcalc_manual.exe](https://github.com/wolverinn/seu_GPACalculator/releases)程序直接运行  
2. 下载```GPAcalc_manual.py```脚本，安装requests库和BeautifulSoup库后在python3环境下运行   

#### 含验证码识别的版本

可以使用```GPAcalc.py```脚本运行，需要以下依赖库：
- torch
- torchvision
- requests
- bs4

运行的时候需要将此脚本和```jwc_model.pt```放在同一目录下。

也可以直接下载[GPAcalc.rar](https://github.com/wolverinn/seu_GPACalculator/releases)文件，解压之后在文件夹里找到```GPAcalc.exe```，然后运行。

## 关于教务处验证码识别

最初尝试的是使用Tesseract OCR 进行识别，但是准确率很低，只有不到30%，后来使用卷积神经网络进行识别，能达到90%的准确率。具体可以参考我的另一个repository：

[GitHub - wolverinn/SEU-captcha-recognition: recognition of verification code in jwc.seu.edu.cn using CNN implemented with PyTorch](https://github.com/wolverinn/SEU-captcha-recognition)

- 没来得及完善的方面：  
1. 没有界面  
2. 效率方面还可以改进  
3. 没有计算出国绩点的功能

其他，欢迎 pull-request...
