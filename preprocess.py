import sys
import array

import numpy as np

from skimage.transform import resize
from skimage.io import imread, imshow, imshow_collection, show

IMG_W = 200
IMG_H = 66
IMG_D = 3

def resize_image(img):
    im = resize(img, (IMG_H, IMG_W, IMG_D))
    im_arr = im.reshape((IMG_H, IMG_W, IMG_D))
    return im_arr

if __name__ == '__main__':
        images = np.loadtxt('./input_monza3.txt', delimiter=',', dtype=str, usecols=(0,))
        values = np.loadtxt('./input_monza3.txt', delimiter=',', usecols=(1,2,3,4,5))

        print("Preparing data")

        X = []
        y = []

        y.append(values)
        print(y)

        print("Resizing...")
        for image_file in images:
                print(image_file)
                image = imread(image_file)
                vec = resize_image(image)
                X.append(vec)

        X = np.asarray(X)
        y = np.concatenate(y)
        print(y.shape)
        print(X.shape)
        np.save("data/X_m3", X)
        np.save("data/y_m3", y)
        print("Done!")
        imshow(X[0])
        show()