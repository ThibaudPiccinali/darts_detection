import time
import cv2
import numpy as np

import camera as cam
import processing_pixels as pp

###### Activation des caméras ######

# cap1, cap2 = cam.open_stream([1, 2]) # Les caméras doivent être sur deux ports différents

# # Necessaire parce que doit laisser le temps à la caméra de bien de setup
# _ = cam.get_frame(cap1)
# time.sleep(1) # necessaire pour avoir laisser le temps à la cam de changer (?)
# _ = cam.get_frame(cap2)
# time.sleep(1)

# ###### Capture (et mise en forme) des images ######

# # Cam 1
# base_image_cam1_colors = cam.get_frame(cap1)
# base_image_cam1 = cv2.cvtColor(base_image_cam1_colors, cv2.COLOR_BGR2GRAY)
# # Convertir les images en format compatible (unsigned char)
# base_image_cam1 = np.array(base_image_cam1,dtype=np.uint8)
# base_image_cam1_grey = np.stack([base_image_cam1] * 3, axis=-1)

# # Cam 2
# base_image_cam2_colors = cam.get_frame(cap2)
# base_image_cam2 = cv2.cvtColor(base_image_cam2_colors, cv2.COLOR_BGR2GRAY)
# # Convertir les images en format compatible (unsigned char)
# base_image_cam2 = np.array(base_image_cam2,dtype=np.uint8)
# base_image_cam2_grey = np.stack([base_image_cam2] * 3, axis=-1)

# cv2.imshow('Image de base cam1 en niveau de gris', base_image_cam1_grey.astype(np.uint8))
# cv2.imshow('Image de base cam2 en niveau de gris', base_image_cam2_grey.astype(np.uint8))

# ## On attend que l'utilisateur lance la flechette
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# dart_image_cam1_colors = cam.get_frame(cap1)
# dart_image_cam1 = cv2.cvtColor(dart_image_cam1_colors, cv2.COLOR_BGR2GRAY)
# # Convertir les images en format compatible (unsigned char)
# dart_image_cam1 = np.array(dart_image_cam1,dtype=np.uint8)
# dart_image_cam1_grey = np.stack([dart_image_cam1] * 3, axis=-1)

# dart_image_cam2_colors = cam.get_frame(cap2)
# dart_image_cam2 = cv2.cvtColor(dart_image_cam2_colors, cv2.COLOR_BGR2GRAY)
# # Convertir les images en format compatible (unsigned char)
# dart_image_cam2 = np.array(dart_image_cam2,dtype=np.uint8)
# dart_image_cam2_grey = np.stack([dart_image_cam2] * 3, axis=-1)

# cv2.imshow('Image cam1 avec la flechette en niveau de gris', dart_image_cam1_grey.astype(np.uint8))
# cv2.imshow('Image cam2 avec la flechette en niveau de gris', dart_image_cam2_grey.astype(np.uint8))

# ###### Première étape de detection (comparaison entre les deux images) ######

# # Appeler la fonction pour obtenir les différences binaires
# diff_image_cam1 = pp.binary_diff_images(base_image_cam1_grey, dart_image_cam1_grey)
# diff_image_cam2 = pp.binary_diff_images(base_image_cam2_grey, dart_image_cam2_grey)

# # Afficher les résultats (différences en blanc)
# cv2.imshow('diff_image_cam1', diff_image_cam1.astype(np.uint8))
# cv2.imshow('diff_image_cam2', diff_image_cam2.astype(np.uint8))
# diff_image_cam1 = np.uint8(diff_image_cam1)
# diff_image_cam2 = np.uint8(diff_image_cam2)

# ###### Filtrage (méthode Opening) ######

# kernel = np.ones((2,2),np.uint8)

# opened_image_cam1 = cv2.morphologyEx(diff_image_cam1, cv2.MORPH_OPEN, kernel)
# opened_image_cam2 = cv2.morphologyEx(diff_image_cam2, cv2.MORPH_OPEN, kernel)
# cv2.imshow('opening cam 1', opened_image_cam1.astype(np.uint8))    
# cv2.imshow('opening cam 2', opened_image_cam2.astype(np.uint8))

# ###### Filtrage (centre de masse) ######

# filtered_image_cam1 = pp.filter_by_centroid(opened_image_cam1, 170)
# filtered_image_cam2 = pp.filter_by_centroid(opened_image_cam2, 170)

# ###### Affichage final ######

