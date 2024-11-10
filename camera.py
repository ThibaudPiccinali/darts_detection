import cv2
import numpy as np
from typing import List

def open_stream(list_index : List[int]):
    cap = [0 for i in range(len(list_index))]
    j = 0
    for i in list_index:
        cap[j] = cv2.VideoCapture(i)
        if not cap[j].isOpened():
            print(f"Erreur : impossible d'ouvrir la caméra {i}")
        else:
            # Forcer la résolution à 1280x720
            cap[j].set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap[j].set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        j +=1
    return cap

def get_frame(cap):
    ret, frame = cap.read()
    # Vérifie que la frame a bien été capturée
    if not ret:
        print(f"Erreur : impossible de lire l'image de la caméra {cap}")
    return frame

def display(pixels: np.ndarray, window_name: str) -> None:
    """
    Displays the image using OpenCV's imshow function.

    Parameters:
        pixels (np.ndarray): Image data.
        window_name (str): Name of the window.
    """
    pixels = pixels.astype(np.uint8) 
    # Display the resulting image
    cv2.imshow(window_name, pixels)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Fonction pour effectuer la comparaison binaire d'images
def binary_diff_images(pixels_list_a, pixels_list_b):
    h, w, _ = pixels_list_a.shape
    # Créer une image vide pour stocker les résultats
    result = np.zeros((h, w), dtype=int)
    for i in range(len(pixels_list_a)):
        for j in range(len(pixels_list_a[0])):
                if abs(int(pixels_list_a[i][j][0]) - int(pixels_list_b[i][j][0])) > 50:
                    result[i][j] = 255
    
    return result


if __name__ == '__main__':
    cap = open_stream([1])[0]
    # display(get_frame(cap),"test")

    # Charger les images
    a = cv2.imread('image.jpg')
    b = cv2.imread('image3.jpg')

    # Vérifier que les deux images ont la même taille
    if a.shape != b.shape:
        raise ValueError("Les images doivent avoir la même taille")

    # Convertir les images en format compatible (unsigned char)
    image1 = np.array(a)
    image2 = np.array(b)
    
    # Appeler la fonction pour obtenir les différences binaires
    diff_image = binary_diff_images(image1, image2)

    # Afficher les résultats (différences en blanc)
    cv2.imshow('diff_image', diff_image.astype(np.uint8))
    diff_image = np.uint8(diff_image)
    
    kernel = np.ones((2,2),np.uint8)
    opened_image = cv2.morphologyEx(diff_image, cv2.MORPH_OPEN, kernel)
    
    cv2.imshow('erosion', opened_image.astype(np.uint8))
    
    for i in range(len(a)):
        for j in range(len(a[0])):
                if opened_image[i][j] == 255:
                    b[i][j] = [0, 0, 255]
    
    cv2.imshow('Detection', b)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()