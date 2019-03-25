import pyvjoy

button0 = 1
button6 = 64
button7 = 128

j = pyvjoy.VJoyDevice(1)

j.data.lButtons = 0
j.data.wAxisX = 16384
j.data.wAxisY = 16384
j.update()