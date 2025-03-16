#include "object.h"

void Dartboard::to_init(json data) {
    radius = strtod(data["radius"].get<std::string>().c_str(), NULL);
    for (int i = 0; i< NB_SECTOR ; i++){
        sectors[i] = atoi(data["sectors"][i].get<std::string>().c_str());
    }
    radius_bullseye = strtod(data["radius_bullseye"].get<std::string>().c_str(), NULL);
    radius_outer_bullseye = strtod(data["radius_outer_bullseye"].get<std::string>().c_str(), NULL);
    radius_double_inner = strtod(data["radius_double_inner"].get<std::string>().c_str(), NULL);
    radius_double_outer = strtod(data["radius_double_outer"].get<std::string>().c_str(), NULL);
    radius_triple_inner = strtod(data["radius_triple_inner"].get<std::string>().c_str(), NULL);
    radius_triple_outer = strtod(data["radius_triple_outer"].get<std::string>().c_str(), NULL);
}

int Dartboard:: compute_score(std::vector<double> pos_dart) {
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

void Game::to_init(json data) {
    nb_player = data["players"].size();
    game_mode = atoi(data["game_mode"].get<std::string>().c_str());
    for (int i = 0; i < nb_player; ++i) {
        std::strcpy(players[i], data["players"][i].get<std::string>().c_str());
        scores[i] = game_mode;
        n_tours[i] = 0;
        for (int j = 0; j <MAX_TOURS;j++){
            detailed_scores[i][j] = -1;
        }
    }
    position[0] = -999;
    position[1] = 999;
    index_current_player = 0;
    last_darts_score[0] = -1;
    last_darts_score[1] = -1;
    last_darts_score[2] = -1;
    reset = 0;
}

void Game::to_reset(void){
    for (int i = 0; i < nb_player; ++i) {
        scores[i] = game_mode;
        n_tours[i] = 0;
        for (int j = 0; j <MAX_TOURS;j++){
            detailed_scores[i][j] = -1;
        }
    }
    position[0] = -999;
    position[1] = 999;
    index_current_player = 0;
    last_darts_score[0] = -1;
    last_darts_score[1] = -1;
    last_darts_score[2] = -1;
    reset = 1;
}

json Game::to_json() const {
    json j;
    j["nb_player"] = nb_player;
    j["game_mode"] = game_mode;
    j["position"] = {position[0], position[1]};
    j["index_current_player"] = index_current_player;

    json players_array = json::array();
    for (int i = 0; i < nb_player; i++) {
        players_array.push_back(std::string(players[i]));
    }
    j["players"] = players_array;

    j["last_darts_score"] = {last_darts_score[0], last_darts_score[1], last_darts_score[2]};

    json scores_array = json::array();
    json tours_array = json::array();
    for (int i = 0; i < nb_player; i++) {
        if (scores[i] >= 0) {
            scores_array.push_back(scores[i]);
        }
        if (n_tours[i] >= 0) {
            tours_array.push_back(n_tours[i]);
        }
    }
    j["scores"] = scores_array;
    j["n_tours"] = tours_array;

    json detailed_scores_array = json::array();
    for (int i = 0; i < nb_player; i++) {
        json player_scores = json::array();
        for (int j = 0; detailed_scores[i][j] >= 0; j++) {
            player_scores.push_back(detailed_scores[i][j]);
        }
        detailed_scores_array.push_back(player_scores);
    }
    j["detailed_scores"] = detailed_scores_array;

    return j;
}