# -*- coding: utf-8 -*-
"""““CS543_MP4_part2_starter_code_ipynb”的副本”的副本.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vwmpTkpn0hW0qH0yWaMcGvS44kS-DbMJ
"""

# Mounting your Google Drive is optional, and you could also simply copy and
# upload the data to your colab instance. This manula upload is also easy to do, 
# but you will have to figure out how to do it.
from google.colab import drive
drive.mount('/content/gdrive/')

import os
if not os.path.exists("/content/gdrive/My Drive/Colab Notebooks/CS_543_MP4"):
    os.makedirs("/content/gdrive/My Drive/Colab Notebooks/CS_543_MP4")
os.chdir("/content/gdrive/My Drive/Colab Notebooks/CS_543_MP4")

# Commented out IPython magic to ensure Python compatibility.
# download dataset 
#if not os.path.exists("/content/gdrive/My Drive/Colab Notebooks/CS_543_MP4/data"):
# %pip install -U gdown
import gdown
url = "https://drive.google.com/uc?id=1sdmNN6b3stiDCwyZbVsl5vS5VbPnKixa"
gdown.download(url, quiet=False)
!unzip -qqo data.zip
!rm data.zip

import glob
import os
import numpy as np
import random
import time
from tqdm.notebook import tqdm
import matplotlib.pyplot as plt

import cv2
from PIL import Image
import torch
from torch import nn, optim
import torch.nn.functional as F
from torch.utils import data
from torchvision import models
from torchvision.transforms import ToTensor, Normalize

# global variable
device = torch.device("cuda:0")

class SegmentationDataset(data.Dataset):
    """
    Data loader for the Segmentation Dataset. If data loading is a bottleneck,
    you may want to optimize this in for faster training. Possibilities include
    pre-loading all images and annotations into memory before training, so as
    to limit delays due to disk reads.
    """

    def __init__(self, split="train", data_dir="data"):
        assert (split in ["train", "val", "test"])
        self.img_dir = os.path.join(data_dir, split)
        self.classes = []
        with open(os.path.join(data_dir, 'classes.txt'), 'r') as f:
            for l in f:
                self.classes.append(l.rstrip())
        self.n_classes = len(self.classes)
        self.split = split
        self.data = glob.glob(self.img_dir + '/*.jpg')
        self.data = sorted([os.path.splitext(l)[0] for l in self.data])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        img = Image.open(self.data[index] + '.jpg')
        if self.split == 'test':
            gt = Image.new('RGB', img.size)
        else:
            gt = Image.open(self.data[index] + '.png')
        img = ToTensor()(img)
        img = Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])(img)
        gt = np.asarray(gt)
        gt = torch.from_numpy(np.array(gt)).long().unsqueeze(0)
        return img, gt

train_dataset = SegmentationDataset(split='train')

# vis the training set
mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])
fig, axs = plt.subplots(ncols=5, nrows=2, figsize=(22, 7))
for idx, ax_i in enumerate(axs.T):
    ax = ax_i[0]
    img, gt = train_dataset[idx]
    img = std * img.permute((1, 2, 0)).cpu().numpy() + mean
    gt = gt.squeeze().numpy()
    ax.imshow((img * 255).astype(np.uint8))
    ax.axis('off')
    ax = ax_i[1]
    ax.imshow(gt)
    ax.axis('off')
fig.tight_layout()
plt.savefig('vis_trainset.pdf', format='pdf', bbox_inches='tight')

resnet18 = models.resnet18(pretrained=True)

from torchvision.models.resnet import conv1x1
##########
#TODO: design your own network here. The expectation is to write from scratch. But it's okay to get some inspiration 
#from conference paper. We are providing a very simple network that does a single 1x1 convolution to prdict the class label.
##########

import torch.nn as nn
import torchvision.models as models




# class MyModel(nn.Module):
#     def __init__(self, n_classes):
#         super(MyModel, self).__init__()

#         # Load the pre-trained ResNet-18 model
#         resnet = models.resnet18(pretrained=True)
        
#         # Remove the last two layers (global average pooling and fully connected layers)
#         self.features = nn.Sequential(*list(resnet.children())[:-2])

