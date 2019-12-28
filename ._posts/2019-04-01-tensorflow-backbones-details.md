---
layout: post
comments : true
title: Tensorflow 复现 Backbones 时的一些细节
date: 2019-04-06
categories: techcode
tags: [TECH, tensorflow]
description: tensorflow backbones 细节
---

# Tensorflow 复现 Backbones 时的一些细节

最近工作需要做一些图像识别的项目，在github上浏览了好些tensorflow的经典算法复现，如ResNet, VGG, SEnet等，由于每位大大的代码风格不一，对TF的API使用又各有不同，实在不太好做对照实验，再者很多大佬的代码普遍由于要抢fork抢star，想要尽早复现（我猜的），普遍存在下面这些问题：

1. 没有多gpu训练（我的天啊，大佬们不用多gpu哪来的pretrained...）
2. 参数隐藏在脚本里（很多x-implement的代码都是这样，调参侠表示很不爽啊）
3. 不同模型的复现风格迥异，模型结构在代码中展现不清楚，难做比较

再者自己对照着论文和大佬的代码撸一次代码，自己也可以对模型和api有个大致理解，所以我就动手了，地址如下：
https://github.com/HoracceFeng/Image-Recognize-Tensorflow/tree/master [^0]
欢迎大家来指正，赐star赐fork当然更好啦。如果大家有什么经典模型想要看我复现一次的话，十分欢迎以下留言或者issue给我。tensorflow版本完成后会开始pytorch版本，万分感谢。


先说一下为什么用tensorflow. 其实我想过用keras，主要是因为以下这张图让我改变主意了：
图源是“机器之心”的这篇文章[^1]
同时感谢数据来源[^2]

![图一](/img/2019-04-01/graph1.jpg)
其实keras可以吐槽的东西确实很多，虽然它很方便，但是对比tensorflow和pytorch，它至少有以下问题：
1. 不方便做更进一步细小的改进
2. 训练速度慢，实例使用时间（inference time）速度也是慢
3. 玄学训练，gpu经常神经质性突然掉线
4. gpu吐槽2: 多gpu训练直接保存居然，居然，居然直接就把多gpu的图保存下来了，再运行不给同样的gpu还不行了（这个问题有解决方法，敬请留意后续更新）
5. 还有一个不负责任的观察，keras版本的模型准确率相对低一些。对比pytoch下的backbone实现，只有Inception-series的是keras略胜，其他的都比不过pytorch。而我实现的eras-tiny-yolo3（同样在我GitHub上能找到）的准确率也比darknet原版掉了5%


进入正题，
首先说说 layers, nn, contrib 这三个库的异同。nn 和 layers 都是官方实现的函数库，contrib则是第三方提交的代码。尽管contrib里实现了很多官方代码中不支持的功能，部分后来也被加入到官方库中，但实际上大部分代码仍然存在代码格式不统一，支持文档不齐全，和由于版本更新带来的不稳定的情况。由于官方最新版的 tensorflow 2.0 已经不支持 contrib 库了，所以目前的代码要支持最新版本的 TF 必须替换 contrib 函数。如果要尽量避免代码更新和维护的工作，tf.nn是最稳定的实现，也是这三个库中最底层。tf.layers则是相对更高级的API，使用这个库实现简单的深度学习模型是新手使用 tensorflow 一个比较好的选择，正如上面的例子所示，tf.layers的实现相对tf.nn可以节省很多代码。

## 1. tf.layer.conv2d与tf.nn.conv2d
先上两个函数的api：
```
tf.layers.conv2d(inputs, filters, kernel_size, strides=(1,1),
                      padding='valid', data_format='channels_last',
                　　　 dilation_rate=(1,1), activation=None,
                　　　 use_bias=True, kernel_initializer=None,
                　　　 bias_initializer=init_ops.zeros_initializer(),
                　　　 kernel_regularizer=None,
                　　　 bias_regularizer=None,
                　　　 activity_regularizer=None, trainable=True,
                　　　 name=None, reuse=None)
```
```
tf.nn.conv2d(input, filter, strides, padding, use_cudnn_on_gpu=None, data_format=None, name=None)
```

两个函数其实都是一样做卷积的，tf.layer.conv2d 是在tf.nn.conv2d上做了一系列函数的集成，具体差异是：
           - layers.conv2d集成了activate, bias, dilation等方法；而用tf.nn.conv2d则要自行添加
           - layers.conv2d已经将reuse,training参数暴露出来，方便逐层控制训练，多gpu训练，特定层权值共享等骚操作；而使用tf.nn.conv2d需要自己暴露reuse和training
           - tf.nn.conv2d相对更灵活，因为它的strides设置允许使用者在 batch 和 channel 部分执行


