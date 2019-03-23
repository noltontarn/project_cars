from skimage.io import imread
from preprocess import resize_image
import mss
import numpy as np
import pyvjoy
import tensorflow as tf
import time
from skimage.transform import resize
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D
from keras import optimizers
from keras import backend as K
import pypcars2api
import random
import os
import pickle
from pynput import keyboard

game = pypcars2api.live()

crash = {
  "0" : "CRASH_DAMAGE_NONE",
  "1" : "CRASH_DAMAGE_OFFTRACK",
  "2" : "CRASH_DAMAGE_LARGE_PROP",
  "3" : "CRASH_DAMAGE_SPINNING",
  "4" : "CRASH_DAMAGE_ROLLING",
}

terrain =	{
  "0" : "TERRAIN_ROAD",
  "1" : "TERRAIN_LOW_GRIP_ROAD",
  "2" : "TERRAIN_BUMPY_ROAD1",
  "3" : "TERRAIN_BUMPY_ROAD2",
  "4" : "TERRAIN_BUMPY_ROAD3",
  "5" : "TERRAIN_MARBLES",
  "6" : "TERRAIN_GRASSY_BERMS",
  "7" : "TERRAIN_GRASS",
  "8" : "TERRAIN_GRAVEL",
  "9" : "TERRAIN_BUMPY_GRAVEL",
  "10" : "TERRAIN_RUMBLE_STRIPS",
  "11" : "TERRAIN_DRAINS",
  "12" : "TERRAIN_TYREWALLS",
  "13" : "TERRAIN_CEMENTWALLS",
  "14" : "TERRAIN_GUARDRAILS",
  "15" : "TERRAIN_SAND",
  "16" : "TERRAIN_BUMPY_SAND",
  "17" : "TERRAIN_DIRT",
  "18" : "TERRAIN_BUMPY_DIRT",
  "19" : "TERRAIN_DIRT_ROAD",
  "20" : "TERRAIN_BUMPY_DIRT_ROAD",
  "21" : "TERRAIN_PAVEMENT",
  "22" : "TERRAIN_DIRT_BANK",
  "23" : "TERRAIN_WOOD",
  "24" : "TERRAIN_DRY_VERGE",
  "25" : "TERRAIN_EXIT_RUMBLE_STRIPS",
  "26" : "TERRAIN_GRASSCRETE",
  "27" : "TERRAIN_LONG_GRASS",
  "28" : "TERRAIN_SLOPE_GRASS",
  "29" : "TERRAIN_COBBLES",
  "30" : "TERRAIN_SAND_ROAD",
  "31" : "TERRAIN_BAKED_CLAY",
  "32" : "TERRAIN_ASTROTURF",
  "33" : "TERRAIN_SNOWHALF",
  "34" : "TERRAIN_SNOWFULL"
}

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)

IMG_W = 200
IMG_H = 66
IMG_D = 3

button0 = 0
button6 = 64
button7 = 128

OUT_SHAPE = 21
INPUT_SHAPE = (IMG_H, IMG_W, IMG_D)

sct = mss.mss()

j = pyvjoy.VJoyDevice(1)

def TransformAxisValue(Value):
    Value *= 16384
    Value += 16384
    return Value

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

def forward():
    j.data.lButtons = button7
    j.data.wAxisX = 16384
    j.update()

def forwardSmallL():
    j.data.lButtons = button7
    j.data.wAxisX = 13884
    j.update()

def forwardL():
    j.data.lButtons = button7
    j.data.wAxisX = 11384
    j.update()

def forwardFullL():
    j.data.lButtons = button7
    j.data.wAxisX = 8884
    j.update()

def forwardSmallR():
    j.data.lButtons = button7
    j.data.wAxisX = 18884
    j.update()

def forwardR():
    j.data.lButtons = button7
    j.data.wAxisX = 21384
    j.update()

def forwardFullR():
    j.data.lButtons = button7
    j.data.wAxisX = 23884
    j.update()

def none():
    j.data.lButtons = button0
    j.data.wAxisX = 16384
    j.update()

def noneSmallL():
    j.data.lButtons = button0
    j.data.wAxisX = 13884
    j.update()

def noneL():
    j.data.lButtons = button0
    j.data.wAxisX = 11384
    j.update()

def noneFullL():
    j.data.lButtons = button0
    j.data.wAxisX = 8884
    j.update()

def noneSmallR():
    j.data.lButtons = button0
    j.data.wAxisX = 18884
    j.update()

def noneR():
    j.data.lButtons = button0
    j.data.wAxisX = 21384
    j.update()

def noneFullR():
    j.data.lButtons = button0
    j.data.wAxisX = 23884
    j.update()

def brake():
    j.data.lButtons = button6
    j.data.wAxisX = 16384
    j.update()

def brakeSmallL():
    j.data.lButtons = button6
    j.data.wAxisX = 13884
    j.update()

def brakeL():
    j.data.lButtons = button6
    j.data.wAxisX = 11384
    j.update()

def brakeFullL():
    j.data.lButtons = button6
    j.data.wAxisX = 8884
    j.update()

def brakeSmallR():
    j.data.lButtons = button6
    j.data.wAxisX = 18884
    j.update()

def brakeR():
    j.data.lButtons = button6
    j.data.wAxisX = 21384
    j.update()

def brakeFullR():
    j.data.lButtons = button6
    j.data.wAxisX = 23884
    j.update()

moves = 21
learningRate = 0.9
f = open('store.pckl', 'rb')
epsilon = pickle.load(f)
f.close()
epsilon_min = 0.01
epsilon_decay = 0.995
episodes = 100
#memory = []
f = open('mem.pckl', 'rb')
memory = pickle.load(f)
f.close()
max_memory = 5000

