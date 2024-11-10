import time

import processing_pixels as pp
import camera as cam


cap = open_stream([1])[0]
# Necessaire parce que doit laisser le temps à la caméra de bien de setup
_ = get_frame(cap)
time.sleep(1)

# display(get_frame(cap),"test")

# # Charger les images
# a = cv2.imread('image.jpg')
# b = cv2.imread('image2.jpg')

# Capturer les images
a_colors = get_frame(cap)
a = cv2.cvtColor(a_colors, cv2.COLOR_BGR2GRAY)
# Convertir les images en format compatible (unsigned char)
image1 = np.array(a,dtype=np.uint8)
image1 = np.stack([image1] * 3, axis=-1)
display(image1,"Image 1")
    
b_colors = get_frame(cap)
b = cv2.cvtColor(b_colors, cv2.COLOR_BGR2GRAY)
# Convertir les images en format compatible (unsigned char)
image2 = np.array(b,dtype=np.uint8)
image2 = np.stack([image2] * 3, axis=-1)
display(image2,"Image 2")
    
# Appeler la fonction pour obtenir les différences binaires
diff_image = binary_diff_images(image1, image2)

# Afficher les résultats (différences en blanc)
cv2.imshow('diff_image', diff_image.astype(np.uint8))
diff_image = np.uint8(diff_image)
    
kernel = np.ones((2,2),np.uint8)
opened_image = cv2.morphologyEx(diff_image, cv2.MORPH_OPEN, kernel)
    
cv2.imshow('erosion', opened_image.astype(np.uint8))
    
filtered_image = filter_by_centroid(opened_image, 170)
    
for i in range(len(a)):
    for j in range(len(a[0])):
        if filtered_image[i][j] == 255:
            b_colors[i][j] = [0, 0, 255]
    
cv2.imshow('Detection',b_colors)
    
cv2.waitKey(0)
cv2.destroyAllWindows()