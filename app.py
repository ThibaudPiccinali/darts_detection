from flask import Flask, jsonify, render_template,redirect, url_for, request
from threading import Thread, Condition

import vision as vision
import objet as obj
import time

app = Flask(__name__)

partie = None
cible = None

condition_next_dart = Condition()
condition_next_player = Condition()

def game(list_players):
    
    # Setup nécessaire des caméras
    cap1, cap2 = vision.open_stream([2, 0]) # Les caméras doivent être sur deux ports différents
    # Necessaire parce que doit laisser le temps à la caméra de bien de setup
    cam1 = vision.get_frame(cap1)
    time.sleep(1) # necessaire pour avoir laisser le temps à la cam de changer (?)
    cam2 = vision.get_frame(cap2)
    time.sleep(1)
    
    # Création des joueurs
    liste_joueurs = []
    for name in list_players:
        liste_joueurs.append(obj.Player(1,name))
    
    global partie, cible
    partie = obj.Game(liste_joueurs)
    cible = obj.Dartboard()
    
    while(True):
        print(f"C'est à {partie.players[partie.index_current_player].nom} de jouer")
        last_darts_pos = [[], [] ,[]]
        cible.save_image_dart_on_board("images/dartboard.png",last_darts_pos)
        
        for i in range(3):
            # 3 fléchettes
            # Images de références 
            images_ref = vision.get_images_both_cameras(cap1,cap2)
            partie.can_play = 1
            # L'utilisateur peut jeter sa fléchette
            print("Jettez fléchette")
            
            with condition_next_dart:  # Acquiert la condition pour attendre
                condition_next_dart.wait()  # Attend passivement une notification
                
            print("Fléchette lancée")
            partie.can_play = 0
            # Images avec la fléchette 
            images_dart = vision.get_images_both_cameras(cap1,cap2)
            # Calcul de la position de la fléchette
            pos_dart = vision.get_coord_dart(images_ref[0][0],images_ref[0][1],images_ref[1][0],images_ref[1][1],images_dart[0][0],images_dart[0][1],images_dart[1][0],images_dart[1][1])
                
            score = cible.compute_score(pos_dart)
            last_darts_pos[i] = pos_dart
            partie.last_darts_score[i] = score
            cible.save_image_dart_on_board("images/dartboard.png",last_darts_pos)
            
        # On met à jour la table des scores
        score = partie.last_darts_score[0] + partie.last_darts_score[1] + partie.last_darts_score[2]
        print(f"{partie.players[partie.index_current_player].nom} a marqué {score} points")
        partie.scores[partie.index_current_player] -= score
        partie.detailed_scores[partie.index_current_player].append(score)
            
        # On vérifie si le joueur vient de gagner
        if partie.scores[partie.index_current_player] ==0:
            print(f"{partie.players[partie.index_current_player].nom} a gagné")
            return 1
            
        else:
            print(f"Fin de tour pour {partie.players[partie.index_current_player].nom}. Ramassez vos flechettes")
            
            with condition_next_player:  # Acquiert la condition pour attendre
                condition_next_player.wait()  # Attend passivement une notification
                
            print("Fléchettes ramassées")
            
            # On réinitialise les dernières flechettes et la cible
            partie.last_darts_score = [-1, -1 ,-1]
            cible.save_image_dart_on_board("images/dartboard.png",[])
            
            # On passe la main au prochain joueur        
            partie.index_current_player = (partie.index_current_player + 1 )%partie.nb_player

     
# Route pour récupérer les données
@app.route('/api/data')
def get_data():
    if partie !=None and type(partie)!=int:
        response = jsonify(partie.to_dict())
        response.charset = 'utf-8'  # Spécification de l'encodage UTF-8
        return response
    return jsonify({"message": "Partie non commencée"}), 400

# Route pour démarer la partie
@app.route('/api/start_game', methods=['POST'])
def start_game():
    request_data = request.get_json()
    list_players = request_data['name_players'].split(", ")
    if len(list_players) == 1 and list_players[0] == "":
        return jsonify({"message": "Pas de joueurs pour commmencer"}), 400
    
    # On lance la partie
    
    global partie,thread
    partie = 1 # Permet de directement passer à la page d'après même si la partie n'est pas correctement initialisé
    thread = Thread(target=game,args=(list_players,),  daemon=True)
    thread.start()
    
    return jsonify({"message": "Jeu démarré", "redirect_url": url_for('main_page')}), 200

# Route pour terminer la partie
@app.route('/api/end_game', methods=['POST'])
def end_game():
    global partie
    partie = None
    return jsonify({"message": "Jeu terminé", "redirect_url": url_for('index')}), 200

# Route pour informer que le changemnt de joueur est demandé (les fléchettes ont été ramassée)
@app.route('/api/next_player', methods=['POST'])
def next_player():
    with condition_next_player:  # Acquiert la condition avant de notifier
        condition_next_player.notify_all()
    return jsonify({"message": "Joueur changé"}), 200

# Route pour informer que la fléchette a été lancée
@app.route('/api/dart_throw', methods=['POST'])
def dart_throw():
    with condition_next_dart:  # Acquiert la condition avant de notifier
        condition_next_dart.notify_all()
    return jsonify({"message": "Fléchette changée"}), 200

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