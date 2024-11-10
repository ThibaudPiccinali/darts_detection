import time
import cv2
import numpy as np

import camera as cam
import processing_pixels as pp

###### Activation de la caméra ######

cap = cam.open_stream([1])[0]
# Necessaire parce que doit laisser le temps à la caméra de bien de setup
_ = cam.get_frame(cap)
time.sleep(1)

###### Capture (et mise en forme) des images ######

# Capturer les images
base_image_colors = cam.get_frame(cap)
base_image = cv2.cvtColor(base_image_colors, cv2.COLOR_BGR2GRAY)
# Convertir les images en format compatible (unsigned char)
base_image = np.array(base_image,dtype=np.uint8)
base_image_grey = np.stack([base_image] * 3, axis=-1)
pp.display(base_image_grey,"Image de base en niveau de gris")
    
dart_image_colors = cam.get_frame(cap)
dart_image = cv2.cvtColor(dart_image_colors, cv2.COLOR_BGR2GRAY)
# Convertir les images en format compatible (unsigned char)
dart_image = np.array(dart_image,dtype=np.uint8)
dart_image_grey = np.stack([dart_image] * 3, axis=-1)
pp.display(dart_image_grey,"Image avec la flechette en niveau de gris")

###### Première étape de detection (comparaison entre les deux images) ######

# Appeler la fonction pour obtenir les différences binaires
diff_image = pp.binary_diff_images(base_image_grey, dart_image_grey)

# Afficher les résultats (différences en blanc)
cv2.imshow('diff_image', diff_image.astype(np.uint8))
diff_image = np.uint8(diff_image)

###### Filtrage (méthode Opening) ######

kernel = np.ones((2,2),np.uint8)
opened_image = cv2.morphologyEx(diff_image, cv2.MORPH_OPEN, kernel)
    
cv2.imshow('erosion', opened_image.astype(np.uint8))

###### Filtrage (centre de masse) ######

filtered_image = pp.filter_by_centroid(opened_image, 170)

###### Affichage final ######

for i in range(len(dart_image_colors)):
    for j in range(len(dart_image_colors[0])):
        if filtered_image[i][j] == 255:
            dart_image_colors[i][j] = [0, 0, 255]
    
cv2.imshow('Detection',dart_image_colors)
    
cv2.waitKey(0)
cv2.destroyAllWindows()