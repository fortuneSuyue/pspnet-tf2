import os
import time

import numpy as np
import tensorflow as tf
from PIL import Image

from pspnet import Pspnet

gpus = tf.config.experimental.list_physical_devices(device_type='GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
'''
该FPS测试不包括前处理（归一化与resize部分）、绘图的部分。
使用'img/street.jpg'图片进行测试，该测试方法参考库https://github.com/zylo117/Yet-Another-EfficientDet-Pytorch
video.py里面测试的FPS会低于该FPS，因为摄像头的读取频率有限，而且处理过程包含了前处理和绘图部分。
'''
class FPS_Pspnet(Pspnet):
    def get_FPS(self, image, test_interval):
        orininal_h = np.array(image).shape[0]
        orininal_w = np.array(image).shape[1]

        img, nw, nh = self.letterbox_image(image,(self.model_image_size[1],self.model_image_size[0]))
        img = np.asarray([np.array(img)/255])
        
        pr = np.array(self.get_pred(img)[0])
        pr = pr.argmax(axis=-1).reshape([self.model_image_size[0],self.model_image_size[1]])
        pr = pr[int((self.model_image_size[0]-nh)//2):int((self.model_image_size[0]-nh)//2+nh), int((self.model_image_size[1]-nw)//2):int((self.model_image_size[1]-nw)//2+nw)]
        
        image = Image.fromarray(np.uint8(pr)).resize((orininal_w,orininal_h), Image.NEAREST)

        t1 = time.time()
        for _ in range(test_interval):
            pr = np.array(self.get_pred(img)[0])
            pr = pr.argmax(axis=-1).reshape([self.model_image_size[0],self.model_image_size[1]])
            pr = pr[int((self.model_image_size[0]-nh)//2):int((self.model_image_size[0]-nh)//2+nh), int((self.model_image_size[1]-nw)//2):int((self.model_image_size[1]-nw)//2+nw)]
            
            image = Image.fromarray(np.uint8(pr)).resize((orininal_w,orininal_h), Image.NEAREST)

        t2 = time.time()
        tact_time = (t2 - t1) / test_interval
        return tact_time
        
pspnet = FPS_Pspnet()
test_interval = 100
img = Image.open('img/street.jpg')
tact_time = pspnet.get_FPS(img, test_interval)
print(str(tact_time) + ' seconds, ' + str(1/tact_time) + 'FPS, @batch_size 1')
