import cv2

# Ouvre le flux vidéo de la caméra (index 0 pour la caméra par défaut)
cap = cv2.VideoCapture(1)

print(cap)

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
        # Affiche la frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imwrite("image3.jpg", frame)


# Libère les ressources
cap.release()
cv2.destroyAllWindows()