#         # Modify the ResNet-18 architecture to include dilated convolutions
#         dilation = 2
#         self.features[7][1].conv1 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=dilation, dilation=dilation, bias=False)
#         self.features[7][1].conv2 = nn.Conv2d(512, 512, kernel_size=3, padding=dilation, dilation=dilation, bias=False)

#         # Global average pooling
#         self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        
#         # Fully connected layer
#         self.fc = nn.Linear(512, n_classes)

#     def forward(self, img):
#         x = self.features(img)  # Extract features from ResNet-18
#         x = self.avgpool(x)  # Apply global average pooling
#         x = torch.flatten(x, 1)  # Flatten tensor
#         x = self.fc(x)  # Apply the fully connected layer
#         return x


# class MyModel(nn.Module):
#     def __init__(self, n_classes):
#         super(MyModel, self).__init__()

#         # Load the pre-trained ResNet-18 model
#         resnet = models.resnet18(pretrained=True)
        
#         # Remove the last two layers (global average pooling and fully connected layers)
#         self.features = nn.Sequential(*list(resnet.children())[:-2])

#         # Modify the ResNet-18 architecture to include dilated convolutions
#         dilation = 2
#         self.features[7][1].conv1 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=dilation, dilation=dilation, bias=False)
#         self.features[7][1].conv2 = nn.Conv2d(512, 512, kernel_size=3, padding=dilation, dilation=dilation, bias=False)

#         # Decoder with a fully convolutional layer
#         self.decoder = nn.Sequential(
#             nn.Conv2d(512, n_classes, kernel_size=1),  # 1x1 convolution to reduce channels to n_classes
#             nn.ReLU(inplace=True),
#             nn.Upsample(scale_factor=32, mode='bilinear', align_corners=True)  # Upsample to original image resolution
#         )

#     def forward(self, img):
#         x = self.features(img)  # Extract features from ResNet-18
#         x = self.decoder(x)  # Decode the features using the fully convolutional layer
#         return x

# import torch
# import torch.nn as nn
# import torchvision.models as models

# import torch
# import torch.nn as nn
# import torchvision.models as models

# class MyModel(nn.Module):
#     def __init__(self, n_classes):
#         super(MyModel, self).__init__()

#         # Load the pre-trained ResNet-18 model
#         resnet = models.resnet18(pretrained=True)
        
#         # Remove the last two layers (global average pooling and fully connected layers)
#         self.features = nn.Sequential(*list(resnet.children())[:-2])
#         self.dropout = nn.Dropout(p=0.5)
#         # Modify the ResNet-18 architecture to include dilated convolutions
#         # dilation = 2
#         # self.features[7][1].conv1 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=dilation, dilation=dilation, bias=False)
#         # self.features[7][1].conv2 = nn.Conv2d(512, 512, kernel_size=3, padding=dilation, dilation=dilation, bias=False)

#         # Decoder with a fully convolutional layer
#         self.decoder = nn.Sequential(
#             nn.Conv2d(512, 256, kernel_size=3, padding=1),
#             nn.BatchNorm2d(256),
#             nn.ReLU(inplace=True),
#             nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),

#             nn.Conv2d(256, n_classes, kernel_size=3, padding=1),
#             nn.BatchNorm2d(n_classes),
#             nn.ReLU(inplace=True),
#             nn.Upsample(scale_factor=16, mode='bilinear', align_corners=True)
#         )



#     def forward(self, img):
#         x = self.features(img)  # Extract features from ResNet-18
#         x = self.dropout(x)  # Apply dropout
#         x = self.decoder(x)  # Decode the features using the fully convolutional layers
#         return x

# This is the Current Best Model!
class MyModel(nn.Module):
    def __init__(self, n_classes):
        super(MyModel, self).__init__()

        # Load the pre-trained ResNet-18 model
        resnet = models.resnet18(pretrained=True)
        
        # Remove the last two layers (global average pooling and fully connected layers)
        self.features = nn.Sequential(*list(resnet.children())[:-2])

        #Modify the ResNet-18 architecture to include dilated convolutions,it turns out that the dilation only makes it worse
        # dilation = 4
        # self.features[7][1].conv1 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=dilation, dilation=dilation, bias=False)
        # self.features[7][1].conv2 = nn.Conv2d(512, 512, kernel_size=3, padding=dilation, dilation=dilation, bias=False)

        # Add a Dropout layer
        self.dropout = nn.Dropout(p=0.5)

        # Decoder with an additional convolutional layer and batch normalization
        self.decoder = nn.Sequential(
            nn.Conv2d(512, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),

            nn.Conv2d(256, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True),

            nn.Conv2d(128, n_classes, kernel_size=3, padding=1),
            nn.BatchNorm2d(n_classes),
            nn.ReLU(inplace=True),
            nn.Upsample(scale_factor=8, mode='bilinear', align_corners=True)
        )



    def forward(self, img):
        x = self.features(img)  # Apply the CNN layer before ResNet-18
        x = self.dropout(x)  # Apply dropout
        x = self.decoder(x)  # Decode the features using the fully convolutional layers with batch normalization
        return x



