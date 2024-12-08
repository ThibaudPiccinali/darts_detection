import cv2
import glob
import time
import numpy as np

import utils as utils
import processing_pixels as pp

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

def get_intrinsix_matrix(path_images):

    # Préparer les objets 3D du monde réel (un damier avec des coins connus)
    # Points du damier dans le monde réel (coordonnées de chaque coin)
    pattern_size = (8, 6)  # Le nombre de coins dans le damier (9x6)
    square_size = 2.5  # La taille des carrés en unités arbitraires (cm)

    # Préparez les points de référence 3D, en supposant que le damier est sur le plan z=0
    obj_points = np.zeros((np.prod(pattern_size), 3), dtype=np.float32)
    obj_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    obj_points *= square_size

    # Listes pour stocker les points du monde réel et les points image
    obj_points_list = []
    img_points_list = []

    # Charger les images du damier
    images = glob.glob(path_images)  # Remplacez par le chemin vers vos images de calibration

    for image_file in images:
        # Lire l'image
        img = cv2.imread(image_file)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Trouver les coins du damier
        ret, corners = cv2.findChessboardCorners(gray, pattern_size, flags=cv2.CALIB_USE_INTRINSIC_GUESS)

        if ret:
            # Ajouter les points de l'objet et de l'image
            obj_points_list.append(obj_points)
            img_points_list.append(corners)

        else:
            print(f"Échec de détection des coins pour {image_file}")
    cv2.destroyAllWindows()

    # Calibrer la caméra pour obtenir les paramètres intrinsèques
    ret, K, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(obj_points_list, img_points_list, gray.shape[::-1], None, None)

    # K est la matrice intrinsèque
    return K


