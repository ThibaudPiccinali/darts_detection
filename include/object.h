#ifndef OBJECT_H
#define OBJECT_H

#include <vector>

class Dartboard {
public:
    // Constructeur
    Dartboard(double radius = 21.5, 
              std::vector<int> sectors = {6, 13, 4, 18, 1, 20, 5, 12, 9, 14, 11, 8, 16, 7, 19, 3, 17, 2, 15, 10},
              double radius_bullseye = 1.5 / 2, double radius_outer_bullseye = 3.2 / 2,
              double radius_double_inner = 16, double radius_double_outer = 16.9,
              double radius_triple_inner = 9.5, double radius_triple_outer = 10.5);

    // Méthodes
    int compute_score(const std::vector<double>& pos_dart);

private:
    // Variables membres
    double radius;
    std::vector<int> sectors;
    double radius_bullseye;
    double radius_outer_bullseye;
    double radius_double_inner;
    double radius_double_outer;
    double radius_triple_inner;
    double radius_triple_outer;
};

#endif
