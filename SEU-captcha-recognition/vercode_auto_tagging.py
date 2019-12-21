import requests
import os
import shutil
import time

# set GOOGLE_APPLICATION_CREDENTIALS=E:\downloads\tamures-fb7df02185f1.json
# $env:GOOGLE_APPLICATION_CREDENTIALS="E:\downloads\tamures-fb7df02185f1.json"

url2="http://xk.urp.seu.edu.cn/studentService/cs/stuServe/studentExamResultQuery.action"
url="http://xk.urp.seu.edu.cn/studentService/system/login.action"
imgurl="http://xk.urp.seu.edu.cn/studentService/getCheckCode?now=Tue%20Feb%2013%202018%2011:51:54%20GMT+0800%20(%D6%D0%B9%FA%B1%EA%D7%BC%CA%B1%BC%E4)"

username=["213161509","213161536","213163875","213160788","213162697","213162554"]
password=["","","","","",""]
counting = 2845
image_path = "./code.jpg"
save_path = "./jwc/"

def detect_text(path):
    """Detects text in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    # [START vision_python_migration_text_detection]
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    if len(texts) > 0:
        return texts[0].description
    else:
        return ""

def check_correction(vercode,ses,num):
    try:
        int(vercode)
    except:
        print("not all numbers")
        return False
    data = {
        'userName': username[num],
        'password': password[num],
        'vercode': vercode,
        'x': '16',  # 别管
        'y': '7'  # 别管
    }
    wb_data = ses.post(url, data=data)
    gpapage = ses.get(url2)
    if gpapage.url == "http://xk.urp.seu.edu.cn/studentService/cs/stuServe/studentExamResultQuery.action":
        wb_data.close()
        gpapage.close()
        return True
    else:
        wb_data.close()
        gpapage.close()
        return False

for i in range(8000):
    if i%1000 == 0 and i>0:
        time.sleep(120)
    if i%100 == 0:
        print("==========={} tries============".format(str(i)))
    ses=requests.session()
    try:
        image=ses.get(imgurl,timeout = 8)
    except:
        print("connection declined")
        time.sleep(1)
        continue
    if image.status_code !=200:
        print("检查网络连接")
        os.system("pause")
        exit(1)
    f = open(image_path,'wb')
    f.write(image.content)
    f.close()
    image.close()

    result = detect_text(image_path).strip('\n')
    temp_num = i//20
    num = temp_num%6
    if len(result) is 4:
        if check_correction(result,ses,num) is True:
            new_image = save_path + str(counting) + "_" + result + ".jpg"
            counting = counting + 1
            shutil.copyfile(image_path,new_image)
            print(result)
        else:
            result = result.replace('/','1')
            result = result.replace('A','4').replace('o','0').replace('O','0').replace('s','5').replace('S','5').replace('g','9')
            new_image = "./wrong_rec/" + str(counting) + "_" + result + ".jpg"
            try:
                shutil.copyfile(image_path, new_image)
            except:
                pass
            print("login failed, wrong recognition")
    else:
        print("lengths not four")
    ses.close()
    os.remove(image_path)