# class MyModel(nn.Module):
#     def __init__(self, n_classes):
#         super(MyModel, self).__init__()

#         # Load the pre-trained ResNet-18 model
#         resnet = models.resnet18(pretrained=True)
        
#         # Remove the last two layers (global average pooling and fully connected layers)
#         self.features = nn.Sequential(*list(resnet.children())[:-2])

#         #Modify the ResNet-18 architecture to include dilated convolutions,it turns out that the dilation only makes it worse
#         dilation = 4
#         self.features[7][1].conv1 = nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=dilation, dilation=dilation, bias=False)
#         self.features[7][1].conv2 = nn.Conv2d(512, 512, kernel_size=3, padding=dilation, dilation=dilation, bias=False)

#         # Add a Dropout layer
#         self.dropout = nn.Dropout(p=0.5)

#         # Decoder with an additional convolutional layer and batch normalization
#         self.decoder = nn.Sequential(
#             nn.Upsample(scale_factor=32, mode='bilinear', align_corners=True)
#         )



#     def forward(self, img):
#         x = self.features(img)  # Apply the CNN layer before ResNet-18
#         x = self.dropout(x)  # Apply dropout
#         x = self.decoder(x)  # Decode the features using the fully convolutional layers with batch normalization
#         return x


# Implementing DeeplabV3+, BUT TBH it is not helpful.
# class ASPP(nn.Module):
#     def __init__(self, dim_in, dim_out,rate = 1, bn_mom = 0.1):
#         super(ASPP, self).__init__()
#         self.branch1 = nn.Sequential(
#             nn.Conv2d(dim_in,dim_out,1,1,padding=0,dilation=rate,bias=True),
#             nn.BatchNorm2d(dim_out,momentum = bn_mom),
#             nn.ReLU(inplace=True)
#         )
#         self.branch2 = nn.Sequential(
#             nn.Conv2d(dim_in,dim_out,3,1,padding=6*rate,dilation=6*rate,bias=True),
#             nn.BatchNorm2d(dim_out,momentum = bn_mom),
#             nn.ReLU(inplace=True)
#         )
#         self.branch3 = nn.Sequential(
#             nn.Conv2d(dim_in,dim_out,3,1,padding=12*rate,dilation=12*rate,bias=True),
#             nn.BatchNorm2d(dim_out,momentum = bn_mom),
#             nn.ReLU(inplace=True)
#         )
#         self.branch4 = nn.Sequential(
#             nn.Conv2d(dim_in,dim_out,3,1,padding=18*rate,dilation=18*rate,bias=True),
#             nn.BatchNorm2d(dim_out,momentum = bn_mom),
#             nn.ReLU(inplace=True)
#         )
#         self.branch5_conv = nn.Conv2d(dim_in,dim_out,1,1,0,bias=True)
#         self.branch5_bn = nn.BatchNorm2d(dim_out,momentum=bn_mom)
#         self.branch5_relu = nn.ReLU(inplace=True)
#         self.conv_cat = nn.Sequential(
#             nn.Conv2d(dim_out*5,dim_out,1,1,padding=0,bias=True),
#             nn.BatchNorm2d(dim_out,momentum = bn_mom),
#             nn.ReLU(inplace=True)
#         )

