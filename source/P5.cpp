#include <iostream>
#include <vector>
#include "object.h"

int main() {
    // Exemple de coordonnées pour pos_dart
    std::vector<double> pos_dart = {-10.4271, 14.8793}; // Position (x, y)

    // Création de l'objet DartsGame
    Dartboard board;

    // Appel de la méthode compute_score avec pos_dart
    int score = board.compute_score(pos_dart);

    std::cout << "Score: " << score << std::endl;
    // // Exemple de positions de fléchettes pour l'image
    // std::vector<std::vector<float>> darts = {{5.0f, 3.0f}, {-10.0f, 10.0f}, {0.0f, 0.0f}};
    // board.save_image_dart_on_board("dartboard.png", darts);

    return 0;
}
