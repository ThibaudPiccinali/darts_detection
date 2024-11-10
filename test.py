import cv2

# Ouvre le flux vidéo de la caméra (index 0 pour la caméra par défaut)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Erreur : impossible d'ouvrir la caméra")
else:
    while True:
        # Lit une frame de la caméra
        ret, frame = cap.read()

        # Vérifie que la frame a bien été capturée
        if not ret:
            print("Erreur : impossible de lire l'image de la caméra")
            break
        print(frame)
        # Affiche la frame
        cv2.imwrite("image.jpg", frame)


# Libère les ressources
cap.release()
cv2.destroyAllWindows()