#     def forward(self, x):
#       b, c, row, col = x.shape
#       conv1x1 = self.branch1(x)
#       conv3x3_1 = self.branch2(x)
#       conv3x3_2 = self.branch3(x)
#       conv3x3_3 = self.branch4(x)
#       global_feature = torch.mean(x,2,True)
#       global_feature = torch.mean(global_feature,3,True)
#       global_feature = self.branch5_conv(global_feature)
#       global_feature = self.branch5_bn(global_feature)
#       global_feature = self.branch5_relu(global_feature)
#       global_feature = F.interpolate(global_feature, (row, col), None, 'bilinear', True)
      
#       feature_cat = torch.cat([conv1x1, conv3x3_1, conv3x3_2, conv3x3_3, global_feature], dim=1)
#       result = self.conv_cat(feature_cat)
#       return result



# class MyModel(nn.Module):
#     def __init__(self, n_classes):
#         super(MyModel, self).__init__()

#         # Load the pre-trained ResNet-18 model
#         self.resnet18 = nn.Sequential(*list(resnet18.children())[:-2])
#         self.aspp = ASPP(dim_in=512, dim_out=256, rate=1)
        
#         #----------------------------------#
#         #   浅层特征边
#         #----------------------------------#
#         self.shortcut_conv = nn.Sequential(
#             nn.Conv2d(64, 48, 1),
#             nn.BatchNorm2d(48),
#             nn.ReLU(inplace=True)
#         )		

#         self.cat_conv = nn.Sequential(
#             nn.Conv2d(48+256, 256, 3, stride=1, padding=1),
#             nn.BatchNorm2d(256),
#             nn.ReLU(inplace=True),
#             nn.Dropout(0.5),

#             nn.Conv2d(256, 256, 3, stride=1, padding=1),
#             nn.BatchNorm2d(256),
#             nn.ReLU(inplace=True),

#             nn.Dropout(0.1),
#         )
#         self.cls_conv = nn.Conv2d(256, n_classes, 1, stride=1)

#     def forward(self, img):
#       low = self.resnet18[:3](img)
#       x = self.resnet18[3:](low)
#       x = self.aspp(x)
#       low = self.shortcut_conv(low)
#       x = F.interpolate(x,size=(112,112),mode='bilinear',align_corners=True)
#       x = self.cat_conv(torch.cat((x,low),dim=1))
#       x = self.cls_conv(x)
#       x = F.interpolate(x,size=(224,224),mode='bilinear',align_corners=True)
#       return x

##########
#TODO: define your loss function here, we provide the basic Cross Entropy Loss
##########
class MyCriterion(nn.Module):
    def __init__(self):
        super(MyCriterion, self).__init__()
        self.criterion = nn.CrossEntropyLoss(reduction='mean')

    def forward(self, prediction, target):
        return self.criterion(prediction, target.squeeze(1))

########################################################################
# No need to modify below
# Evaluate sementic segmentation
# 1. Average precision of all classes and the average
# 2. Mean IOU of all classes and the average


import numpy as np
from sklearn.metrics import confusion_matrix


def segmentation_eval(gts, preds, classes):
    """
    @param    gts               numpy.ndarray   ground truth labels
    @param    preds             numpy.ndarray   predicted labels
    @param    classes           string          class names
    """
    ious, counts = compute_confusion_matrix(gts, preds)
    aps = compute_ap(gts, preds)
    for i in range(len(classes)):
        print('{:>20s}: AP: {:0.2f}, IoU: {:0.2f}'.format(classes[i], aps[i], ious[i]))
    print('{:>20s}: AP: {:0.2f}, IoU: {:0.2f}'.format('mean', np.mean(aps), np.mean(ious)))
    return aps, ious


def compute_ap(gts, preds):
    aps = []
    for i in range(preds.shape[1]):
        ap, prec, rec = calc_pr(gts == i, preds[:, i:i + 1, :, :])
        aps.append(ap)
    return aps


def calc_pr(gt, out, wt=None):
    gt = gt.astype(np.float64).reshape((-1, 1))
    out = out.astype(np.float64).reshape((-1, 1))

    tog = np.concatenate([gt, out], axis=1) * 1.
    ind = np.argsort(tog[:, 1], axis=0)[::-1]
    tog = tog[ind, :]
    cumsumsortgt = np.cumsum(tog[:, 0])
    cumsumsortwt = np.cumsum(tog[:, 0] - tog[:, 0] + 1)
    prec = cumsumsortgt / cumsumsortwt
    rec = cumsumsortgt / np.sum(tog[:, 0])
    ap = voc_ap(rec, prec)
    return ap, rec, prec


