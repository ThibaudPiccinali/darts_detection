import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import vision as vision

matplotlib.use('agg')

class Dartboard:
    def __init__(self, radius = 21.5, sectors = [6, 13, 4, 18, 1, 20, 5, 12, 9, 14, 11, 8, 16, 7, 19, 3, 17, 2, 15, 10], radius_bullseye = 1.5/2,radius_outer_bullseye = 3.2/2,radius_double_inner=16,radius_double_outer=16.9,radius_triple_inner=9.5,radius_triple_outer=10.5):
        # Distances en cm
        self.radius = radius
        self.sectors = sectors
        self.radius_bullseye = radius_bullseye
        self.radius_outer_bullseye = radius_outer_bullseye
        self.radius_double_inner = radius_double_inner
        self.radius_double_outer = radius_double_outer
        self.radius_triple_inner = radius_triple_inner
        self.radius_triple_outer = radius_triple_outer
    
    def compute_score(self,pos_dart):
        # Calcul de la distance au centre
        r = math.sqrt(pos_dart[0]**2 + pos_dart[1]**2)

        # Vérification des zones concentriques
        if r <= self.radius_bullseye:
            return 50  # Bullseye
        elif r <= self.radius_outer_bullseye:
            return 25  # Outer Bullseye
        elif r > self.radius_double_outer:
            return 0  # Hors cible
        
        # Calcul de l'angle pour déterminer le secteur
        angle = math.degrees(math.atan2(pos_dart[1], pos_dart[0]) + 2*np.pi/40) # Il y a un décalage du au fait les sections sont décalées de 2*np.pi/40 sur chaque axe
        if angle < 0:
            angle += 360
        
        # Trouver le secteur (chaque secteur = 18°)
        sector_index = int(angle // 18 )
        sector_value = self.sectors[sector_index]
        
        # Vérification des anneaux (Triple, Double)
        if self.radius_triple_inner <= r <= self.radius_triple_outer:
            return sector_value * 3  # Triple ring
        elif self.radius_double_inner <= r <= self.radius_double_outer:
            return sector_value * 2  # Double ring
        
        # Si aucune condition spéciale, retourner la valeur du secteur
        return sector_value

    def save_image_dart_on_board(self,image_name,darts):

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
        ax.set_xlim(-self.radius, self.radius)
        ax.set_ylim(-self.radius, self.radius)
        ax.set_aspect('equal')
        ax.axis('off')

        # Ajouter un cercle noir avec un rayon de 10 unités et centré à (0, 0)
        circle = plt.Circle((0, 0), self.radius, color='black', zorder=0)
        # Ajouter le cercle à l'axe
        ax.add_artist(circle)

        # Draw the scoring segments (full pie sections)
        for i in range(segments):
            start_angle = angles[i]
            end_angle = angles[i + 1]
            segment_arc = np.linspace(start_angle, end_angle, 100)
            outer_arc = [(self.radius_double_outer * np.cos(a), self.radius_double_outer * np.sin(a)) for a in segment_arc]
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
            triple_inner_arc = [(self.radius_triple_inner * np.cos(a), self.radius_triple_inner * np.sin(a)) for a in np.linspace(start_angle, end_angle, 100)]
            triple_outer_arc = [(self.radius_triple_outer * np.cos(a), self.radius_triple_outer * np.sin(a)) for a in np.linspace(end_angle, start_angle, 100)]
            triple_ring = plt.Polygon(
                triple_inner_arc + triple_outer_arc,
                closed=True,
                color=triple_color,
                zorder=1
            )
            ax.add_patch(triple_ring)

            # Double ring
            double_inner_arc = [(self.radius_double_inner * np.cos(a), self.radius_double_inner * np.sin(a)) for a in np.linspace(start_angle, end_angle, 100)]
            double_outer_arc = [(self.radius_double_outer * np.cos(a), self.radius_double_outer * np.sin(a)) for a in np.linspace(end_angle, start_angle, 100)]
            double_ring = plt.Polygon(
                double_inner_arc + double_outer_arc,
                closed=True,
                color=double_color,
                zorder=1
            )
            ax.add_patch(double_ring)

        # Draw inner and outer rings for bullseye
        for self.radius, color in zip([self.radius_outer_bullseye,self.radius_bullseye], bullseye_colors):
            bull = plt.Circle((0, 0), self.radius, color=color, zorder=2)
            ax.add_artist(bull)

        # Annotate the scores
        for i, score in enumerate(self.sectors):
            angle = (angles[i] + angles[i + 1]) / 2
            x = (self.radius_double_outer + 1.5) * np.cos(angle)
            y = (self.radius_double_outer + 1.5) * np.sin(angle)
            ax.text(x, y, str(score), ha='center', va='center', fontweight='bold', fontsize=15, color='white')

        # Display darts
        for pos_dart in darts :
            if len(pos_dart) != 0:
                dart = plt.Circle((pos_dart), 0.5, color=dart_color, zorder=2)
                ax.add_artist(dart)
        
        plt.savefig(image_name, bbox_inches='tight', pad_inches=0.1, transparent=True)


class Player:
    def __init__(self, id, nom):
        self.nom = nom
        self.id = id
        self.nb_party_played = 0
    
    def display(self):
        print(f"---------- {self.nom} ----------")
        print(f"ID : {self.id}")
        print(f"Nombre de partie jouée(s) : {self.nb_party_played}")
    
    # Méthode to_dict pour convertir l'objet Player en dictionnaire
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'nb_party_played': self.nb_party_played
        }
            
