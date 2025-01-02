from flask import Flask, jsonify, render_template
import threading

import utils as utils
import vision as vision
import objet as obj
import time
import cv2
import matplotlib.pyplot as plt

app = Flask(__name__)

partie = None

def game():
    # cap1, cap2 = vision.open_stream([0, 1]) # Les caméras doivent être sur deux ports différents

    # # Necessaire parce que doit laisser le temps à la caméra de bien de setup
    # cam1 = vision.get_frame(cap1)
    # time.sleep(1) # necessaire pour avoir laisser le temps à la cam de changer (?)
    # cam2 = vision.get_frame(cap2)
    # time.sleep(1)

    # cv2.imshow('CAM1', cam1)
    # cv2.imshow('CAM2', cam2)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # Création des joueurs
    liste_joueurs = [obj.Player(1,"Thibaud"),obj.Player(4,"Clément")]

    # Setup utilisé
    cible = obj.Dartboard()

    pos_dart = [13,1.9]
    cible.save_image_dart_on_board("test.png",pos_dart)
    print(f"Score : {cible.compute_score(pos_dart)}")
    global partie 
    partie = obj.Game(liste_joueurs)

    # exit = 1

    # while exit != -1:
    #     # On envoie les données au serveur
    #     exit = partie.next_turn(cap1,cap2,cible)
        
# On lance un thread pour gérer la partie
threading.Thread(target=game, daemon=True).start()

# Route pour récupérer les données
@app.route('/api/data')
def get_data():
    response = jsonify(partie.to_dict())
    response.charset = 'utf-8'  # Spécification de l'encodage UTF-8
    return response

# Route pour redémarer la partie
@app.route('/api/restart_game', methods=['POST'])
def restart_game():
    partie.restart()
    return jsonify({"message": "Jeu redémarré"}), 200

# Route pour la page HTML
@app.route('/')
def index():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)


