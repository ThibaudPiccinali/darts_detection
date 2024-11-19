import cv2
import glob
import time
import numpy as np

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