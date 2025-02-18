#ifndef OBJECT_H
#define OBJECT_H

#include <vector>
#include <opencv2/opencv.hpp>

#define NB_MAX_PLAYERS 10
#define MAX_CAR_NAME 50
#define MAX_TOURS 30
#define NB_SECTOR 20

#include <json.hpp>
using json = nlohmann::json;

struct Dartboard {

    void to_init(json data);
    int compute_score(std::vector<double> pos_dart);

    double radius;
    int sectors[NB_SECTOR];
    double radius_bullseye;
    double radius_outer_bullseye;
    double radius_double_inner;
    double radius_double_outer;
    double radius_triple_inner;
    double radius_triple_outer;
};

struct Game {
    char players[NB_MAX_PLAYERS][MAX_CAR_NAME];
    int nb_player;
    int game_mode;
    double position[2];  // Position avec un vecteur fixe de 2 doubles
    int index_current_player;
    int last_darts_score[3];
    int scores[NB_MAX_PLAYERS];
    int n_tours[NB_MAX_PLAYERS];
    int detailed_scores[NB_MAX_PLAYERS][MAX_TOURS];
    int reset; // 0 si aucune demande de reset enregistrée, 1 si oui
    void to_init(json data);
    json to_json() const;
    void to_reset(void);
};
#endif