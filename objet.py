import cv2
import math
import vision as vision

class Dartboard:
    def __init__(self, radius = 21.5, sectors = [11,8,16,7,19,3,17,2,15,10,6,13,4,18,1,20,5,12,9,14], radius_bullseye = 1.5/2,radius_outer_bullseye = 3.2/2,radius_double_inner=16,radius_double_outer=16.9,radius_triple_inner=9.5,radius_triple_outer=10.5):
        ## Attention ici sectors sens particulier parce repère de la cible non usuel -> à changer
        # Distances en cm
        self.radius = radius
        self.sectors = sectors
        self.radius_bullseye = radius_bullseye
        self.radius_outer_bullseye = radius_outer_bullseye
        self.radius_double_inner = radius_double_inner
        self.radius_double_outer = radius_double_outer
        self.radius_triple_inner = radius_triple_inner 
        self.radius_triple_outer = radius_triple_outer
    
    def compute_score(self,coord_x,coord_y):
        # Calcul de la distance au centre
        r = math.sqrt(coord_x**2 + coord_y**2)

        # Vérification des zones concentriques
        if r <= self.radius_bullseye:
            return 50  # Bullseye
        elif r <= self.radius_outer_bullseye:
            return 25  # Outer Bullseye
        elif r > self.radius_double_outer:
            return 0  # Hors cible
        
        # Calcul de l'angle pour déterminer le secteur
        angle = math.degrees(math.atan2(coord_y, coord_x))
        if angle < 0:
            angle += 360
        
        # Trouver le secteur (chaque secteur = 18°)
        sector_index = int(angle // 18)
        sector_value = self.sectors[sector_index]
        
        # Vérification des anneaux (Triple, Double)
        if self.radius_triple_inner <= r <= self.radius_triple_outer:
            return sector_value * 3  # Triple ring
        elif self.radius_double_inner <= r <= self.radius_double_outer:
            return sector_value * 2  # Double ring
        
        # Si aucune condition spéciale, retourner la valeur du secteur
        return sector_value

    def display_dart_on_board(self,pos_dart,board_image):
        size_board_image = board_image.shape[0] # Suppose que l'image soit carré
        pos_dart_pixels = (pos_dart[0]*size_board_image/(self.radius*2),pos_dart[1]*size_board_image/(self.radius*2))

        point_x = int(size_board_image // 2 - pos_dart_pixels[0])
        point_y = int(size_board_image // 2 + pos_dart_pixels[1])
        
        cv2.imshow('Pointe flechette cam 1',cv2.circle(board_image, (point_x, point_y), 5, [0,0,255], -1))   
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
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
        
        for player in self.players:
            player.nb_party_played+=1
    
    def to_dict(self):
        return {
            'players': [player.to_dict() for player in self.players],  # Convertir chaque player en dict
            'scores': self.scores,
            'detailed_scores': self.detailed_scores,
            'index_current_player': self.index_current_player,
            'nb_player': self.nb_player
        }
      
    def restart(self):
        self.scores = [301 for i in range(len(self.players))] # Le cumul des scores
        self.detailed_scores = [[] for i in range(len(self.players))] # Le score détaillé
        self.index_current_player = 0 # Le joueur qui doit jouer
             
    def next_turn(self,cap1,cap2,dartboard):
        print(f"C'est à {self.players[self.index_current_player].nom} de jouer")
        
        # 3 fléchettes
        print("Première fléchette")
        pos_dart = vision.get_coord_dart(cap1,cap2)
        score1 = dartboard.compute_score(pos_dart[0],pos_dart[1])
        print(score1)
        print("Deuxième fléchette")
        pos_dart = vision.get_coord_dart(cap1,cap2)
        score2 = dartboard.compute_score(pos_dart[0],pos_dart[1])
        print(score2)
        print("Troisième fléchette")
        pos_dart = vision.get_coord_dart(cap1,cap2)
        score3 = dartboard.compute_score(pos_dart[0],pos_dart[1])
        print(score3)
        
        # On met à jour la table des scores
        score = score1 + score2 + score3
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
            self.index_current_player = (self.index_current_player + 1 )%self.nb_player
            return 1
    
    def display(self):
        for i in range(len(self.players)):
            print(f"{self.players[i].nom} |",end=" ")
            for score in self.detailed_scores[i]:
                print(f"{score} |", end=" ")
            print(f"Total : {self.scores[i]}")