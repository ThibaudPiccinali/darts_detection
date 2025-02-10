#include <cmath>

#include <vector>
#include <string>
#include <iostream>
#include <opencv2/opencv.hpp>

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

void Dartboard::save_image_dart_on_board(const std::string& image_name, const std::vector<std::vector<float>>& darts) {
        int width = 800;
        int height = 800;
        cv::Mat image = cv::Mat::zeros(height, width, CV_8UC3);

        cv::Scalar black(0, 0, 0);
        cv::Scalar white(255, 255, 255);
        cv::Scalar green(0, 255, 0);
        cv::Scalar red(0, 0, 255);
        cv::Scalar yellow(0, 255, 255);

        cv::circle(image, cv::Point(width / 2, height / 2), static_cast<int>(radius * 10), black, -1);

        int segments = 20;
        double angle_step = 2 * M_PI / segments;

        for (int i = 0; i < segments; ++i) {
            double start_angle = i * angle_step;
            double end_angle = (i + 1) * angle_step;

            cv::ellipse(image, cv::Point(width / 2, height / 2), cv::Size(static_cast<int>(radius_double_outer * 10), static_cast<int>(radius_double_outer * 10)), 0,
                        start_angle * 180 / M_PI, end_angle * 180 / M_PI, i % 2 == 0 ? white : black, -1);

            cv::ellipse(image, cv::Point(width / 2, height / 2), cv::Size(static_cast<int>(radius_triple_outer * 10), static_cast<int>(radius_triple_outer * 10)), 0,
                        start_angle * 180 / M_PI, end_angle * 180 / M_PI, i % 2 == 0 ? green : red, -1);

            cv::ellipse(image, cv::Point(width / 2, height / 2), cv::Size(static_cast<int>(radius_double_outer * 10), static_cast<int>(radius_double_outer * 10)), 0,
                        start_angle * 180 / M_PI, end_angle * 180 / M_PI, i % 2 == 0 ? green : red, -1);
        }

        cv::circle(image, cv::Point(width / 2, height / 2), static_cast<int>(radius_outer_bullseye * 10), green, -1);
        cv::circle(image, cv::Point(width / 2, height / 2), static_cast<int>(radius_bullseye * 10), red, -1);

        for (int i = 0; i < segments; ++i) {
            double angle = (i + 0.5) * angle_step;
            int x = static_cast<int>(width / 2 + (radius_double_outer + 1.5) * 10 * std::cos(angle));
            int y = static_cast<int>(height / 2 + (radius_double_outer + 1.5) * 10 * std::sin(angle));
            cv::putText(image, std::to_string(sectors[i]), cv::Point(x, y), cv::FONT_HERSHEY_SIMPLEX, 0.5, white, 2);
        }

        for (const auto& dart : darts) {
            if (!dart.empty() && dart[0] != NAN && dart[1] != NAN) {
                int x = static_cast<int>(width / 2 + dart[0] * 10);
                int y = static_cast<int>(height / 2 - dart[1] * 10);
                cv::circle(image, cv::Point(x, y), 5, yellow, -1);
            }
        }

        cv::imwrite(image_name, image);
    }


Player::Player(int id, const std::string& nom) : id(id), nom(nom), nb_party_played(0) {}

void Player::display() {
    std::cout << "---------- " << nom << " ----------" << std::endl;
    std::cout << "ID : " << id << std::endl;
    std::cout << "Nombre de partie jouée(s) : " << nb_party_played << std::endl;
}

std::unordered_map<std::string, std::string> Player::to_dict() const{
    return {
        {"id", std::to_string(id)},
        {"nom", nom},
        {"nb_party_played", std::to_string(nb_party_played)}
    };
}

Game::Game(std::vector<Player>& list_players, int game_mode)
            : players(list_players),
              scores(list_players.size(), game_mode),
              detailed_scores(list_players.size()),
              index_current_player(0),
              can_play(0),
              nb_player(list_players.size()),
              last_darts_score({-1, -1, -1})
        {
            for (auto& player : players) {
                player.nb_party_played += 1;
            }
        }
    
        std::unordered_map<std::string, std::vector<std::unordered_map<std::string, std::string>>> Game::to_dict() const {
            std::vector<std::unordered_map<std::string, std::string>> players_dict;
            for (const auto& player : players) {
                players_dict.push_back(player.to_dict());
            }
            std::vector<std::unordered_map<std::string, std::string>> scores_dict;
            for (int score : scores) {
                scores_dict.push_back({{"value", std::to_string(score)}});
            }

            std::vector<std::unordered_map<std::string, std::string>> last_darts_score_dict;
            for (int score : last_darts_score) {
                last_darts_score_dict.push_back({{"value", std::to_string(score)}});
            }
            return {
                {"players", players_dict},
                {"scores", scores_dict},
                {"detailed_scores", std::vector<std::unordered_map<std::string, std::string>>{}},
                {"index_current_player", { {{"value", std::to_string(index_current_player)}} }},
                {"nb_player", { {{"value", std::to_string(nb_player)}} }},
                {"can_play", { {{"value", std::to_string(can_play)}} }},
                {"last_darts_score", last_darts_score_dict}
            };
        }
    
        void Game::display() const {
            for (size_t i = 0; i < players.size(); ++i) {
                std::cout << players[i].nom << " | ";
                for (int score : detailed_scores[i]) {
                    std::cout << score << " | ";
                }
                std::cout << "Total : " << scores[i] << std::endl;
            }
        }