def voc_ap(rec, prec):
    rec = rec.reshape((-1, 1))
    prec = prec.reshape((-1, 1))
    z = np.zeros((1, 1))
    o = np.ones((1, 1))
    mrec = np.vstack((z, rec, o))
    mpre = np.vstack((z, prec, z))

    mpre = np.maximum.accumulate(mpre[::-1])[::-1]
    I = np.where(mrec[1:] != mrec[0:-1])[0] + 1
    ap = np.sum((mrec[I] - mrec[I - 1]) * mpre[I])
    return ap


def compute_confusion_matrix(gts, preds):
    preds_cls = np.argmax(preds, 1)
    gts = gts[:, 0, :, :]
    conf = confusion_matrix(gts.ravel(), preds_cls.ravel())
    inter = np.diag(conf)
    union = np.sum(conf, 0) + np.sum(conf, 1) - np.diag(conf)
    union = np.maximum(union, 1)
    return inter / union, conf


def val(model, val_dataloader, device):
    preds, gts = [], []

    # Put model in evaluation mode.
    model.eval()
    for i, batch in enumerate(val_dataloader):
        img, gt = batch
        img = img.to(device)
        gt = gt.to(device).long()
        pred = model(img)
        pred = torch.softmax(pred, 1)
        preds.append(pred.detach().cpu().numpy())
        gts.append(gt.detach().cpu().numpy())
    gts = np.concatenate(gts, 0)
    preds = np.concatenate(preds, 0)
    aps, ious = segmentation_eval(gts, preds, val_dataset.classes)
 
    # Put model back in training mode
    model.train()
    return preds,aps,ious

# def val(model, val_dataloader, device):
#     preds, gts = [], []

#     # Put model in evaluation mode.
#     model.eval()
#     for i, batch in enumerate(val_dataloader):
#         img, gt = batch
#         img = img.to(device)
#         gt = gt.to(device).long()
#         pred = model(img)
#         pred = torch.softmax(pred, 1)
#         preds.append(pred.detach().cpu().numpy())
#         gts.append(gt.detach().cpu().numpy())
#     gts = np.concatenate(gts, 0)
#     preds = np.concatenate(preds, 0)
#     aps, ious = segmentation_eval(gts, preds, val_dataset.classes)
 
#     # Put model back in training mode
#     model.train()
#     return preds

# TODO: implement your train loop here, we provide a very basic training loop
from torch.optim.lr_scheduler import StepLR

def train(model, criterion, optimizer, train_dataloader, val_dataloader, device, epochs):
    # Initialize the learning rate scheduler
    scheduler = StepLR(optimizer, step_size=10, gamma=0.1)

    best_val_loss = float('inf')
    
    for epoch in tqdm(range(num_epochs)):
        model.train()
        running_loss = 0.0
        for i, batch in enumerate(train_dataloader):
            optimizer.zero_grad()
            img, gt = batch
            img = img.to(device)
            gt = gt.to(device).long()
            pred = model(img)
            loss = criterion(pred, gt)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            running_loss += loss.item()
        # Update the learning rate using the scheduler
        scheduler.step()

        # Calculate and print the average training loss for the epoch
        epoch_loss = running_loss / len(train_dataloader)
        print(f"Epoch {epoch+1}, Loss: {epoch_loss:.4f}")

        # Evaluate the model on the validation set every few epochs or after the last epoch
        if (epoch+1) % 10 == 0 or epoch == num_epochs - 1:
            preds, aps, ious = val(model, val_dataloader, device)
            print('This is validation during the train')
            print(f"Epoch {epoch+1}, AP: {aps}, IoU: {ious}")

            
    return preds,aps,ious




# def train(model, criterion, optimizer, train_dataloader, epoch, **kwargs):
#     model.train()
#     for i, batch in enumerate(train_dataloader):
#         # Zero out gradient blobs in the optimizer
#         optimizer.zero_grad()
#         img, gt = batch

#         # Move data to device for training
#         img = img.to(device)
#         gt = gt.to(device).long()

#         # Get model predictions
#         pred = model(img)
#         loss = criterion(pred, gt)
#         loss.backward()

#         # Take a step to update network parameters.
#         optimizer.step()

