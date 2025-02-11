#include <opencv2/opencv.hpp>
#include <iostream>
#include "processing.h"
#include "vision.h"
#include <unistd.h>

int main() {

    // int count_cam1;
    // int count_cam2;

    // // Déclare les matrices pour les images
    // cv::Mat base_image_cam1_colors, base_image_cam2_colors;
    // cv::Mat base_image_cam1_gray,base_image_cam2_gray;
    // cv::Mat dart_image_cam1_colors, dart_image_cam2_colors;
    // cv::Mat dart_image_cam1_gray,dart_image_cam2_gray;
    // cv::Mat diff_image_cam1, diff_image_cam2;

    // // Ouvre la première caméra
    // cv::VideoCapture cap1(2);
    // if (!cap1.isOpened()) {
    //     std::cerr << "Erreur : Impossible d'ouvrir la première caméra !" << std::endl;
    //     return -1;
    // }
    // cap1 >> base_image_cam1_colors;
    // base_image_cam1_colors = cropBottomTwoThirds(base_image_cam1_colors);
    // cap1.release();  // On est obligé de fermer le flux sinon ça ne marche pas (Python ça marchait mieux)

    // // Ouvre la deuxième caméra
    // cv::VideoCapture cap2(0);
    // if (!cap2.isOpened()) {
    //     std::cerr << "Erreur : Impossible d'ouvrir la deuxième caméra !" << std::endl;
    //     return -1;
    // }
    // cap2 >> base_image_cam2_colors;
    // base_image_cam2_colors = cropBottomTwoThirds(base_image_cam2_colors);
    // cap2.release(); 

    // // Conversion en nuance de gris
    // cv::cvtColor(base_image_cam1_colors, base_image_cam1_gray, cv::COLOR_BGR2GRAY);
    // cv::cvtColor(base_image_cam2_colors, base_image_cam2_gray, cv::COLOR_BGR2GRAY);

    // while(true){

    //     cv::VideoCapture cap1(2);
    //     if (!cap1.isOpened()) {
    //         std::cerr << "Erreur : Impossible d'ouvrir la première caméra !" << std::endl;
    //         return -1;
    //     }
    //     cap1 >> dart_image_cam1_colors;
    //     dart_image_cam1_colors = cropBottomTwoThirds(dart_image_cam1_colors);
    //     cap1.release(); 
    //     cv::VideoCapture cap2(0);
    //     if (!cap2.isOpened()) {
    //         std::cerr << "Erreur : Impossible d'ouvrir la deuxième caméra !" << std::endl;
    //         return -1;
    //     }
    //     cap2 >> dart_image_cam2_colors;
    //     dart_image_cam2_colors = cropBottomTwoThirds(dart_image_cam2_colors);
    //     cap2.release(); 

    //     // Conversion en nuance de gris
    //     cv::cvtColor(dart_image_cam1_colors, dart_image_cam1_gray, cv::COLOR_BGR2GRAY);
    //     cv::cvtColor(dart_image_cam2_colors, dart_image_cam2_gray, cv::COLOR_BGR2GRAY);

    //     diff_image_cam1 = binary_diff_images(base_image_cam1_gray, dart_image_cam1_gray);
    //     diff_image_cam2 = binary_diff_images(base_image_cam2_gray, dart_image_cam2_gray);

    //     count_cam1 = cv::countNonZero(diff_image_cam1);
    //     count_cam2 = cv::countNonZero(diff_image_cam2);

    //     if(count_cam1 > 100 || count_cam2 >100){
    //         // Il y a bien une différence entre les deux images
    //         break;
    //     }
    //     std::cout << "Pas de mouvement détecté" << std::endl;
    //     std::cout << "count_cam1 : " << count_cam1 << std::endl;
    //     std::cout << "count_cam2 : " << count_cam2 << std::endl;
    //     sleep(5);
    // }
    // std::cout << "Mouvement détecté" << std::endl;
    // std::cout << "count_cam1 : " << count_cam1 << std::endl;
    // std::cout << "count_cam2 : " << count_cam2 << std::endl;
    // cv::imwrite("base_cam1.png", base_image_cam1_gray);
    // cv::imwrite("Difference_cam1.png", diff_image_cam1);
    // cv::imwrite("Darts_cam1.png", dart_image_cam1_gray);
    // cv::imwrite("base_cam2.png", base_image_cam2_gray);
    // cv::imwrite("Difference_cam2.png", diff_image_cam2);
    // cv::imwrite("Darts_cam2.png", dart_image_cam2_gray);
    int cap1 = 2;
    int cap2 = 0;
    std::pair<cv::Mat, cv::Mat> images_courantes_gray = get_gray_images_both_cameras(cap1, cap2);
    cv::Mat dart_image_cam1_gray = images_courantes_gray.first;
    cv::Mat dart_image_cam2_gray = images_courantes_gray.second;
    cv::imwrite("cam_1_gray.png",dart_image_cam1_gray);
    cv::imwrite("cam_2_gray.png",dart_image_cam2_gray);
}