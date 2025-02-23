#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>
#include <semaphore.h>
#include <sys/fcntl.h>
#include <iostream>
#include <sys/mman.h>
#include <sys/stat.h>
#include <opencv2/opencv.hpp>
#include <string>
#include <sys/socket.h>
#include <arpa/inet.h>
#include "json.hpp"

using json = nlohmann::json;

#include "utils.h"
#include "object.h"
#include "vision.h"
#include "processing.h"

#define CAP1 2
#define CAP2 0

#define LOCALPORT 8080
#define BUFFER_SIZE 1024
#define MAXCLIENTS 5

#define FILE_NAME_IMG_CAM1 "cam1.png"
#define FILE_NAME_IMG_CAM2 "cam2.png"

sem_t* acces_partie;
sem_t* start_game;
sem_t* demande_flech;
sem_t* score_flech;
sem_t* mvt_cam;
sem_t* image;
sem_t* cam;
sem_t* ask_clear_board;
sem_t* board_cleared;

Game* partie;
int shm_fd;
size_t size_game = sizeof(Game);

Dartboard* board;
int shm;
size_t size_board = sizeof(Dartboard);

void bye(void);
void gestion_partie(void);
void compute_position(void);
void gestion_camera(void);
void gestion_flechette(void);
void gestion_cible(void);
void gestion_port(void);

int main() {

    pid_t pid[6];
    long no;
    
    // Création des MUTEX
    CHECK_S(acces_partie = sem_open("acces_partie",O_CREAT|O_EXCL,0666,1),"sem_open(acces_partie)");
    CHECK_S(start_game = sem_open("start_game",O_CREAT|O_EXCL,0666,0),"sem_open(start_game)");
    CHECK_S(demande_flech = sem_open("demande_flech",O_CREAT|O_EXCL,0666,0),"sem_open(demande_flech)");
    CHECK_S(score_flech = sem_open("score_flech",O_CREAT|O_EXCL,0666,0),"sem_open(score_flech)");
    CHECK_S(image = sem_open("image",O_CREAT|O_EXCL,0666,0),"sem_open(image)");
    CHECK_S(cam = sem_open("cam",O_CREAT|O_EXCL,0666,0),"sem_open(cam)");
    CHECK_S(mvt_cam = sem_open("mvt_cam",O_CREAT|O_EXCL,0666,0),"sem_open(mvt_cam)");
    CHECK_S(ask_clear_board = sem_open("ask_clear_board",O_CREAT|O_EXCL,0666,0),"sem_open(ask_clear_board)");
    CHECK_S(board_cleared = sem_open("board_cleared",O_CREAT|O_EXCL,0666,0),"sem_open(board_cleared)");

    // Permet de faire le cleanning des sémaphores lors des exits
    atexit(bye);// bye detruit les semaphores

    // Gestion des mémoires partagées
    CHECK(shm = shm_open("board_partagee", O_CREAT | O_RDWR, 0666),"shm_open(board_partagee)");
    CHECK(ftruncate(shm, size_board),"ftruncate(shm_fd)");
    CHECK_MAP(board = (Dartboard*)mmap(0, size_board, PROT_READ | PROT_WRITE, MAP_SHARED, shm, 0),"mmap");

    CHECK(shm_fd = shm_open("partie_partagee", O_CREAT | O_RDWR, 0666),"shm_open(partie_partagee)");
    CHECK(ftruncate(shm_fd, size_game),"ftruncate(shm_fd)");
    CHECK_MAP(partie = (Game*)mmap(0, size_game, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0),"mmap");

    // Avec ça le père sera "imunisé" au Ctrl-C mais pas ses fils (on va réactiver le SIGINT pour eux) ! 
    // Du coup ils vont tous se terminer, sauf le père qui va pouvoir les récupérer et terminer correctement est donc faire le nettoyage des sémaphores
    // Masque SIGINT pour le père
    sigset_t Mask,OldMask;
    CHECK(sigemptyset(&Mask), "sigemptyset()");
    CHECK(sigaddset(&Mask , SIGINT), "sigaddset(SIGINT)");
    CHECK(sigprocmask(SIG_SETMASK , &Mask , &OldMask), "sigprocmask()");    

    // Création de l'ensemble des fils du processus père
    for(no = 0; no<6;no++){
        CHECK(pid[no]=fork(),"fork(pid[no])");
        if (pid[no]==0){
            // Démasque SIGINT
            CHECK(sigprocmask(SIG_SETMASK , &OldMask , NULL), "sigprocmask()");

            // On lance les processus fils           
            if (no == 0){
                // Gestionnaire de partie
                gestion_partie(); 
            }
            if(no== 1){
                // Calcul de la postion de la fléchette
                compute_position();
            }
            if (no == 2){
                // Gestionnaire de evenement caméra
                gestion_camera();
            }
            if (no == 3){
                // Gestionnaire de fléchette
                gestion_flechette();
            }
            if(no == 4){
                // Gestionnaire port communication
                gestion_port();
            }
            if(no ==5){
                // Gestionnaire de cible
                gestion_cible();
            }
        }
    }

    // Processus Père
    // Attente de la terminaison des threads
    for(int i = 0 ; i < 6; i ++){
        int status;
        CHECK(wait(&status), "wait()");
   }

    return 0;
}