# TODO: Implement your training cycles, make sure you evaluate on validation 
# dataset and compute evaluation metrics every so often. 
# You may also want to save models that perform well.
# Tune your own optimizer and number of epochs, learning rate, etc
from tqdm import tqdm


model = MyModel(n_classes=len(train_dataset.classes)).to(device)
print(model)
criterion = MyCriterion().to(device)
optimizer = optim.Adam(model.parameters(), lr=1e-4)
train_dataloader = data.DataLoader(train_dataset, batch_size=32, 
                                    shuffle=True, num_workers=2, 
                                    drop_last=True)

val_dataset = SegmentationDataset(split="val")
val_dataloader = data.DataLoader(val_dataset, batch_size=1, 
                                 shuffle=False, num_workers=0, 
                                 drop_last=False)
num_epochs = 20
preds,aps,ious = train(model, criterion, optimizer, train_dataloader,val_dataloader,'cuda',epochs=num_epochs)






# model = MyModel(n_classes=len(train_dataset.classes)).to(device)
# criterion = MyCriterion().to(device)
# #lr = 1e-4 is the best
# optimizer = optim.Adam(model.parameters(), lr=1e-4)
# train_dataloader = data.DataLoader(train_dataset, batch_size=32, 
#                                     shuffle=True, num_workers=2, 
#                                     drop_last=True)

# val_dataset = SegmentationDataset(split="val")
# val_dataloader = data.DataLoader(val_dataset, batch_size=1, 
#                                  shuffle=False, num_workers=0, 
#                                  drop_last=False)
# num_epochs = 20
# for epoch in tqdm(range(num_epochs)):
#     train(model, criterion, optimizer, train_dataloader, epoch)
#     # consider reducing learning rate
    
#     # test results on validation set
#     if epoch % 10 ==0 or epoch == num_epochs-1:
#         print("epoch: {}, performance on validation set".format(epoch))
#         preds = val(model, val_dataloader, device)

# visualization pred on validation set against GT
# Feel free to modify for your custom visualization
mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])
# vis input & pred on test set
fig, axs = plt.subplots(ncols=5, nrows=2, figsize=(22, 7))
for idx, ax_i in enumerate(axs.T):
    ax = ax_i[0]
    img, gt = val_dataset[idx]
    img = std * img.permute((1, 2, 0)).cpu().numpy() + mean
    ax.imshow((img * 255).astype(np.uint8))
    ax.axis('off')
    ax = ax_i[1]
    pred = np.argmax(preds[idx], 0)
    ax.imshow(pred)
    ax.axis('off')
fig.tight_layout()
plt.savefig('vis_valset.pdf', format='pdf', bbox_inches='tight')

########################################################################
# No need to modify below
# Generate predictions on test split
def predict(model, test_dataloader, device):
    preds = []
    # Put model in evaluation mode.
    model.eval()
    for i, batch in enumerate(test_dataloader):
        img, _ = batch
        img = img.to(device)
        pred = model(img)
        pred = torch.softmax(pred, 1)
        preds.append(pred.detach().cpu().numpy())
    preds = np.concatenate(preds, 0)
    # Put model back in training mode
    model.train()
    return preds

test_dataset = SegmentationDataset(split="test")
test_dataloader = data.DataLoader(test_dataset, batch_size=1, shuffle=False, num_workers=0, drop_last=False)
preds = predict(model, test_dataloader, device)

# visualization pred on test set
# Feel free to pick your favorite images for visualization
mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])
# vis input & pred on test set
fig, axs = plt.subplots(ncols=5, nrows=2, figsize=(22, 7))
for idx, ax_i in enumerate(axs.T):
    ax = ax_i[0]
    img, _ = test_dataset[idx]
    img = std * img.permute((1, 2, 0)).cpu().numpy() + mean
    ax.imshow((img * 255).astype(np.uint8))
    ax.axis('off')
    ax = ax_i[1]
    pred = np.argmax(preds[idx], 0)
    ax.imshow(pred)
    ax.axis('off')
fig.tight_layout()
plt.savefig('vis_testset.pdf', format='pdf', bbox_inches='tight')

# save prediction, please upload to Gradescope
np.save('Q2_sseg_predictions', (preds*255).astype(np.uint8))

print(list(resnet18.children()))