class Game:
    def __init__(self, list_players):
        self.players = list_players
        self.scores = [301 for i in range(len(self.players))] # Le cumul des scores
        self.detailed_scores = [[] for i in range(len(self.players))] # Le score détaillé
        self.index_current_player = 0 # Le joueur qui doit jouer
        self.nb_player = len(list_players)
        self.last_darts_pos = [[], [] ,[]]
        self.last_darts_score = [-1, -1 ,-1]
        
        for player in self.players:
            player.nb_party_played+=1
    
    def to_dict(self):
        return {
            'players': [player.to_dict() for player in self.players],  # Convertir chaque player en dict
            'scores': self.scores,
            'detailed_scores': self.detailed_scores,
            'index_current_player': self.index_current_player,
            'nb_player': self.nb_player,
            'last_darts_pos': self.last_darts_pos,
            'last_darts_score': self.last_darts_score
        }
      
    def restart(self):
        self.scores = [301 for i in range(len(self.players))] # Le cumul des scores
        self.detailed_scores = [[] for i in range(len(self.players))] # Le score détaillé
        self.index_current_player = 0 # Le joueur qui doit jouer
             
    def next_turn(self,cap1,cap2,dartboard):
        print(f"C'est à {self.players[self.index_current_player].nom} de jouer")
        
        for i in range(3):
            # 3 fléchettes
            pos_dart = vision.get_coord_dart(cap1,cap2)
            score = dartboard.compute_score(pos_dart)
            self.last_darts_pos[i] = pos_dart
            self.last_darts_score[i] = score
            dartboard.save_image_dart_on_board("images/dartboard.png",pos_dart)
        
        # On met à jour la table des scores
        score = self.last_darts_score[0] + self.last_darts_score[1] + self.last_darts_score[2]
        print(f"{self.players[self.index_current_player].nom} a marqué {score} points")
        self.scores[self.index_current_player] -= score
        self.detailed_scores[self.index_current_player].append(score)
        
        # On vérifie si le joueur vient de gagner
        if self.scores[self.index_current_player] ==0:
            print(f"{self.players[self.index_current_player].nom} a gagné")
            return -1
        
        else:
            print(f"Fin de tour pour {self.players[self.index_current_player].nom}. Ramassez vos flechettes puis pressez <Enter>")
            input()
            # On passe la main au prochain joueur
            # On réinitialise les dernières flechettes
            self.last_darts_score = [-1, -1 ,-1]
            self.last_darts_pos = [[], [] ,[]]
            
            self.index_current_player = (self.index_current_player + 1 )%self.nb_player
            return 1
    
    def display(self):
        for i in range(len(self.players)):
            print(f"{self.players[i].nom} |",end=" ")
            for score in self.detailed_scores[i]:
                print(f"{score} |", end=" ")
            print(f"Total : {self.scores[i]}")