下面分别使用两个函数实现同样的功能：
```
x = tf.layers.conv2d(x, filter=channels, kernel_size=(kernel_h, kernel_w), strides=step, padding=’same’, activation=tf.nn.relu, bias=True,reuse=True)
```
```
def bias_variable(shape, name="biases"):
         initial = tf.constant(0.1, dtype=tf.float32, shape=shape)
         return tf.Variable(initial, name=name)
         
with tf.variable_scope(‘’, reuse=True):
         x = tf.nn.conv2d(x, filter=[batch_size, kernel_h, kernel_w, channels], strides=(1,step,step,1)), padding=’SAME’)
         b = bias_variable([channels]) 
         x = tf.nn.relu(x + b)
```


## 2. tf.layers.batch_normalization / tf.nn.batch_normalization/ tf.contrib.layers.batch_normalization
同样的，这三个函数其实实现内容都是一样的，底层api均依赖tf.nn.batch_normalization:
```
tf.nn.batch_normalize(x, mean, variance, offset, scale, variance_epsilon, name=None)
```
从底层实现能够比较容易看到 batch_normalize 层的全貌，输入为x，对输入的 tensor 进行归一处理涉及到4个参数的学习，分别是 mean, variance, offset, scale。套用官方文档中公式更清晰，
![图二](/img/2019-04-01/graph2.jpg)
至于其他两个api与这个的区别，无非是四个参数的初始化方法和decay数值，一般直接使用原来的设置就可以了。值得注意的是，部分decay的默认值是0.99，但是0.99容易造成过拟合（？），一般会更改为0.9。另外一个会使用到的选项是 training 和 reuse，
```
tf.layers.batch_normalization(.., trainable, training, reuse, name)
tf.contrib.layers.batch_norm(.., is_training, reuse, scope)
```
tf.layers.batch_normalization 中的trainable决定该参数是否可训练，通过关闭该参数可以锁死BN层的参数不更新。training参数则是一个允许使用者选择模型运行过程中是否更新BN参数的选项，实际使用时在 traning_epoch 我们会打开，在 testing_epoch 则需要关闭，避免BN层在验证测试过程中继续学习。reuse参数的使用范围很广，在本例中主要是用于实现多GPU训练，下面会再详细讲解。
tf.contrib.layers.batch_norm 中，is_training 和 上面的training参数使用方法相同，scope 则对应 name 参数。
最后再附上 stackoverflow 上大神对于各API功能的整理：
![图三](/img/2019-04-01/graph3.jpg)
     

## 3. name_scope 与 variable_scope
对于tensorflow 里面图定义的问题和变量命名的方式不太清楚的同学，建议可以先看看这篇吐槽短文[^3]
name_scope 和 variable_scope 的最大区别是，后者是专门为了解决权值共享的问题而设计的，通过 reuse 参数的控制，variable_scope 可以实现整个参数层的共享。这个功能在同一个运算图下的模型中或许没有太大作用，但却是不同运算图下的模型共享权值的方法，也是多GPU训练设置的关键。详细的使用实例可以参考[^4]

## 4. 分类模型的损失函数设置
这里我只介绍 sigmoid 和 softmax 两种常用的激活函数和他们对应的损失函数计算API（一般使用交叉墒）:
![图四](/img/2019-04-01/graph4.jpg)

- tf.nn.softmax_cross_entropy_with_logits:
       这是一般分类器中最常用的损失函数计算，主要用在==单标签多分类==问题中。在tf1.5及以下的版本中，这个api只是单纯计算损失函数，不会更新softmax到cross_entropy间的一些参数设置，在tf1.5以上的版本，则统一更新成会自动更新内部参数的形式
- tf.nn.softmax_cross_entropy_with_logits_v2:
       tf1.5及以下版本中更新内部参数的损失函数计算，在以上的版本中退化成上面的函数形式
- tf.nn.sigmoid_cross_entropy_with_logits:
       主要用于==多标签多分类==问题

从上面的公式可知，softmax函数所有类别的confidence相加为1，因此适合作为单标签分类的激活函数；而sigmoid函数则允许所有类别的confidence互不干扰地落在[0,1]之间，因此适合多标签分类。顺带一提，计算预测模型或类似的连续数分类模型，一般使用 MSE 作为损失函数。


