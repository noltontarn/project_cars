from train import create_model
from preprocess import resize_image
import mss
from skimage.io import imread
import os
import numpy as np
import pyvjoy
import tensorflow as tf

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)

button0 = 1
button6 = 64
button7 = 128

def TransformAxisValue(Value):
    Value *= 16384
    Value += 16384
    return Value

def check_button(output):
    if output == 0:
        button = button0
        return button
    if output == 1:
        button = button6
        return button
    if output == 2:
        button = button7
        return button

j = pyvjoy.VJoyDevice(1)

#with tf.device('cpu:0'):
print("preparing model..")
model = create_model(keep_prob=1) # no dropout
print("model created, loading weights...")
model.load_weights('model_weights.h5')
print(model.get_weights())
print("weights loaded")
sct = mss.mss()
id = 1
button = -1
while(True):
    name = "./play/" + str(id) + ".png"
    monitor = {"top": 272, "left": 570, "width": 800, "height": 600}
    output = name.format(**monitor)
    sct_img = sct.grab(monitor)
    mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
    
    img = imread(name)
    vec = resize_image(img)
    vec = np.expand_dims(vec, axis=0)
    joystick = model.predict(vec, batch_size=1)[0]
    output = [
            int(TransformAxisValue(joystick[0])),
            int(TransformAxisValue(joystick[1])),
            joystick[2],
            joystick[3],
            joystick[4],
        ]
    print(output)
    id += 1
    button = check_button(np.argmax(joystick[-3:]))
    print(button)
    j.data.lButtons = button
    j.data.wAxisX = output[0]
    j.data.wAxisY= output[1]
    #j.data.wSlider = int(TransformAxisValue(-0.8))
    #j.data.wDial = int(TransformAxisValue(-1))
    j.update()
    os.remove(name)