# for i in range(len(base_image_cam2_colors)):
#     for j in range(len(base_image_cam2_colors[0])):
        
#         if filtered_image_cam1[i][j] == 255:
#             dart_image_cam1_colors[i][j] = [0, 0, 255]
            
#         if filtered_image_cam2[i][j] == 255:
#             dart_image_cam2_colors[i][j] = [0, 0, 255]

# cv2.imshow('Detection cam 1',dart_image_cam1_colors)    
# cv2.imshow('Detection cam 2',dart_image_cam2_colors)
    
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# ###### Identification de la pointe de la flechette ######

# # Trouver les coordonnées des pixels blancs (255)
# points_felchette_cam1 = np.column_stack(np.where(filtered_image_cam1 == 255))

# # Trouver le point avec la plus grande coordonnée y
# lowest_point_felchette_cam1 = points_felchette_cam1[points_felchette_cam1[:, 0].argmax()]
# # Inverser les coordonnées pour obtenir (x, y)
# lowest_point_felchette_cam1 = (lowest_point_felchette_cam1[0], lowest_point_felchette_cam1[1])

# points_felchette_cam2 = np.column_stack(np.where(filtered_image_cam2 == 255))
# lowest_point_felchette_cam2 = points_felchette_cam2[points_felchette_cam2[:, 0].argmax()]
# lowest_point_felchette_cam2 = (lowest_point_felchette_cam2[0], lowest_point_felchette_cam2[1])

# print(f"Le point le plus bas sur la caméra 1 est à la position : {lowest_point_felchette_cam1}")
# print(f"Le point le plus bas sur la caméra 2 est à la position : {lowest_point_felchette_cam2}")

# cv2.imshow('Pointe flechette cam 1',cv2.circle(dart_image_cam1_colors, (lowest_point_felchette_cam1[1], lowest_point_felchette_cam1[0]), 5, [0,255,0], -1))    
# cv2.imshow('Pointe flechette cam 2',cv2.circle(dart_image_cam2_colors, (lowest_point_felchette_cam2[1], lowest_point_felchette_cam2[0]), 5, [0,255,0], -1))
    
# cv2.waitKey(0)
# cv2.destroyAllWindows()

##### Calcul de la position réelle associée ######

# Matrices intrinsèques des caméras
K1 = np.array(cam.get_intrinsix_matrix('cam1_images/*.jpg'))  # Matrice de la caméra 1
K2 = np.array(cam.get_intrinsix_matrix('cam2_images/*.jpg'))  # Matrice de la caméra 2

# Matrices extrinsèques (Rotation et Translation)
# Origine -> Centre de la cible

R1Z = np.array([
    [np.cos(np.radians(180)), -np.sin(np.radians(180)), 0],
    [np.sin(np.radians(180)), np.cos(np.radians(180)), 0],
    [0, 0, 1]
])

R1Y = np.array([
    [np.cos(np.radians(-90)), 0, np.sin(np.radians(-90))],
    [0, 1, 0],
    [-np.sin(np.radians(-90)), 0, np.cos(np.radians(-90))]
])

R1 = R1Z @ R1Y  # Rotation de la caméra 1
T1 = np.array([[30], [0], [0]])  # Translation de la caméra 1

R2Z = np.array([
    [np.cos(np.radians(90)), -np.sin(np.radians(90)), 0],
    [np.sin(np.radians(90)), np.cos(np.radians(90)), 0],
    [0, 0, 1]
])

R2Y = np.array([
    [np.cos(np.radians(-90)), 0, np.sin(np.radians(-90))],
    [0, 1, 0],
    [-np.sin(np.radians(-90)), 0, np.cos(np.radians(-90))]
])

R2 = R2Z @ R2Y  # Rotation de la caméra 2
T2 = np.array([[0], [30], [0]])  # Translation de la caméra 2

lowest_point_felchette_cam1 = (243, 88)
lowest_point_felchette_cam2 = (281, 309)

# Triangulation pour obtenir les points 3D
points_2D_felchette = pp.triangulate_point(K1, K2, R1, T1, R2, T2, np.array(lowest_point_felchette_cam1), np.array(lowest_point_felchette_cam2))

# Affichage des résultats
print("Coordonnées de la flechette :")
print(points_2D_felchette)

## Prochaine fois 
# -> Avoir une meilleure calcul pour les matrices intrinsèques : prendre plus de photos pour faire une estimation plus fine
# -> Je pense que c'est ça qui pose problème dans l'estimation finale des coordonnées 2D