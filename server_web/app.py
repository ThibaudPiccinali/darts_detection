import socket
import json
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')
from flask import Flask, jsonify, render_template,redirect, url_for, request

app = Flask(__name__)

sum_last_3_darts = 0
darts = []

# Paramètres de la board
radius = "22.5"
sectors = ["6", "13", "4", "18", "1", "20", "5", "12", "9", "14", "11", "8", "16", "7", "19", "3", "17", "2", "15", "10"]
radius_bullseye = "0.8"
radius_outer_bullseye = "1.7"
radius_double_inner="15.8"
radius_double_outer="16.9"
radius_triple_inner="9.5"
radius_triple_outer="10.6"

# Fonction pour envoyer les commandes sur le port 80 (ou écoute la partie C++)
def send_command(command):
    host = '192.168.0.109'
    #host = '127.0.0.1'
    port = 8080
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(command.encode())
        response = s.recv(1024).decode()
    return response

# Route pour récupérer les données
@app.route('/api/data',methods=['POST'])
def get_data():
    # On demande les informations sur la partie
    request_cpp = json.dumps({"command": "getdata"})
    response = json.loads(send_command(request_cpp))
    # On vérifie s'il faut créer une nouvelle image
    sum_3_darts = response["last_darts_score"][0]+response["last_darts_score"][1]+response["last_darts_score"][2]
    global sum_last_3_darts, darts
    if(sum_3_darts!=sum_last_3_darts):
        # Une fléchette a été lancée (ou on a changé de joueur)
        # On génère la nouvelle image de la board
        sum_last_3_darts = sum_3_darts
        if len(darts) == 3:
            darts = []
        if (response["position"][0]==-999 and response["position"][1]==999):
            darts.append([None,None])
        else:
            while([None,None] in darts):
                darts.remove([None,None])
            darts.append(response["position"])
        if(sum_last_3_darts == -3):
            darts = [[None,None]]
        save_image_dart_on_board("images/dartboard.png",darts)
    print(darts)
    return response

# Route pour démarer la partie
@app.route('/api/start_game', methods=['POST'])
def start_game():
    request_data = request.get_json()
    list_players = request_data['name_players'].split(", ")
    if len(list_players) == 1 and list_players[0] == "":
        return jsonify({"message": "Pas de joueurs pour commmencer"}), 400
    game_mode = request_data['game_mode']
    # On demande de lancer la partie avec ces paramètres (et ceux de la cible)
    request_cpp = json.dumps({"command": "start", "players": list_players,"game_mode":game_mode,"radius":radius,"sectors":sectors,"radius_bullseye":radius_bullseye,"radius_outer_bullseye":radius_outer_bullseye,"radius_double_inner":radius_double_inner,"radius_double_outer":radius_double_outer,"radius_triple_inner":radius_triple_inner,"radius_triple_outer":radius_triple_outer})
    response = send_command(request_cpp)
    if (json.loads(response)['output'] == "Success"): 
        return jsonify({"message": "Jeu démarré", "redirect_url": url_for('main_page')}), 200
    return jsonify({"message": "Impossible de démarrer le jeu"}), 400

# Route pour changer le score des fléchettes
@app.route('/api/change_score_dart', methods=['POST'])
def change_score_dart():
    request_data = request.get_json()
    if not request_data['new_value'].isnumeric():
        return jsonify({"message": "Score doit être numérique"}), 400
    if not (int(request_data['new_value']) >= 0 and int(request_data['new_value']) <= 60):
        return jsonify({"message": "Score doit être compris entre 0 et 60"}), 400
    request_cpp = json.dumps({"command": "change_score_dart", "dart_n": str(int(request_data['dart_number'])-1),"new_score":str(int(request_data['new_value'])),})
    response = send_command(request_cpp)
    if (json.loads(response)['output'] == "Success"): 
        return jsonify({"message": "Score changé"}), 200
    return jsonify({"message": "Impossible de changé le score"}), 400

# Route pour recommencer la partie
@app.route('/api/restart_game', methods=['POST'])
def restart_game():
    request_cpp = json.dumps({"command": "reset"})
    response = send_command(request_cpp)
    if (json.loads(response)['output'] == "Success"): 
        return jsonify({"message": "Partie reset"}), 200
    return jsonify({"message": "Impossible de recommencer la partie"}), 400

# Route pour terminer la partie
@app.route('/api/end_game', methods=['POST'])
def end_game():
    request_cpp = json.dumps({"command": "end"})
    response = send_command(request_cpp)
    if (json.loads(response)['output'] == "Success"): 
        return jsonify({"message": "Jeu terminé", "redirect_url": url_for('index')}), 200
    return jsonify({"message": "Impossible d'arreter la partie"}), 400

# Route pour la page HTML de login
@app.route('/')
def index():
    return render_template('login.html')

