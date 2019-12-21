import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data as data
from torchvision import datasets, transforms
import os
import numpy as np
from PIL import Image
import time

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu") # 让torch判断是否使用GPU，建议使用GPU环境，因为会快很多

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


transform = transforms.Compose([
    transforms.ToTensor(),  # 将图片转换为Tensor,归一化至[0,1]
    # transforms.Normalize(mean=[.5, .5, .5], std=[.5, .5, .5])  # 标准化至[-1,1]
])

class ImageSet(data.Dataset):
    def __init__(self,root):
        # 所有图片的绝对路径
        imgs=os.listdir(root)
        self.imgs=[os.path.join(root,k) for k in imgs]
        self.transforms=transform

    def __getitem__(self, index):
        img_path = self.imgs[index]
        pil_img = Image.open(img_path).convert('L')
        pil_img = pil_img.crop((5,0,205,96))
        if self.transforms:
            data = self.transforms(pil_img)
        else:
            pil_img = np.asarray(pil_img)
            data = torch.from_numpy(pil_img)
        return data

    def __len__(self):
        return len(self.imgs)

recog_loader = data.DataLoader(ImageSet("./img/"),batch_size=1,shuffle=True)
model = ConvNet().to(DEVICE)

def recog(model, device, recog_loader):
    model.load_state_dict(torch.load('jwc_model.pt',map_location='cpu'))
    model.eval()
    with torch.no_grad():
        for data in recog_loader:
            data = data.to(device)
            output = model(data)
            pred_0 = torch.argmax(output[0,0:9])
            pred_1 = torch.argmax(output[0,10:19])
            pred_2 = torch.argmax(output[0,20:29])
            pred_3 = torch.argmax(output[0,30:39])
            pred_name = [int(pred_0),int(pred_1),int(pred_2),int(pred_3)]
            print(pred_name)

recog(model,DEVICE,recog_loader)