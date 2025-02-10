#ifndef OBJECT_H
#define OBJECT_H

#include <vector>
#include <opencv2/opencv.hpp>

class Dartboard {
public:
    // Constructeur
    Dartboard(double radius = 21.5, 
              std::vector<int> sectors = {6, 13, 4, 18, 1, 20, 5, 12, 9, 14, 11, 8, 16, 7, 19, 3, 17, 2, 15, 10},
              double radius_bullseye = 1.5 / 2, double radius_outer_bullseye = 3.2 / 2,
              double radius_double_inner = 16, double radius_double_outer = 16.9,
              double radius_triple_inner = 9.5, double radius_triple_outer = 10.5);

    // Méthodes
    int compute_score(std::vector<double> pos_dart);
    void save_image_dart_on_board(const std::string& image_name, const std::vector<std::vector<float>>& darts);

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

class Player{

public:
    // Constructeur
    Player(int id, const std::string& nom);

    // Méthodes
    void display();
    std::unordered_map<std::string, std::string> to_dict() const;

    // Variables membres
    int id;
    const std::string& nom;
    int nb_party_played;
};

class Game {
    public:
        Game(std::vector<Player>& list_players, int game_mode);
        std::unordered_map<std::string, std::vector<std::unordered_map<std::string, std::string>>> to_dict() const;
        void display() const;

        std::vector<Player> players;
        std::vector<int> scores;
        std::vector<std::vector<int>> detailed_scores;
        int index_current_player;
        int can_play;
        int nb_player;
        std::vector<int> last_darts_score;
    };
#endif