#include <cmath>

#include <vector>
#include <string>
#include <iostream>

#include "object.h"

Dartboard::Dartboard(double radius, 
                     std::vector<int> sectors, 
                     double radius_bullseye, 
                     double radius_outer_bullseye, 
                     double radius_double_inner, 
                     double radius_double_outer, 
                     double radius_triple_inner, 
                     double radius_triple_outer)
    : radius(radius), sectors(sectors), radius_bullseye(radius_bullseye),
      radius_outer_bullseye(radius_outer_bullseye), radius_double_inner(radius_double_inner),
      radius_double_outer(radius_double_outer), radius_triple_inner(radius_triple_inner),
      radius_triple_outer(radius_triple_outer) {}

int Dartboard:: compute_score(const std::vector<double>& pos_dart) {
        // Gestion du cas d'erreur ou aucun changement n'a été constaté
        if (pos_dart[0] == 0.0 && pos_dart[1] == 0.0) {
            return 0;
        }
        
        // Calcul de la distance au centre
        double r = std::sqrt(pos_dart[0] * pos_dart[0] + pos_dart[1] * pos_dart[1]);

        // Vérification des zones concentriques
        if (r <= radius_bullseye) {
            return 50;  // Bullseye
        } else if (r <= radius_outer_bullseye) {
            return 25;  // Outer Bullseye
        } else if (r > radius_double_outer) {
            return 0;  // Hors cible
        }

        // Calcul de l'angle pour déterminer le secteur
        double angle = std::atan2(pos_dart[1], pos_dart[0]) * 180 / M_PI + 360.0 / 40;
        if (angle < 0) {
            angle += 360;
        }

        // Trouver le secteur (chaque secteur = 18°)
        int sector_index = static_cast<int>(angle / 18);
        int sector_value = sectors[sector_index];

        // Vérification des anneaux (Triple, Double)
        if (radius_triple_inner <= r && r <= radius_triple_outer) {
            return sector_value * 3;  // Triple ring
        } else if (radius_double_inner <= r && r <= radius_double_outer) {
            return sector_value * 2;  // Double ring
        }

        // Si aucune condition spéciale, retourner la valeur du secteur
        return sector_value;
    }