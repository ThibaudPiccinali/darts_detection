import cv2
import math
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

def display_dart_on_board(pos_dart,radius_board,board_image):
    size_board_image = board_image.shape[0] # Suppose que l'image soit carré
    pos_dart_pixels = (pos_dart[0]*size_board_image/(radius_board*2),pos_dart[1]*size_board_image/(radius_board*2))

    point_x = int(size_board_image // 2 - pos_dart_pixels[0])
    point_y = int(size_board_image // 2 + pos_dart_pixels[1])
    
    cv2.imshow('Pointe flechette cam 1',cv2.circle(board_image, (point_x, point_y), 5, [0,0,255], -1))   
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def calculate_score(x, y):
    
    SECTORS = [11,8,16,7,19,3,17,2,15,10,6,13,4,18,1,20,5,12,9,14] # sens particulier parce repère de la cible non usuel
    RADIUS_BULLSEYE = 1.5/2
    RADIUS_OUTER_BULLSEYE = 3.2/2
    RADIUS_DOUBLE_INNER = 16
    RADIUS_DOUBLE_OUTER = 16.9
    RADIUS_TRIPLE_INNER = 9.5
    RADIUS_TRIPLE_OUTER = 10.5
    
    # Calcul de la distance au centre
    r = math.sqrt(x**2 + y**2)
    
    # Vérification des zones concentriques
    if r <= RADIUS_BULLSEYE:
        return 50  # Bullseye
    elif r <= RADIUS_OUTER_BULLSEYE:
        return 25  # Outer Bullseye
    elif r > RADIUS_DOUBLE_OUTER:
        return 0  # Hors cible
    
    # Calcul de l'angle pour déterminer le secteur
    angle = math.degrees(math.atan2(y, x))
    if angle < 0:
        angle += 360
    
    # Trouver le secteur (chaque secteur = 18°)
    sector_index = int(angle // 18)
    sector_value = SECTORS[sector_index]
    
    # Vérification des anneaux (Triple, Double)
    if RADIUS_TRIPLE_INNER <= r <= RADIUS_TRIPLE_OUTER:
        return sector_value * 3  # Triple ring
    elif RADIUS_DOUBLE_INNER <= r <= RADIUS_DOUBLE_OUTER:
        return sector_value * 2  # Double ring
    
    # Si aucune condition spéciale, retourner la valeur du secteur
    return sector_value
