from flask import Flask, jsonify, render_template,redirect, url_for, request
import threading

import utils as utils
import vision as vision
import objet as obj
import time
import cv2

app = Flask(__name__)

partie = None

def game(list_player_names):
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
    liste_joueurs = []
     
    for name in list_player_names:
        liste_joueurs.append(obj.Player(1,name))

    # Setup utilisé
    cible = obj.Dartboard()

    #cible.save_image_dart_on_board("images/dartboard.png",[])
    global partie 
    partie = obj.Game(liste_joueurs)

    # exit = 1

    # while exit != -1:
    #     # On envoie les données au serveur
    #     exit = partie.next_turn(cap1,cap2,cible)
        

# Route pour récupérer les données
@app.route('/api/data')
def get_data():
    response = jsonify(partie.to_dict())
    response.charset = 'utf-8'  # Spécification de l'encodage UTF-8
    return response

# Route pour démarer la partie
@app.route('/api/start_game', methods=['POST'])
def start_game():
    request_data = request.get_json()
    list_players = request_data['name_players'].split(", ")
    if len(list_players) == 1 and list_players[0] == "":
        return jsonify({"message": "Pas de joueurs pour commmencer"}), 400
    # On lance un thread pour gérer la partie
    threading.Thread(target=game,args=(list_players,),  daemon=True).start()
    return jsonify({"message": "Jeu démarré", "redirect_url": url_for('main_page')}), 200

# Route pour redémarer la partie
@app.route('/api/restart_game', methods=['POST'])
def restart_game():
    partie.restart()
    return jsonify({"message": "Jeu redémarré"}), 200

# Route pour terminer la partie
@app.route('/api/end_game', methods=['POST'])
def end_game():
    global partie
    partie = None
    return jsonify({"message": "Jeu terminé", "redirect_url": url_for('index')}), 200

# Route pour la page HTML de login
@app.route('/')
def index():
    return render_template('login.html')

# Route pour la page HTML principale
@app.route('/main')
def main_page():
    if partie == None:
        # Redirige vers une page d'accueil si le jeu n'a pas démarré
        return redirect(url_for('index'))
    return render_template('main.html')

# Route pour le dossier images
@app.route('/images/<path:filename>')
def images(filename):
    from flask import send_from_directory
    return send_from_directory('images', filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)