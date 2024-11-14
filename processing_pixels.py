import cv2
import numpy as np

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

def center_of_mass(image):
    # On extrait les coordonnées des pixels à 255
    coordinates = np.argwhere(image == 255)
    
    # Calcul du centre de masse (moyenne des coordonnées)
    if len(coordinates) > 0:
        center = np.mean(coordinates, axis=0)
    else:
        center = (0, 0)
    
    return center

def filter_by_centroid(image, radius):
    # Calcul du centre de masse de l'image binaire
    center = center_of_mass(image)
    
    # Création de la nouvelle image filtrée
    filtered_image = np.zeros_like(image)
    
    # Parcours de tous les pixels de l'image
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            # Calcul de la distance au centre de masse
            distance = np.sqrt((x - center[1])**2 + (y - center[0])**2)
            
            # Si le pixel est dans le rayon et à 255, on le garde
            if distance <= radius and image[y, x] == 255:
                filtered_image[y, x] = 255

    return filtered_image

def triangulate_point(K1, K2, R1, T1, R2, T2,pts1, pts2):
    """
    Calcule la position réelle de la fléchette par triangulation.

    :param pts1: Point dans l'image de la première caméra (x, y).
    :param pts2: Point dans l'image de la deuxième caméra (x, y).
    :param K1: Matrice intrinsèque de la première caméra.
    :param K2: Matrice intrinsèque de la deuxième caméra.
    :param R1: Matrice de rotation de la première caméra.
    :param T1: Vecteur de translation de la première caméra.
    :param R2: Matrice de rotation de la deuxième caméra.
    :param T2: Vecteur de translation de la deuxième caméra.
    :return: Position 3D de la fléchette dans le monde réel (X, Y, Z).
    """
    # Convertir les points d'image en coordonnées homogènes (arrays numpy)
    pts1_hom = np.array([pts1[0], pts1[1], 1.0], dtype=np.float32)
    pts2_hom = np.array([pts2[0], pts2[1], 1.0], dtype=np.float32)

    # Obtenir les matrices de projection des caméras
    P1 = np.dot(K1, np.hstack((R1, T1)))
    P2 = np.dot(K2, np.hstack((R2, T2)))

    # Calculer la triangulation
    point_3d_hom = cv2.triangulatePoints(P1, P2, pts1_hom[:2].reshape(-1, 1), pts2_hom[:2].reshape(-1, 1))

    # Convertir les coordonnées homogènes en coordonnées 3D
    point_3d = point_3d_hom[:3] / point_3d_hom[3]

    return point_3d.flatten()
