from train import create_model
from preprocess import resize_image
import mss
from skimage.io import imread
import os
import numpy as np
import pyvjoy
import tensorflow as tf
import pypcars2api
import time
from pynput import keyboard

game = pypcars2api.live()

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)

button0 = 1
button6 = 64
button7 = 128

def on_press(key):
    if key == keyboard.Key.f10:
        return False

def TransformAxisValue(Value):
    Value *= 16384
    Value += 16384
    return Value

def check_button(output, x):
    speed = round(game.mSpeed, 1)
    FL = game.mTerrain[0]
    FR = game.mTerrain[1]
    if output == 0:
        button = button0
        return button
    if output == 1:
        if speed < 65*0.447:
            button = 0
        else:
            button = button6
        return button
    if output == 2:
        if speed > 60*0.447 and (x < 11500 or x > 19000):
            button = 0
        elif speed > 80*0.447:
            button = 0
        else:
            button = button7
        return button

def check_x(x, Lfirst, Rfirst, state, count):
    FL = game.mTerrain[0]
    FR = game.mTerrain[1]
    RL = game.mTerrain[2]
    RR = game.mTerrain[3]
    sector = game.mParticipantInfo[0].mCurrentSector
    print(sector)
    if sector == 0 and x > 19000:
        x -= 1000
    if sector == 1 and x > 21000:
        x += 500
    if FL != 0:
        if Rfirst == False:
            Lfirst = True
            print("too much left")
            x += 2000
            if FR != 0:
                state = "outL"
                count = 4
                if x < 20000:
                    x = 21000
                else:
                    x += 3500
    if FR != 0:
        if Lfirst == False:
            Rfirst = True 
            print("too much right")
            x -= 500
            if FL != 0 and RR != 0 and sector != 1:
                x -= 2500
            '''
            if FL != 0:
                state = "outR"
                count = 3
                if x > 15000:
                    x = 8000
                else:
                    x -= 5000
            '''
    if FL == 0 and FR == 0 and RL == 0 and RR == 0:
        Rfirst = False
        Lfirst = False

    if FL == 0 and FR == 0 and count > 0:
        if state == "outL":
            if x > 17000:
                x = 10000
            elif x < 12000 and x > 9000:
                x -= 0
            else:
                x -= 9000
            count -= 1
        if state == "outR":
            if x < 15000:
                x = 20000
            elif x > 17000 and x < 21000:
                x -= 0
            else:
                x += 6000
            count -= 1
        if count == 0:
            state = "none"
    return x, Lfirst, Rfirst, state, count


j = pyvjoy.VJoyDevice(1)

Lfirst = False
Rfirst = False

#with tf.device('cpu:0'):
print("preparing model..")
model = create_model(keep_prob=1) # no dropout
print("model created, loading weights...")
#model.load_weights('CNN+reinforce_weights.h5')
model.load_weights('CNN_half_weights.h5')
#model.load_weights('CNN_half_monza_weights.h5')
print(model.get_weights())
print("weights loaded")
sct = mss.mss()
id = 1
button = -1
state = "none"
count = 0
with keyboard.Listener(on_press=on_press) as listener:
        while(True):
            print('press F10 to start')
            time.sleep(1)
            if not listener.running:
                break
while(True):
    name = "./play/" + str(id) + ".png"
    #monitor = {"top": 272, "left": 570, "width": 800, "height": 600}
    monitor = {"top": 272, "left": 570, "width": 798, "height": 300}
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
    output[0], Lfirst, Rfirst, state, count = check_x(output[0], Lfirst, Rfirst, state, count)
    button = check_button(np.argmax(joystick[-3:]), output[0])
    print(button)
    j.data.lButtons = button
    j.data.wAxisX = output[0]
    j.data.wAxisY= output[1]
    #j.data.wSlider = int(TransformAxisValue(-0.8))
    #j.data.wDial = int(TransformAxisValue(-1))
    j.update()
    os.remove(name)