void bye(void){
    // Fermeture et supression des sémaphores nommées
    CHECK(sem_close(acces_partie),"sem_close(acces_partie)");
    CHECK(sem_unlink("acces_partie"),"sem_unlink(acces_partie)");
    CHECK(sem_close(demande_flech),"sem_close(demande_flech)");
    CHECK(sem_unlink("demande_flech"),"sem_unlink(demande_flech)");
    CHECK(sem_close(score_flech),"sem_close(score_flech)");
    CHECK(sem_unlink("score_flech"),"sem_unlink(score_flech)");
    CHECK(sem_close(image),"sem_close(image)");
    CHECK(sem_unlink("image"),"sem_unlink(image)");
    CHECK(sem_close(cam),"sem_close(cam)");
    CHECK(sem_unlink("cam"),"sem_unlink(cam)");
    CHECK(sem_close(mvt_cam),"sem_close(mvt_cam)");
    CHECK(sem_unlink("mvt_cam"),"sem_unlink(mvt_cam)");
    CHECK(sem_close(start_game),"sem_close(start_game)");
    CHECK(sem_unlink("start_game"),"sem_unlink(start_game)");
    CHECK(sem_close(ask_clear_board),"sem_close(ask_clear_board)");
    CHECK(sem_unlink("ask_clear_board"),"sem_unlink(ask_clear_board)");
    CHECK(sem_close(board_cleared),"sem_close(board_cleared)");
    CHECK(sem_unlink("board_cleared"),"sem_unlink(board_cleared)");

    // Suppression des mémoires partagés
    CHECK(munmap(partie, size_game),"munmap(Game)");
    CHECK(close(shm_fd),"close(partie)");
    CHECK(shm_unlink("partie_partagee"),"shm_unlink(partie_partagee)");

    CHECK(munmap(board, size_board),"munmap(board)");
    CHECK(close(shm),"close(board)");
    CHECK(shm_unlink("board_partagee"),"shm_unlink(board_partagee)");

    CHECK(unlink(FILE_NAME_IMG_CAM1),"unlink(FILE_NAME_IMG_CAM1)");
    CHECK(unlink(FILE_NAME_IMG_CAM2),"unlink(FILE_NAME_IMG_CAM2)");
}