# Route pour la page HTML principale
@app.route('/main')
def main_page():
    return render_template('main.html')

# Route pour le dossier images
@app.route('/images/<path:filename>')
def images(filename):
    from flask import send_from_directory
    return send_from_directory('images', filename)

def save_image_dart_on_board(image_name,darts):

    radius = 21.5
    sectors = [6, 13, 4, 18, 1, 20, 5, 12, 9, 14, 11, 8, 16, 7, 19, 3, 17, 2, 15, 10]
    radius_bullseye = 1.5/2
    radius_outer_bullseye = 3.2/2
    radius_double_inner=16
    radius_double_outer=16.9
    radius_triple_inner=9.5
    radius_triple_outer=10.5
    # Define scoring segments
    segments = 20  # Number of scoring segments (1 to 20)
    angles = np.linspace(-2 * np.pi/20 + 2 * np.pi/40, 2 * np.pi + 2 * np.pi/40 - 2 * np.pi/20, segments + 1)
        
    # Define colors for the segments and scoring areas
    segment_colors = ['#FFFFFF', '#000000']  # Alternate white and black for the segments
    triple_colors = ['#0F9536', '#E62F2B']  # Green for white sections, red for black sections
    double_colors = ['#0F9536', '#E62F2B']  # Same as triple colors
    bullseye_colors = ['#0F9536', '#E62F2B']  # Green for inner bull, red for outer bull
    dart_color = '#F7F011'
        
    # Create the dartboard
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-radius, radius)
    ax.set_ylim(-radius, radius)
    ax.set_aspect('equal')
    ax.axis('off')

    # Ajouter un cercle noir avec un rayon de 10 unités et centré à (0, 0)
    circle = plt.Circle((0, 0), radius, color='black', zorder=0)
    # Ajouter le cercle à l'axe
    ax.add_artist(circle)

    # Draw the scoring segments (full pie sections)
    for i in range(segments):
        start_angle = angles[i]
        end_angle = angles[i + 1]
        segment_arc = np.linspace(start_angle, end_angle, 100)
        outer_arc = [(radius_double_outer * np.cos(a), radius_double_outer * np.sin(a)) for a in segment_arc]
        wedge = plt.Polygon(
            [(0, 0)] + outer_arc,
            closed=True,
            color=segment_colors[i % 2],
            zorder=0
        )
        ax.add_patch(wedge)

    # Draw the inner and outer scoring areas (triple and double rings)
    for i in range(segments):
        start_angle = angles[i]
        end_angle = angles[i + 1]
        triple_color = triple_colors[i % 2]
        double_color = double_colors[i % 2]

        # Triple ring
        triple_inner_arc = [(radius_triple_inner * np.cos(a), radius_triple_inner * np.sin(a)) for a in np.linspace(start_angle, end_angle, 100)]
        triple_outer_arc = [(radius_triple_outer * np.cos(a), radius_triple_outer * np.sin(a)) for a in np.linspace(end_angle, start_angle, 100)]
        triple_ring = plt.Polygon(
            triple_inner_arc + triple_outer_arc,
            closed=True,
            color=triple_color,
            zorder=1
        )
        ax.add_patch(triple_ring)

       # Double ring
        double_inner_arc = [(radius_double_inner * np.cos(a), radius_double_inner * np.sin(a)) for a in np.linspace(start_angle, end_angle, 100)]
        double_outer_arc = [(radius_double_outer * np.cos(a), radius_double_outer * np.sin(a)) for a in np.linspace(end_angle, start_angle, 100)]
        double_ring = plt.Polygon(
            double_inner_arc + double_outer_arc,
            closed=True,
            color=double_color,
            zorder=1
        )
        ax.add_patch(double_ring)

    # Draw inner and outer rings for bullseye
    for radius, color in zip([radius_outer_bullseye, radius_bullseye], bullseye_colors):
        bull = plt.Circle((0, 0), radius, color=color, zorder=2)
        ax.add_artist(bull)

    # Annotate the scores
    for i, score in enumerate(sectors):
        angle = (angles[i] + angles[i + 1]) / 2
        x = (radius_double_outer + 1.5) * np.cos(angle)
        y = (radius_double_outer + 1.5) * np.sin(angle)
        ax.text(x, y, str(score), ha='center', va='center', fontweight='bold', fontsize=15, color='white')

    # Display darts
    if len(darts) != 0:
        for pos_dart in darts :
            if len(pos_dart) != 0 and (pos_dart[0] !=None and pos_dart[1] !=None):
                dart_circle = plt.Circle((pos_dart), 0.5, color=dart_color, zorder=2)
                ax.add_artist(dart_circle)
        
    plt.savefig(image_name, bbox_inches='tight', pad_inches=0.1, transparent=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)