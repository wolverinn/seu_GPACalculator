import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data as data
import torch.optim as optim
from torch.autograd import Variable
from torchvision import datasets, transforms
import os
import numpy as np
from PIL import Image
import time

BATCH_SIZE=512 #大概需要2G的显存
EPOCHS=7 # 总共训练批次
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu") # 让torch判断是否使用GPU，建议使用GPU环境，因为会快很多

class ConvNet(nn.Module):
    def __init__(self):
        super().__init__()
        # (1,96,200)
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

def name2label(name):
    label = torch.zeros(40,dtype=torch.float)
    for i, c in enumerate(name):
        idx = i*10 + int(c)
        label[idx] = 1
    # label = torch.zeros(4, dtype=torch.long)
    # for i in range(4):
    #     label[i] = int(name[i])
    return label

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
        name = str(img_path).split('_')[1]
        name = name.split('.')[0]
        label = name2label(name)
        return data,label

    def __len__(self):
        return len(self.imgs)

train_loader = data.DataLoader(ImageSet("./jwc-train/"),batch_size=BATCH_SIZE,shuffle=True)
test_loader = data.DataLoader(ImageSet("./jwc-test/"),batch_size=1,shuffle=True)
validation_loader = data.DataLoader(ImageSet("./jwc-validation/"),batch_size=1,shuffle=True)

model = ConvNet().to(DEVICE)
print(model)
optimizer = optim.Adam(model.parameters())
criterion = nn.MultiLabelSoftMarginLoss()
valid_loss_min = np.Inf

def train(model, device, train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        data_v = Variable(data)
        target_v = Variable(target)
        optimizer.zero_grad()  # 梯度归零
        output = model(data_v)
        loss = criterion(output, target_v)
        loss.backward()
        optimizer.step()  # 更新梯度
        if(batch_idx+1)%10 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))

def validation(model, device, validation_loader,epoch):
    global valid_loss_min,startTick
    model.eval()
    validation_loss = 0
    with torch.no_grad():
        for data, target in validation_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            validation_loss += criterion(output, target).item() # 将一批的损失相加
    validation_loss /= len(validation_loader.dataset)
    timeSpan = time.clock() - startTick
    print('EPOCH:{}    Time used:{}    Validation set: Average loss: {:.4f}'.format(epoch,str(timeSpan),validation_loss))
    if validation_loss < valid_loss_min:
        valid_loss_min = validation_loss
        print("saving model ...")
        torch.save(model.state_dict(),'jwc_model.pt')

def test(model, device, test_loader):
    model.load_state_dict(torch.load('jwc_model.pt'))
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += criterion(output, target).item() # 将一批的损失相加
            pred_0 = torch.argmax(output[0,0:9])
            pred_1 = torch.argmax(output[0,10:19])
            pred_2 = torch.argmax(output[0,20:29])
            pred_3 = torch.argmax(output[0,30:39])
            pred_name = str(pred_0)+str(pred_1)+str(pred_2)+str(pred_3)
            target_0 = torch.argmax(target[0,0:9])
            target_1 = torch.argmax(target[0,10:19])
            target_2 = torch.argmax(target[0,20:29])
            target_3 = torch.argmax(target[0,30:39])
            target_name = str(target_0)+str(target_1)+str(target_2)+str(target_3)
            if pred_name == target_name:
                correct += 1

    test_loss /= len(test_loader.dataset)
    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))

startTick = time.clock()
for epoch in range(1, EPOCHS + 1):
    train(model, DEVICE, train_loader, optimizer, epoch)
    validation(model, DEVICE, validation_loader,epoch)

test(model, DEVICE, test_loader)