void gestion_partie(void){
    int score;
    int scores[3];
    // On attend que la partie se lance sur le site
    while(1){
        printf("Partie prête\n");
        CHECK(sem_wait(start_game),"sem_wait(start_game)");
        while(1){
            // Gestionnaire des fléchettes
            for(int i =0; i<3;i++){
                sleep(5);
                // On informe les autres processus qu'on peut jetter la fléchette
                CHECK(sem_post(demande_flech),"sem_post(demande_flech)");
                // On attends la position calculée soit prête
                CHECK(sem_wait(score_flech),"sem_wait(score_flech)");
                // On calcule le score
                CHECK(sem_wait(acces_partie),"sem_wait(acces_partie)");

                if(partie->reset ==1){
                    CHECK(sem_post(acces_partie),"sem_post(acces_partie)");
                    break;
                }

                std::vector<double> pos(partie->position, partie->position + 2); // On convertit au bon format de donnée pour mes fonctions
                score = board->compute_score(pos);
                partie->last_darts_score[i] = score;
                scores[i] = score;
                CHECK(sem_post(acces_partie),"sem_post(acces_partie)");
                std::cout << "Score: " << score << std::endl;
            }
            // Gestionnaire de fin de tour
            CHECK(sem_wait(acces_partie),"sem_wait(acces_partie)");
            if(partie->reset ==1){
                CHECK(sem_post(acces_partie),"sem_post(acces_partie)");
                break;
            }
            CHECK(sem_post(acces_partie),"sem_post(acces_partie)");

            // On demande si la cible est prête (le joueur à retiré les fléchettes)
            CHECK(sem_post(ask_clear_board),"sem_wait(ask_clear_board)");
            CHECK(sem_wait(board_cleared),"sem_post(board_cleared)");

            CHECK(sem_wait(acces_partie),"sem_wait(acces_partie)");
            if(partie->reset ==1){
                CHECK(sem_post(acces_partie),"sem_post(acces_partie)");
                break;
            }
            int score_tot = partie->last_darts_score[0] + partie->last_darts_score[1] + partie->last_darts_score[2];
            partie->scores[partie->index_current_player] = partie->scores[partie->index_current_player] - score_tot;
            partie->detailed_scores[partie->index_current_player][partie->n_tours[partie->index_current_player]] = score_tot;
            partie->n_tours[partie->index_current_player] = partie->n_tours[partie->index_current_player] + 1;
            partie->index_current_player = (partie->index_current_player + 1 )%partie->nb_player;
            partie->last_darts_score[0] = -1;
            partie->last_darts_score[1] = -1;
            partie->last_darts_score[2] = -1;
            CHECK(sem_post(acces_partie),"sem_post(acces_partie)");
        }
    CHECK(sem_wait(acces_partie),"sem_wait(acces_partie)");
    partie->reset = 0; // Le reset a bien été effectué
    CHECK(sem_post(acces_partie),"sem_post(acces_partie)");
    }
}
void compute_position(void){
    while(1){
        // On attends les images soient pretes
        CHECK(sem_wait(image),"sem_wait(image)");
        // On récupère les images dans les fichiers partagés
        
        cv::Mat diff_cam1 = cv::imread(FILE_NAME_IMG_CAM1);
        cv::Mat diff_cam2 = cv::imread(FILE_NAME_IMG_CAM2);
        cv::cvtColor(diff_cam1, diff_cam1, cv::COLOR_BGR2GRAY);
        cv::cvtColor(diff_cam2, diff_cam2, cv::COLOR_BGR2GRAY);

        std::vector<double> pos = get_coord_dart(diff_cam1,diff_cam2);
        std::cout << "Coordonnées Dart: (" << pos[0] << ", " << pos[1] << ")" << std::endl;
        CHECK(sem_wait(acces_partie),"sem_post(acces_partie)");
        std::copy(pos.begin(), pos.begin() + 2, partie->position);
        CHECK(sem_post(acces_partie),"sem_post(acces_partie)");
        CHECK(sem_post(score_flech),"sem_post(score_flech)");
    }
}
void gestion_camera(void){
    int count_cam1;
    int count_cam2;
    // Déclare les matrices pour les images
    cv::Mat base_image_cam1_gray,base_image_cam2_gray;
    cv::Mat dart_image_cam1_gray,dart_image_cam2_gray;
    cv::Mat diff_image_cam1, diff_image_cam2;

    while(1){
        CHECK(sem_wait(cam),"sem_wait(cam)");

        // Capture de l'image de référence
        // std::pair<cv::Mat, cv::Mat> images_ref_gray = get_gray_images_both_cameras(CAP1, CAP2);
        // base_image_cam1_gray = images_ref_gray.first;
        // base_image_cam2_gray = images_ref_gray.second;
        
        // Tests
        base_image_cam1_gray = cv::imread("tests/base_image_cam1_colors.png", cv::IMREAD_GRAYSCALE);
        base_image_cam2_gray = cv::imread("tests/base_image_cam2_colors.png", cv::IMREAD_GRAYSCALE);

        while (1){
            // Capture des images courantes
            // std::pair<cv::Mat, cv::Mat> images_courantes_gray = get_gray_images_both_cameras(CAP1, CAP2);
            // dart_image_cam1_gray = images_courantes_gray.first;
            // dart_image_cam2_gray = images_courantes_gray.second;
            
            // Tests
            dart_image_cam1_gray = cv::imread("tests/dart_image_cam1_colors.png", cv::IMREAD_GRAYSCALE);
            dart_image_cam2_gray = cv::imread("tests/dart_image_cam2_colors.png", cv::IMREAD_GRAYSCALE);

            // Calcul des différences
            diff_image_cam1 = binary_diff_images(base_image_cam1_gray, dart_image_cam1_gray);
            diff_image_cam2 = binary_diff_images(base_image_cam2_gray, dart_image_cam2_gray);
            // On les compte
            count_cam1 = cv::countNonZero(diff_image_cam1);
            count_cam2 = cv::countNonZero(diff_image_cam2);
            std::cout << "count_cam1 " <<count_cam1 << std::endl;
            std::cout << "count_cam2 " <<count_cam2 << std::endl;
            if(count_cam1 > 100 && count_cam2 >100){
                // Il y a bien une différence importante entre les deux images
                break;
            }
        }
        
        // On enregistre les images de différence dans l'espace partagé entre les processus
        
        cv::imwrite(FILE_NAME_IMG_CAM1,diff_image_cam1);
        cv::imwrite(FILE_NAME_IMG_CAM2,diff_image_cam2);
        CHECK(sem_post(mvt_cam),"sem_post(mvt_cam)");
    }
}
void gestion_flechette(void){
    while(1){
        CHECK(sem_wait(demande_flech),"sem_wait(demande_flech)");
        CHECK(sem_post(cam),"sem_post(cam)");
        CHECK(sem_wait(mvt_cam),"sem_wait(mvt_cam)");
        CHECK(sem_post(image),"sem_post(image)");
    }
}