def get_coord_dart(cap1,cap2,DEBUG=False):
    ###### Capture (et mise en forme) des images ######
    # Cam 1
    base_image_cam1_colors = get_frame(cap1)
    base_image_cam1 = cv2.cvtColor(base_image_cam1_colors, cv2.COLOR_BGR2GRAY)
    # Convertir les images en format compatible (unsigned char)
    base_image_cam1 = np.array(base_image_cam1,dtype=np.uint8)
    base_image_cam1_grey = np.stack([base_image_cam1] * 3, axis=-1)

    # Cam 2
    base_image_cam2_colors = get_frame(cap2)
    base_image_cam2 = cv2.cvtColor(base_image_cam2_colors, cv2.COLOR_BGR2GRAY)
    # Convertir les images en format compatible (unsigned char)
    base_image_cam2 = np.array(base_image_cam2,dtype=np.uint8)
    base_image_cam2_grey = np.stack([base_image_cam2] * 3, axis=-1)
    
    if DEBUG:
        cv2.imshow('Image de base cam1 en niveau de gris', base_image_cam1_grey.astype(np.uint8))
        cv2.imshow('Image de base cam2 en niveau de gris', base_image_cam2_grey.astype(np.uint8))
    
    ## On attend que l'utilisateur lance la flechette
    print("Capture de l'image de référence effectuée. Lancez votre flechette puis pressez <Enter>")
    input()

    dart_image_cam1_colors = get_frame(cap1)
    dart_image_cam1 = cv2.cvtColor(dart_image_cam1_colors, cv2.COLOR_BGR2GRAY)
    # Convertir les images en format compatible (unsigned char)
    dart_image_cam1 = np.array(dart_image_cam1,dtype=np.uint8)
    dart_image_cam1_grey = np.stack([dart_image_cam1] * 3, axis=-1)

    dart_image_cam2_colors = get_frame(cap2)
    dart_image_cam2 = cv2.cvtColor(dart_image_cam2_colors, cv2.COLOR_BGR2GRAY)
    # Convertir les images en format compatible (unsigned char)
    dart_image_cam2 = np.array(dart_image_cam2,dtype=np.uint8)
    dart_image_cam2_grey = np.stack([dart_image_cam2] * 3, axis=-1)
    
    if DEBUG:
        cv2.imshow('Image cam1 avec la flechette en niveau de gris', dart_image_cam1_grey.astype(np.uint8))
        cv2.imshow('Image cam2 avec la flechette en niveau de gris', dart_image_cam2_grey.astype(np.uint8))
    
    ###### Première étape de detection (comparaison entre les deux images) ######

    # Appeler la fonction pour obtenir les différences binaires
    diff_image_cam1 = pp.binary_diff_images(base_image_cam1_grey, dart_image_cam1_grey)
    diff_image_cam2 = pp.binary_diff_images(base_image_cam2_grey, dart_image_cam2_grey)

    if DEBUG:
        # Afficher les résultats (différences en blanc)
        cv2.imshow('diff_image_cam1', diff_image_cam1.astype(np.uint8))
        cv2.imshow('diff_image_cam2', diff_image_cam2.astype(np.uint8))
    
    diff_image_cam1 = np.uint8(diff_image_cam1)
    diff_image_cam2 = np.uint8(diff_image_cam2)

    ###### Filtrage (méthode Opening) ######

    kernel = np.ones((2,2),np.uint8)

    opened_image_cam1 = cv2.morphologyEx(diff_image_cam1, cv2.MORPH_OPEN, kernel)
    opened_image_cam2 = cv2.morphologyEx(diff_image_cam2, cv2.MORPH_OPEN, kernel)
    
    if DEBUG:
        cv2.imshow('opening cam 1', opened_image_cam1.astype(np.uint8))    
        cv2.imshow('opening cam 2', opened_image_cam2.astype(np.uint8))

    ###### Filtrage (centre de masse) ######

    filtered_image_cam1 = pp.filter_by_centroid(opened_image_cam1, 170)
    filtered_image_cam2 = pp.filter_by_centroid(opened_image_cam2, 170)

    ###### Affichage final ######

    for i in range(len(base_image_cam2_colors)):
        for j in range(len(base_image_cam2_colors[0])):
            
            if filtered_image_cam1[i][j] == 255:
                dart_image_cam1_colors[i][j] = [0, 0, 255]
                
            if filtered_image_cam2[i][j] == 255:
                dart_image_cam2_colors[i][j] = [0, 0, 255]

    if DEBUG:
        cv2.imshow('Detection cam 1',dart_image_cam1_colors)    
        cv2.imshow('Detection cam 2',dart_image_cam2_colors)

    ###### Identification de la pointe de la flechette ######

    # Trouver les coordonnées des pixels blancs (255)
    points_felchette_cam1 = np.column_stack(np.where(filtered_image_cam1 == 255))
    # Trouver le point avec la plus grande coordonnée x
    lowest_point_felchette_cam1 = points_felchette_cam1[points_felchette_cam1[:, 0].argmax()]
    lowest_point_felchette_cam1 = (lowest_point_felchette_cam1[1],lowest_point_felchette_cam1[0])

    points_felchette_cam2 = np.column_stack(np.where(filtered_image_cam2 == 255))
    lowest_point_felchette_cam2 = points_felchette_cam2[points_felchette_cam2[:, 0].argmax()]
    lowest_point_felchette_cam2 = (lowest_point_felchette_cam2[1],lowest_point_felchette_cam2[0])

    if DEBUG:
        print(f"Le point le plus bas sur la caméra 1 est à la position : {lowest_point_felchette_cam1}")
        print(f"Le point le plus bas sur la caméra 2 est à la position : {lowest_point_felchette_cam2}")
        cv2.imshow('Pointe flechette cam 1',cv2.circle(dart_image_cam1_colors, (lowest_point_felchette_cam1[0], lowest_point_felchette_cam1[1]), 5, [0,255,0], -1))    
        cv2.imshow('Pointe flechette cam 2',cv2.circle(dart_image_cam2_colors, (lowest_point_felchette_cam2[0], lowest_point_felchette_cam2[1]), 5, [0,255,0], -1))

    ##### Calcul de la position réelle associée ######

    # Matrices intrinsèques des caméras
    K1 = np.array([[459.44732253,0.,339.56888157],[0.,462.62071383, 222.54341588],[0., 0., 1.]])  # Matrice de la caméra 1
    K2 = np.array([[458.80917086,0.,360.12752469],[0.,462.44782024, 194.38816358],[0., 0., 1.]])  # Matrice de la caméra 2

    # Matrices extrinsèques (Rotation et Translation)
    # Origine -> Cam1

    R1 = np.eye(3)  # Rotation de la caméra 1
    T1 = np.array([[0], [0], [0]])  # Translation de la caméra 1

    R2 = utils.rot_y(90)  # Rotation de la caméra 2
    T2 = np.array([[-30], [0], [-30]])  # Translation de la caméra 2

    # Triangulation pour obtenir les points 3D
    points_2D_felchette = pp.triangulate_point(K1, K2, R1, T1, R2, T2, np.array((lowest_point_felchette_cam1)), np.array((lowest_point_felchette_cam2)))

    R = np.eye(3)  # Rotation de la caméra 1 par rapport au centre de le cible
    T = np.array([0, 0, -30])  # Translation de la caméra 1
    points_2D_felchette_reel = np.dot(R,points_2D_felchette) + T
    
    if DEBUG:
        # Affichage des résultats
        print("Coordonnées de la flechette (repère cam1) :")
        print(points_2D_felchette)
        print("Coordonnées de la flechette (repère centre de la cible) :")
        print(points_2D_felchette_reel[0],points_2D_felchette_reel[2])
    
    return np.array([points_2D_felchette_reel[0],points_2D_felchette_reel[2]])

if __name__ == '__main__':
    # Captures utiles pour la calibration
    # cap = open_stream([1])[0]
    # _ = get_frame(cap)
    # time.sleep(1) 
    # i=1
    # while True:
    #     pixels_cam = get_frame(cap)
        
    #     cv2.imwrite(f'cam2_images/cam2_image{64+i}.jpg', pixels_cam)
        
    #     cv2.imshow(f'cam {i}', pixels_cam.astype(np.uint8))
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    #     i+=1
    print(get_intrinsix_matrix('cam2_images/*.jpg'))