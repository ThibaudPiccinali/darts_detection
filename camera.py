import cv2
from typing import List

def open_stream(list_index : List[int]):
    cap = [0 for i in range(len(list_index))]
    j = 0
    for i in list_index:
        cap[j] = cv2.VideoCapture(i)
        if not cap[j].isOpened():
            print(f"Erreur : impossible d'ouvrir la caméra {i}")
        # else:
        #     # Forcer la résolution à 1280x720
        #     cap[j].set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        #     cap[j].set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        j +=1
    return cap

def get_frame(cap):
    ret, frame = cap.read()
    # Vérifie que la frame a bien été capturée
    if not ret:
        print(f"Erreur : impossible de lire l'image de la caméra {cap}")
    return frame