void gestion_cible(void){
    while(1){
        CHECK(sem_wait(ask_clear_board),"sem_wait(ask_clear_board)");
        CHECK(sem_post(cam),"sem_post(cam)");
        CHECK(sem_wait(mvt_cam),"sem_wait(mvt_cam)");
        //sleep(10);// Tests
        CHECK(sem_post(board_cleared),"sem_post(board_cleared)");
    }
}

void gestion_port(void){
    int se;
    int erreur;
    int client_sd;
    int nbcar;
    struct sockaddr_in adrserveur;
    struct sockaddr_in adrclient;
    socklen_t adrclient_len = sizeof(adrclient);

    // Création de la socket d'écoute
    CHECK(se=socket(AF_INET, SOCK_STREAM, 0),"Erreur socket d'écoute non cree !!! \n");
    // Permet de réutiliser l'adresse
    int opt = 1;
    CHECK_0(setsockopt(se, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)),"setsockopt\n");
    // Preparation de l'adresse de la socket
    adrserveur.sin_family = AF_INET;
    adrserveur.sin_port = htons(LOCALPORT);
    adrserveur.sin_addr.s_addr = INADDR_ANY;
    //Affectation d'une adresse a la socket
    CHECK(erreur = bind(se, (const struct sockaddr *)&adrserveur, sizeof(adrserveur)),"Erreur de bind !!!\n");
    CHECK_0(listen(se, MAXCLIENTS),"Erreur listen !\n");

    std::string response;
    char buff_reception[BUFFER_SIZE];
    while(1){
        memset(buff_reception, 0, BUFFER_SIZE);
        CHECK(client_sd = accept(se, (struct sockaddr *)&adrclient, &adrclient_len),"Erreur de accept !!!\n");
        CHECK(nbcar = recv(client_sd, buff_reception, BUFFER_SIZE, 0),"Problème de réception !!!\n");
        
        std::string request(buff_reception);

        json j = json::parse(request);
        std::string command = j["command"];

        std::string response;
        if (command == "start") {

            if(j["players"].size() <= NB_MAX_PLAYERS){

                // Initialisation de la partie et de la dartboard
                CHECK(sem_wait(acces_partie),"sem_post(acces_partie)");
                partie->to_init(j);
                board->to_init(j);
                CHECK(sem_post(acces_partie),"sem_post(acces_partie)");

                // On lance la partie
                CHECK(sem_post(start_game),"sem_post(start_game)");
                json response_json = {{"output", "Success"}};
                std::string response_str = response_json.dump();
                send(client_sd, response_str.c_str(), response_str.size(), 0);
                CHECK(close(client_sd), "Erreur lors de la fermeture de la socket client");
            }
            else{
                json response_json = {{"output", "Erreur : Trop de joueurs"}};
                std::string response_str = response_json.dump();
                send(client_sd, response_str.c_str(), response_str.size(), 0);
            }
        }
        else if (command == "getdata") {  
            CHECK(sem_wait(acces_partie),"sem_post(acces_partie)");
            json response_json = partie->to_json();
            CHECK(sem_post(acces_partie),"sem_post(acces_partie)");
            std::string response_str = response_json.dump();
            send(client_sd, response_str.c_str(), response_str.size(), 0);
            }
        else if(command == "reset"){
            CHECK(sem_wait(acces_partie),"sem_post(acces_partie)");
            partie->to_reset();
            CHECK(sem_post(acces_partie),"sem_post(acces_partie)");
            // On relance la partie
            CHECK(sem_post(start_game),"sem_post(start_game)");
            json response_json = {{"output", "Success"}};
            std::string response_str = response_json.dump();
            send(client_sd, response_str.c_str(), response_str.size(), 0);
        }
        else if(command == "end"){
            CHECK(sem_wait(acces_partie),"sem_post(acces_partie)");
            partie->to_reset();
            CHECK(sem_post(acces_partie),"sem_post(acces_partie)");
            json response_json = {{"output", "Success"}};
            std::string response_str = response_json.dump();
            send(client_sd, response_str.c_str(), response_str.size(), 0);
        }
        else if (command =="change_score_dart"){
            CHECK(sem_wait(acces_partie),"sem_post(acces_partie)");
            partie->last_darts_score[atoi(j["dart_n"].get<std::string>().c_str())] = atoi(j["new_score"].get<std::string>().c_str());
            CHECK(sem_post(acces_partie),"sem_post(acces_partie)");
            json response_json = {{"output", "Success"}};
            std::string response_str = response_json.dump();
            send(client_sd, response_str.c_str(), response_str.size(), 0);
        }
        
    }
}