## 5. 代码设计上具体的小细节
为了实现代码内实时的参数控制，比如前面讲到的控制BN层和其他 trainable variable 训练和停止更新用到的 training_flag，dropout层在不同情况下控制dropout比例的 keep_prob。通常做法是，我们在训练脚本中需要事实定义一个占位符或者一个变量给他们，然后在训练过程中连带数据 feed_dict 进去，如下：
```
training_flag = tf.placeholder(tf.bool)
keep_prob = tf.placeholder(tf.float32, [None])
train_feed_dict = {‘input':x, ‘training’:training_flag, ‘keep_prob’:keep_prob}
loss = sess.run([‘_loss’], feed_dict=train_feed_dict)
```
这样的代码当然能正常运行，但是如果在模型代码内部安排不当，就会造成运算图中定义点过多，从而影响运算速度，产生的模型也会记录无用变量而变得冗肿，不利于部署，以下面batch_normalization 的实现为例：
```
## solution-1
x = tf.layers.batch_normalization(inputs=x, momentum=0.9, training=argdict['train'], name='bnorm_'+str(argdict['nlayer']))

## solution-2
with arg_scope([batch_norm],
                    scope='bnorm_'+str(argdict['nlayer']),
                    updates_collections=None,
                    decay=0.9,
                    center=True,
                    scale=True,
                    zero_debias_moving_mean=True):
     x = tf.cond(argdict['train'],
                    lambda : batch_norm(inputs=x, is_training=argdict['train'], reuse=None),
                    lambda : batch_norm(inputs=x, is_training=argdict['train'], reuse=True))
```
上面两种方法均能实现 batch_normalization，但是我在自己的笔记本电脑上运行时前者速度比后者快了20%，原因很简单，因为下面的解决方法使用了 tf.cond 作为判断方法去控制，而无论你使用的是 true 状态还是 false 状态的 batch_norm，运算图在 “bnorm_num” 这一层中都会分开定义这两个节点，加上判断语句本身占用时间，在如今 backbones 几乎每一层都要做 BN 的情况下，所增加的节点和运算量自然可观。

## 6. tf_debug使用 [^5]
最后再来说说 tf.debug 这个神器。使用方法很简单，就是在session定义后加入下面两行代码：
```
from tensorflow.python import debug as tf_debug
sess = tf_debug.LocalCLIDebugWrapperSession(sess)
```
tf_debug模式在可以在命令行界面中运行，也可以使用tensorboard实现UI交互，进入界面后按s则会根据计算图中各点的顺序依次计算并返回各个tensor的运算值，十分适合大量查看tensor shape 和对应激活值。另外，由于很多时候需要使用服务器进行GPU训练，很多时候难以避免需要查看服务器上 tensorboard，这里介绍一个在利用docker实现，能快速在本机中实时查看服务器tensorboard的方法。docker镜像启动时运行：
```
sudo docker run -it —rm -p 24000:6006 docker_image_name bash
```
通过这个命令，我们将docker容器内的 tensorboard 端口6006映射到服务器端口24000上，这样我们就可以在连通服务器的任何电脑上使用浏览器浏览这个端口下的tensorboard了。


## 预告 
接下来打算更新：
1. 如何改造代码变成多gpu训练？同时部署多个tensorflow模型？如何在tensorflow中实现freeze backbone操作？以及如何把 github 上其他人的backbone抢过来改一改当作是自己训练的backbone （hehehe…）【图与变量命名的问题】
2. 激活函数，优化函数，损失函数


## Reference 
[^0]: 厚颜无耻求关注 (这周我会写完ResNet Backbone的 T_T)  <https://github.com/HoracceFeng/Image-Recognize-Tensorflow/tree/master>

[^1]: keras 与 pytorch 的34个模型复现对比 <https://mp.weixin.qq.com/s/UTkjFSha2nfnmC-cwZjSKg>

[^2]: 不同框架下的速度测试 <https://github.com/ilkarman/DeepLearningFrameworks>

[^3]: tensorflow 吐槽小短文 <https://mp.weixin.qq.com/s?__biz=MzA3MzI4MjgzMw==&mid=2650758563&idx=4&sn=5fb7f9bf8cb07329ee70bd2bfc1e3e58&chksm=871a99ddb06d10cb4e2110d94efd3150ec09e06b455a8dde99e28be7fcb7b36caf42487d54ec&mpshare=1&scene=1&srcid=&pass_ticket=SLZZoHYqWTbSV2PzTtk7g469ebzouLY2%2B664%2BJ%2FqGKE%3D#rd>

[^4]: name_scope 与 variable_scope 的实例 <https://blog.csdn.net/u012609509/article/details/80045529>

[^5]: tf_debug 官方文档 <https://www.tensorflow.org/guide/debugger?hl=zh_cn>