def customized_loss(y_true, y_pred, loss='euclidean'):
    # Simply a mean squared error that penalizes large joystick summed values
    if loss == 'L2':
        L2_norm_cost = 0.001
        val = K.mean(K.square((y_pred - y_true)), axis=-1) \
                    + K.sum(K.square(y_pred), axis=-1)/2 * L2_norm_cost
    # euclidean distance loss
    elif loss == 'euclidean':
        val = K.sqrt(K.sum(K.square(y_pred-y_true), axis=-1))
    return val

def on_press(key):
    if key == keyboard.Key.f10:
        return False

model = Sequential()

    # NVIDIA's model
model.add(Conv2D(24, kernel_size=(5, 5), strides=(2, 2), activation='relu', input_shape= INPUT_SHAPE))
model.add(Conv2D(36, kernel_size=(5, 5), strides=(2, 2), activation='relu'))
model.add(Conv2D(48, kernel_size=(5, 5), strides=(2, 2), activation='relu'))
model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
model.add(Flatten())
model.add(Dense(1164, activation='relu'))
drop_out = 0
model.add(Dropout(drop_out))
model.add(Dense(100, activation='relu'))
model.add(Dropout(drop_out))
model.add(Dense(50, activation='relu'))
model.add(Dropout(drop_out))
model.add(Dense(10, activation='relu'))
model.add(Dropout(drop_out))
model.add(Dense(OUT_SHAPE, activation='softsign'))

model.compile(loss=customized_loss, optimizer=optimizers.adam())

print("loding weights")
model.load_weights('reinforce_weights.h5')

for i in range(episodes):
    print(epsilon)

    with keyboard.Listener(on_press=on_press) as listener:
        while(True):
            print('still running...')
            time.sleep(1)
            if not listener.running:
                break

    print("starting episode: " + str(i))
    input_img = capture()
    reward = 0
    crashState = 0
    preDistance = 0
    while crashState == 0:
        if np.random.rand() <= epsilon:
            action = np.random.randint(0, moves, size=1)[0]
            print("random")
        else:
            output = model.predict(input_img)
            action = np.argmax(output[0])
            print("predict")
        if int(action) == 0:
            forward()
            print("forward")
        elif int(action) == 1:
            forwardSmallL()
            print("forwardSmallL")
        elif int(action) == 2:
            forwardL()
            print("forwardL")
        elif int(action) == 3:
            forwardFullL()
            print("forwardFullL")
        elif int(action) == 4:
            forwardSmallR()
            print("forwardSmallR")
        elif int(action) == 5:
            forwardR()
            print("forwardR")
        elif int(action) == 6:
            forwardFullR()
            print("forwardFullR")
        elif int(action) == 7:
            none()
            print("none")
        elif int(action) == 8:
            noneSmallL()
            print("noneSmallL")
        elif int(action) == 9:
            noneL()
            print("noneL")
        elif int(action) == 10:
            noneFullL()
            print("noneFullL")
        elif int(action) == 11:
            noneSmallR()
            print("noneSmallR")
        elif int(action) == 12:
            noneR()
            print("noneR")
        elif int(action) == 13:
            noneFullR()
            print("noneFullR")
        elif int(action) == 14:
            brake()
            print("brake")
        elif int(action) == 15:
            brakeSmallL()
            print(" brakeSmallL")
        elif int(action) == 16:
            brakeL()
            print("brakeL")
        elif int(action) == 17:
            brakeFullL()
            print("brakeFullL")
        elif int(action) == 18:
            brakeSmallR()
            print("brakeSmallR")
        elif int(action) == 19:
            brakeR()
            print("brakeR")
        else:
           brakeFullR()
           print("brakeFullR")
        
        input_next_img = capture()
        FL = game.mTerrain[0]
        FR = game.mTerrain[1]
        RL = game.mTerrain[2]
        RR = game.mTerrain[3]
        if FL != 0:
            reward -= 0.1
        if FR != 0:
            reward -= 0.1
        if RL != 0:
            reward -= 0.1
        if RR != 0:
            reward -= 0.1
        if FL == 0 and FR == 0 and RL == 0 and RR == 0:
            reward += 0.01
        curDistance = game.mParticipantInfo[0].mCurrentLapDistance
        if curDistance - preDistance > 0:
            reward += 0.1
        else:
            reward -= 0.2
        crashState = game.mCrashState

        if len(memory) >= max_memory:
            del memory[0]
        
        memory.append((input_img, action, reward, input_next_img, crashState))
        preDistance = curDistance
        input_img = input_next_img

        if crashState != 0:
            j.data.lButtons = button0
            j.data.wAxisX = 16384
            j.update()
            print("end episode: reward = " + str(reward))
    
    if len(memory) > 512:
        batch_size = 512
    else:
        batch_size = len(memory)
    
    batch = random.sample(memory, batch_size)

    for input_img, action, reward, input_next_img, crashState in batch:
        target_reward = reward
        if crashState == 0:
            target_reward = reward + learningRate * np.amax(model.predict(input_next_img)[0])
        desired_target = model.predict(input_img)
        desired_target[0][action] = target_reward
        model.fit(input_img, desired_target, epochs=1, verbose=0)
        model.save_weights('reinforce_weights.h5')

    if epsilon > epsilon_min:
        epsilon *= epsilon_decay

    f = open('store.pckl', 'wb')
    pickle.dump(epsilon, f)
    f.close()

    f = open('mem.pckl', 'wb')
    pickle.dump(memory, f)
    f.close()

    