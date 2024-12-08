import time
import cv2

import utils as utils
import vision as vision
import objet as obj

# ###### Activation des caméras ######

cap1, cap2 = vision.open_stream([0, 1]) # Les caméras doivent être sur deux ports différents

# Necessaire parce que doit laisser le temps à la caméra de bien de setup
cam1 = vision.get_frame(cap1)
time.sleep(1) # necessaire pour avoir laisser le temps à la cam de changer (?)
cam2 = vision.get_frame(cap2)
time.sleep(1)

cv2.imshow('CAM1', cam1)
cv2.imshow('CAM2', cam2)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Création des joueurs
liste_joueurs = [obj.Player(1,"Thibaud"),obj.Player(2,"Cyril"),obj.Player(3,"Alexis"),obj.Player(4,"Clément")]

# Setup utilisé
cible = obj.Dartboard()
board_image = cv2.imread('cible_template.jpg')

partie = obj.Game(liste_joueurs)

exit = 1

while exit != -1:
    exit = partie.next_turn(cap1,cap2,cible)
