from train import create_model, customized_loss
from keras import optimizers
from preprocess import resize_image
import mss
from skimage.io import imread
import os
import numpy as np
import pyvjoy
import tensorflow as tf
import pypcars2api
from pynput import keyboard
import pickle
import time
import random

game = pypcars2api.live()

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)

button0 = 1
button6 = 64
button7 = 128

def capture():
    name = "./play/" + "1" + ".png"
    monitor = {"top": 272, "left": 570, "width": 800, "height": 600}
    output = name.format(**monitor)
    sct_img = sct.grab(monitor)
    mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
    
    img = imread(name)
    vec = resize_image(img)
    vec = np.expand_dims(vec, axis=0)

    os.remove(name)
    return vec

def TransformAxisValue(Value):
    Value *= 16384
    Value += 16384
    return Value

def TransformAxisBack(Value):
    Value -= 16384
    Value /= 16384
    return Value

def check_button(output, x):
    speed = round(game.mSpeed, 1)
    if output == 0:
        button = button0
        return button
    if output == 1:
        if speed < 26.8:
            button = 0
        else:
            button = button6
        return button
    if output == 2:
        if speed > 20.12 and (x < 11500 or x > 19000):
            button = button6
        elif speed > 30.85:
            button = 0
        else:
            button = button7
        return button

def check_x(x, Lfirst, Rfirst):
    FL = game.mTerrain[0]
    FR = game.mTerrain[1]
    RL = game.mTerrain[2]
    RR = game.mTerrain[3]
    if FL != 0:
        if Rfirst == False:
            Lfirst = True
            print("too much left")
    if FR != 0:
        if Lfirst == False:
            Rfirst = True 
            print("too much right")
    if FL == 0 and FR == 0 and RL == 0 and RR == 0:
        Rfirst = False
        Lfirst = False
    
    return x, Lfirst, Rfirst

def on_press(key):
    if key == keyboard.Key.f10:
        return False

j = pyvjoy.VJoyDevice(1)

Lfirst = False
Rfirst = False

#with tf.device('cpu:0'):
print("preparing model..")
model = create_model(keep_prob=0.8) # no dropout
model.compile(loss=customized_loss, optimizer=optimizers.adam())
print("model created, loading weights...")
model.load_weights('CNN+reinforce_weights.h5')
print(model.get_weights())
print("weights loaded")
sct = mss.mss()
button = -1
memory = []
max_memory = 5
while(True):
    with keyboard.Listener(on_press=on_press) as listener:
        while(True):
            print('still running...')
            time.sleep(1)
            if not listener.running:
                break
    img = capture()
    crashState = 0
    while crashState == 0:

        joystick = model.predict(img, batch_size=1)[0]
        output = [
                int(TransformAxisValue(joystick[0])),
                int(TransformAxisValue(joystick[1])),
                joystick[2],
                joystick[3],
                joystick[4],
            ]
        print(output)
        button = check_button(np.argmax(joystick[-3:]), output[0])
        print(button)
        j.data.lButtons = button
        j.data.wAxisX = output[0]
        j.data.wAxisY= output[1]
        #j.data.wSlider = int(TransformAxisValue(-0.8))
        #j.data.wDial = int(TransformAxisValue(-1))
        j.update()
        img_next = capture()
        crashState = game.mCrashState
        output[0], Lfirst, Rfirst = check_x(output[0], Lfirst, Rfirst)
        if Lfirst == True or Rfirst == True:
            if Lfirst == True:
                reward = "L"
                print("append L")
            if Rfirst == True:
                reward = "R"
                print("append R")
            if len(memory) >= max_memory:
                del memory[0]
            action = output[0]
            print(action)
            memory.append((img, action, reward, img_next, crashState))
        
        img = img_next
        
        if crashState != 0:
            j.data.lButtons = 0
            j.data.wAxisX = 16384
            j.update()
            print("end episode")
    
    batch = random.sample(memory, 2)

    for img, action, reward, img_next, crashState in batch:
        #next_act = TransformAxisValue(model.predict(img_next)[0][0])
        #print("next" + str(next_act))
        if reward == "L":
            target_reward = action + 500
            if crashState == 0:
                target_reward = action + 300
        
        if reward == "R":
            target_reward = action - 500
            if crashState == 0:
                target_reward = action - 300

        target_reward = TransformAxisBack(target_reward)
        desired_target = model.predict(img)
        desired_target[0][0] = target_reward
        print("target" + str(desired_target[0][0]))
        model.fit(img, desired_target, epochs=1, verbose=0)
        print("fitted model")
    
    memory = []
    model.save_weights('CNN+reinforce_weights2.h5')
    #f = open('CNN+rmem.pckl', 'wb')
    #pickle.dump(memory, f)
    #f.close()