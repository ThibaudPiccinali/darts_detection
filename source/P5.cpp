#include <iostream>
#include <vector>
#include <SFML/Graphics.hpp>
#include "object.h"

int main() {
    // Exemple de coordonnées pour pos_dart
    std::vector<double> pos_dart = {1.0, 2.0}; // Position (x, y)

    // Création de l'objet DartsGame
    Dartboard board;

    // Appel de la méthode compute_score avec pos_dart
    int score = board.compute_score(pos_dart);

    // Affichage du résultat
    std::cout << "Score: " << score << std::endl;

    return 0;
}
