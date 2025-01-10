import vision as vision
import time
import cv2

cap1, cap2 = vision.open_stream([1, 0]) # Les caméras doivent être sur deux ports différents

# Necessaire parce que doit laisser le temps à la caméra de bien de setup
cam1 = vision.get_frame(cap1)
time.sleep(1) # necessaire pour avoir laisser le temps à la cam de changer (?)
cam2 = vision.get_frame(cap2)
time.sleep(1)

cv2.imshow('CAM1', cam1)
cv2.imshow('CAM2', cam2)
cv2.waitKey(0)
cv2.destroyAllWindows()