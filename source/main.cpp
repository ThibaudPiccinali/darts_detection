#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>
#include <semaphore.h>
#include <sys/fcntl.h>
#include <iostream>
#include <sys/mman.h>
#include <sys/stat.h>
#include <opencv2/opencv.hpp>

#include "utils.h"
#include "object.h"
#include "vision.h"
#include "processing.h"

#define CAP1 2
#define CAP2 0

#define FILE_NAME_IMG_CAM1 "cam1.png"
#define FILE_NAME_IMG_CAM2 "cam2.png"

sem_t* demande_flech;
sem_t* score_flech;
sem_t* mvt_cam;
sem_t* image;
sem_t* cam;

struct SharedMemory {
    double position[2];  // Position avec un vecteur fixe de 2 doubles
};

SharedMemory* memoire;
int shm_fd;
size_t size = sizeof(SharedMemory);

void bye(void);
void gestion_partie(void);
void compute_position(void);
void gestion_camera(void);
void gestion_images(void);

int main() {
    pid_t pid[4];
    long no;
    
    // Création des MUTEX
    CHECK_S(demande_flech = sem_open("demande_flech",O_CREAT|O_EXCL,0666,0),"sem_open(demande_flech)");
    CHECK_S(score_flech = sem_open("score_flech",O_CREAT|O_EXCL,0666,0),"sem_open(score_flech)");
    CHECK_S(image = sem_open("image",O_CREAT|O_EXCL,0666,0),"sem_open(image)");
    CHECK_S(cam = sem_open("cam",O_CREAT|O_EXCL,0666,0),"sem_open(cam)");
    CHECK_S(mvt_cam = sem_open("mvt_cam",O_CREAT|O_EXCL,0666,0),"sem_open(mvt_cam)");
    
    // Permet de faire le cleanning des sémaphores lors des exits
    atexit(bye);// bye detruit les semaphores

    // Gestion de la mémoire partagée 
    CHECK(shm_fd = shm_open("memoire_partagee", O_CREAT | O_RDWR, 0666),"shm_open(memoire_partagee)");
    size = sysconf(_SC_PAGE_SIZE); 
    CHECK(ftruncate(shm_fd, size),"ftruncate(shm_fd)");
    CHECK_MAP(memoire = (SharedMemory*)mmap(0, size, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0),"mmap");

    // Avec ça le père sera "imunisé" au Ctrl-C mais pas ses fils (on va réactiver le SIGINT pour eux) ! 
    // Du coup ils vont tous se terminer, sauf le père qui va pouvoir les récupérer et terminer correctement est donc faire le nettoyage des sémaphores
    // Masque SIGINT pour le père
    sigset_t Mask,OldMask;
    CHECK(sigemptyset(&Mask), "sigemptyset()");
    CHECK(sigaddset(&Mask , SIGINT), "sigaddset(SIGINT)");
    CHECK(sigprocmask(SIG_SETMASK , &Mask , &OldMask), "sigprocmask()");

    // Création de l'ensemble des fils du processus père
    for(no = 0; no<4;no++){
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
                // Gestionnaire images
                gestion_images();
            }

        }
    }

    // Processus Père
    // Attente de la terminaison des threads
    for (int i = 0; i < 4; i++) {
        int status;
        CHECK(wait(&status), "wait()");
    }
    return 0;
}

void bye(void){
    // Fermeture et supression des sémaphores nommées
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
    
    // Suppression des mémoires partagés
    CHECK(munmap(memoire, size),"munmap(SharedMemory)");
    CHECK(close(shm_fd),"close(score)");
    CHECK(shm_unlink("memoire_partagee"),"shm_unlink(memoire_partagee)");

    CHECK(unlink(FILE_NAME_IMG_CAM1),"unlink(FILE_NAME_IMG_CAM1)");
    CHECK(unlink(FILE_NAME_IMG_CAM2),"unlink(FILE_NAME_IMG_CAM2)");
}

void gestion_partie(void){
    std::vector<Player> players = {Player(1, "Thibaud"), Player(2, "Bob")};
    Game game(players, 301);
    Dartboard board;
    int score;
    int scores[3];
    while(1){
        // Gestionnaire des fléchettes
        for (int i=0; i<3;i++){
            // On informe les autres processus qu'on peut jetter la fléchette
            CHECK(sem_post(demande_flech),"sem_post(demande_flech)");
            // On attends la position calculée soit prête
            CHECK(sem_wait(score_flech),"sem_wait(score_flech)");
            // On calcule le score

            std::vector<double> pos(memoire->position, memoire->position + 2); // On convertit au bon format de donnée pour mes fonctions
            
            score = board.compute_score(pos);
            game.last_darts_score.push_back(score);
            scores[i] = score;
            std::cout << "Score: " << score << std::endl;
        }
        // Gestionnaire de fin de tour
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
        std::copy(pos.begin(), pos.begin() + 2, memoire->position);

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

    CHECK(sem_post(cam),"sem_post(cam)");
    while(1){
        CHECK(sem_wait(cam),"sem_wait(cam)");

        // Capture de l'image de référence
        std::pair<cv::Mat, cv::Mat> images_ref_gray = get_gray_images_both_cameras(CAP1, CAP2);
        base_image_cam1_gray = images_ref_gray.first;
        base_image_cam2_gray = images_ref_gray.second;

        while (1){
            // Capture des images courantes
            std::pair<cv::Mat, cv::Mat> images_courantes_gray = get_gray_images_both_cameras(CAP1, CAP2);
            dart_image_cam1_gray = images_courantes_gray.first;
            dart_image_cam2_gray = images_courantes_gray.second;
            
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
void gestion_images(void){
    while(1){
        CHECK(sem_wait(demande_flech),"sem_wait(demande_flech)");
        CHECK(sem_wait(mvt_cam),"sem_wait(mvt_cam)");
        CHECK(sem_post(image),"sem_post(image)");
        CHECK(sem_post(cam),"sem_post(cam)");
    }
}