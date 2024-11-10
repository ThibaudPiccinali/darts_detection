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

# Fonction pour comparer deux pixels avec une tolérance donnée
def is_close(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

# Fonction pour vérifier si les pixels de deux images sont similaires
def pixels_are_similar(a, b, t):
    return is_close(a[0], b[0], rel_tol=t) and is_close(a[1], b[1], rel_tol=t) and is_close(a[2], b[2], rel_tol=t)

# Fonction pour effectuer la comparaison binaire d'images
def binary_diff_images(a, b, y_bounds=None, t=1e-09):
    h, w, _ = a.shape
    if y_bounds is None:
        y_bounds = (0, h)

    # Créer une image vide pour stocker les résultats
    result = np.zeros((y_bounds[1] - y_bounds[0], w), dtype=int)

    # Comparer les pixels
    for y in range(y_bounds[0], y_bounds[1]):
        for x in range(0, w):
            # Si les pixels sont différents, mettre 255 (blanc) dans le résultat
            result[y - y_bounds[0], x] = 0 if pixels_are_similar(a[y, x], b[y, x], t) else 255

    return result

#### Pour la prochaine fois
# -> essayer le filtrage ci dessous en descandant la camera le plus possible (ou en remontant la cible) pour espérer avoir de meilleurs réslutats

if __name__ == '__main__':
    cap = open_stream([1])[0]
    # display(get_frame(cap),"test")

    # Charger les images
    a = cv2.imread('image_gris.png')
    b = cv2.imread('image_gris2.png')

    # Vérifier que les deux images ont la même taille
    if a.shape != b.shape:
        raise ValueError("Les images doivent avoir la même taille")

    # Convertir les images en format compatible (unsigned char)
    image1 = np.array(a, dtype=np.uint8)
    image2 = np.array(b, dtype=np.uint8)
    
    # Appeler la fonction pour obtenir les différences binaires
    y_bounds = (0, image1.shape[0])  # Comparer toute l'image
    threshold = 0.05  # Seuil de tolérance
    diff_image = binary_diff_images(image1, image2, y_bounds, threshold)

    # Afficher les résultats (différences en blanc)
    cv2.imshow('diff_image', diff_image.astype(np.uint8))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    diff_image = np.uint8(diff_image)
    
    kernel = np.ones((5,5),np.uint8)
    opening = cv2.morphologyEx(diff_image, cv2.MORPH_OPEN, kernel)
    
    cv2.imshow('opening', opening.astype(np.uint8))
    cv2.waitKey(0)
    cv2.destroyAllWindows()