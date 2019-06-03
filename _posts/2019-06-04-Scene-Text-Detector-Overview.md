---
layout: post
title: 文本检测器论文入门导读 --- Scene Text Detector Overview
date: 2019-06-04
categories: techcode
tags: [TECH, PapersIntro]
description: Scene-Text-Detector-Overview
---

最近开始进行文本检测器的算法探索，以下是这些天总结的一些内容，我的想法是提供给大家一个入门时快速浏览、理解和记忆主流文本检测器设计思路的框架，希望能作为入门导读的一个材料供大家使用。由于一开始的目的是看 Pixel-anchor，所以其他算法的设计图没有附上，以后有机会再一一补充吧。本文持续更新，也希望各位赐教。


# Overview

**Thoughts from**  
[pixel_anchor详细介绍](https://zhuanlan.zhihu.com/p/51977978)

**Reference Source**  
[OCR技术简介](https://zhuanlan.zhihu.com/p/45376274)
[深度学习 OCR Overview ](http://xiaofengshi.com/2019/01/05/%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0-OCR_Overview/)


**SOTA：（2019.05.27）** 

目前在 ICDAR15-17上前三的算法是：
- FOTS (+recognition)
- Pixel-Anchor
- PSEnet

在只考虑 precision, recall, Fscore 的情况下，FOTS 的准确度最高，PSEnet的召回性能更好，Pixel-Anchor的较均衡


**文本检测四类错误**

- Miss：遗漏了一些文本区域；
- False：将一些非文本区域错误地视为文本区域；
- Split：错误地将整个文本区域拆分为多个单独的部分；
- Merge ：错误地将几个独立的文本区域合并在一起

&nbsp;

# Methods Summary

论文思路上我大致归类为以下三大类，第一类是 Anchor-based methodm，走的路子是跟目标检测相似，只是适当地更新一些在文本检测场景下有意义的改进，最典型的就是textboxes在算法上的更新了。第二类是 Pixel-based method，走的是图像分割的思路。根据不同文本检测数据的特性和任务设计不同的损失，又会形成不同的方法，这种方法也是目前最流行的思路，因为 anchor-based method 本身存在的问题，比如长文本检测困难等，不抛弃ahchor设定是没有办法解决的，当然，目前 anchor-free 的一些方法也会是文本检测的新思路和方向。第三类是 fusion 的方式，其实就是结合上述两种方法，试图找出最佳候选框。

文本检测器设计思路上还有另一种分法，就是按照文本检测的任务不同而划分，具体来说大致可分：
- 长条形文本（行状文本）
- 曲线文本（弯曲走向的文本，常见于商标、标志等场景）
- 不规则文本（艺术设计的扭曲字体，跟图案混为一体的文字等）

但是个人认为这样的分类方式并不能很好的反映目前学界和业界在这方面的发展潮流和思路，也不能很好地表达文本检测器的设计原则。所以权衡再三我还是觉得入门时阅读论文应该按设计思路为框架去浏览文章。

下面我列一些各方向上比较经典的文章，以供各位作参考或指引。

&nbsp;

## Pixel based （segmentation） 

Drawback: recall 低， 小目标检测效果很差

- direct regression: 
直接回归五个通道，分别对应 xywh + 角度

  - **EAST**
A pipeline，Unet as backbone + feature fusion to a scale + [cls_loss + (IOU_loss + theta_loss)] 【tricks：训练时用ratio=0.3 内缩gtbox，缓和文本重叠和粘连带来的检测不准确；cls_loss 时 weighted-CEloss, 权重设置与overlap相关】

  - **AdvanceEAST**
EAST 上改进长文本检测不佳的情况：主要改进在loss设计部分，after feature fusion to a scale 之后，输出部分从原来的 F_score 和 F_geometry 接 [cls_loss + (IOU_loss + theta_loss)] 改为 [ inner_cls + edge_cls + front_end_cls + (IOU_loss + https://zhuanlan.zhihu.com/p/45376274theta_loss) ]

  - **PSEnet**
Unet as backbone + feature fusion + FPN + [origin_scale_dice_loss + ith_scale_dice_loss] 
【tricks：训练时根据FPN缩放程度设定对应内缩ratio，达到多级学习将detection box从最中心处外扩出去的目的，针对不规则字体做的设计】 



- linked regression:
回归连接关系的方法，以下面两个算法为经典。
  - [**Seglink**](https://www.cnblogs.com/lillylin/p/6596731.html) 
只对水平方向左右相邻的做连接（link），意思就是在输出通道上设置两个通道，分别对应左链接和右连接操作，数值1为连接，0为非连接。另一个点是，做连接的对象在文中被称为"segmentation"，其实就是一个 bounding box，而不是 feature map 上的一个pixel。

  - [**pixel-link**](https://zhuanlan.zhihu.com/p/38171172)
由 Seglink 这个思路改进而来的 pixel-link 看上去更有道理，与上面描述相对的，可以认为 pixel-link 相对 seglink 有两个主要改进，第一个就是舍弃了使用 segmentation 而是采用 pixel 作为连接对象。第二个就是除了左右连接外，将一个 pixel 邻域的8个 pixel 都做连接回归。这样产生出来的结果当然更具说服力，理论上也更鲁棒，而且不需要引入旋转 bbox 等操作去检测非水平框了。
当然，个人认为，实际上这个算法在使用中最大的问题是，超参引入太多了，而且这些超参对结果的影响还很大，包括连接关系置信度、最小/最大文本区域等，一旦代码写得不完备，超参调整就是个噩梦。

&nbsp;

## Anchor based  

Drawback: precision 低，受anchor设计影响严重 （semi-object detector）

[TextBoxes与TextBoxes++对比](https://www.jianshu.com/p/113ef1362676)

- **textboxes**
SSD在文本检测上的改进版，在SSD上只做以下修改 【理论上只做单字检测，且只能出水平矩形框】

  - 3\*3 卷积核改成 1\*5 卷积核，为水平长条形状的文本服务
  - default anchor box 改为 1:1 和 1:5
  - default anchor ratio 改为 2,5,7,10
  - 为避免细长水平框导致竖直方向覆盖不够，在原grid point的垂直方向中间再加一个grid point

- **DMPnet / RRPN**: 
rotate anchor boxes as post process 【简单理解就是在回归部分不使用 xywh+旋转角的方式回归，而是回归四边形框的四个角共八个数值 】

- **textboxes++**
为解决textboxes无法检测旋转文本进行了改进：

  - 1\*5 卷积核改成 3\*5 卷积核，输出作为 textbox layer为后续出文本框服务
  - default anchor ratio 改为对称形态 1,2,3,5,1/2,1/3,1/5
  - 网络输出分成两个部分，水平框出来后与 default_box 匹配（default_box由gtbox转换而来的水平矩形框），然后学习default_box到gtbox的8个offsets

&nbsp;

## Fusion

- [**FOTS**](https://blog.csdn.net/u013063099/article/details/89236368): 优势在于检测识别联合训练，撇除识别，速度效果不算惊艳，检测性能上不到前三（recognition branch对检测的指导性至少3个点）
       
  - detector branch：shared Conv [ResNet50+UNet] -->  EAST【改进了EAST的feature fusion部分，但是没有采用AdvancedEAST的出框机制】
  - recognition branch：shared Conv [ResNet50+UNet] --> ROIRotate 【仿射变换将字条拉平直】 --> text recognition 【VGG-block+LSTM+CTC】
损失函数是 Loss = loss_dect + loss_reg


- **Pixel-Anchor**
  - Pixel-based branch: 
【EAST + ASPP in 1/16】 as feature fusion module --> 
【cls_loss + (IOU_loss+theta_loss)】+ 【attention-heatmap (无R版cls_loss，不算入损失函数)】
  - Anchor-based branch: SSD-like fork 【1/32, 1/64, 1/64 w atrous, 1/64 w atrous】，四分支做 APL 【adaptive prediction layer，卷积按anchor box匹配】，外加 pixel-based-attention-heatmap，5种feature maps concatenate 后回归【8-xy-offset+confidence】
  - some tricks:
    - OHEM 除1:1正负样本
    - extra-grid-point 参考 textboxes
    - anchor truncate 【in anchor-based APL, truncate amount of conv kernel settings】
    - 级联 NMS 【由于非水平框NMS很耗时，第一步先用 水平矩形框（default-box in textboxes++）做普通NMS，再用 shaply-NMS】
![图一](/img/2019-06-03-Scene-Text-Detector-Overview/pixel_anchor_1.PNG)
![图二](/img/2019-06-03-Scene-Text-Detector-Overview/pixel_anchor_2.PNG)
![图三](/img/2019-06-03-Scene-Text-Detector-Overview/pixel_anchor_3.PNG)



