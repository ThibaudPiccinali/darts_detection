import cv2
import numpy as np

# # Ouvre le flux vidéo de la caméra (index 0 pour la caméra par défaut)
# cap = cv2.VideoCapture(1)

# print(cap)

# if not cap.isOpened():
#     print("Erreur : impossible d'ouvrir la caméra")
# else:
#     while True:
#         # Lit une frame de la caméra
#         ret, frame = cap.read()

#         # Vérifie que la frame a bien été capturée
#         if not ret:
#             print("Erreur : impossible de lire l'image de la caméra")
#             break
#         # Affiche la frame
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         cv2.imwrite("image3.jpg", frame)


# # Libère les ressources
# cap.release()
# cv2.destroyAllWindows()



def dessiner_cible(taille=600):
    """
    Dessine une cible de fléchettes réaliste.
    
    :param taille: Taille de l'image (carrée) en pixels.
    :return: Une image OpenCV représentant la cible.
    """
    # Créer une image noire
    image = np.zeros((taille, taille, 3), dtype=np.uint8)
    centre = taille // 2  # Centre de l'image
    rayon_max = taille // 2  # Rayon de la cible entière
    
    # Définir les rayons pour les zones
    rayons = {
        "bullseye_vert": rayon_max // 15,
        "bullseye_rouge": rayon_max // 10,
        "anneau_vert": rayon_max // 3,
        "anneau_rouge": rayon_max // 2
    }
    
    # Dessiner le bullseye (rouge et vert)
    cv2.circle(image, (centre, centre), rayons["bullseye_rouge"], (0, 0, 255), -1)  # Rouge
    cv2.circle(image, (centre, centre), rayons["bullseye_vert"], (0, 255, 0), -1)   # Vert

    # Dessiner les anneaux concentriques alternés (noir/blanc)
    nb_anneaux = 10
    epaisseur_anneau = (rayons["anneau_rouge"] - rayons["bullseye_rouge"]) // nb_anneaux
    for i in range(nb_anneaux):
        couleur = (255, 255, 255) if i % 2 == 0 else (0, 0, 0)
        rayon_externe = rayons["bullseye_rouge"] + i * epaisseur_anneau
        rayon_interne = rayon_externe - epaisseur_anneau
        cv2.circle(image, (centre, centre), rayon_externe, couleur, -1)
        cv2.circle(image, (centre, centre), rayon_interne, (0, 0, 0), -1)

    # Dessiner les zones rouges et vertes (extérieur)
    cv2.circle(image, (centre, centre), rayons["anneau_rouge"], (0, 0, 255), thickness=3)
    cv2.circle(image, (centre, centre), rayons["anneau_vert"], (0, 255, 0), thickness=3)
    
    return image

# Générer la cible
cible = dessiner_cible()

# Afficher la cible
cv2.imshow("Cible de Fléchettes", cible)
cv2.waitKey(0)
cv2.destroyAllWindows()