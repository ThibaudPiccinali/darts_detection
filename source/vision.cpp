#include <opencv2/opencv.hpp>
#include <iostream>
#include "processing.h"

std::vector<double> get_coord_dart(
    const cv::Mat& diff_image_cam1, const cv::Mat& diff_image_cam2,
    bool DEBUG = false) {

    if (DEBUG) {
        cv::imshow("diff_image_cam1", diff_image_cam1);
        cv::imshow("diff_image_cam2", diff_image_cam2);
        cv::waitKey(0);
        cv::destroyAllWindows();
    }

    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(2, 2));
    cv::Mat opened_image_cam1, opened_image_cam2;
    cv::morphologyEx(diff_image_cam1, opened_image_cam1, cv::MORPH_OPEN, kernel);
    cv::morphologyEx(diff_image_cam2, opened_image_cam2, cv::MORPH_OPEN, kernel);

    if (DEBUG) {
        cv::imshow("opening cam 1", opened_image_cam1);
        cv::imshow("opening cam 2", opened_image_cam2);
        cv::waitKey(0);
        cv::destroyAllWindows();
    }

    cv::Mat filtered_image_cam1 = filter_by_centroid(opened_image_cam1, 250);
    cv::Mat filtered_image_cam2 = filter_by_centroid(opened_image_cam2, 250);

    cv::Point2f lowest_point_felchette_cam1 = find_lowest_white_pixel(filtered_image_cam1);
    cv::Point2f lowest_point_felchette_cam2 = find_lowest_white_pixel(filtered_image_cam2);

    if (DEBUG) {

        cv::imshow("filtered_image_cam1", filtered_image_cam1);
        cv::imshow("filtered_image_cam2", filtered_image_cam2);

        std::cout << "Le point le plus bas sur la caméra 1 : " << lowest_point_felchette_cam1 << std::endl;
        std::cout << "Le point le plus bas sur la caméra 2 : " << lowest_point_felchette_cam2 << std::endl;

        cv::circle(diff_image_cam1, lowest_point_felchette_cam1, 10, cv::Scalar(0, 255, 0), -1);
        // Afficher l'image avec le cercle
        cv::imshow("Pointe flechette cam 1", diff_image_cam1);
        cv::waitKey(0);
        cv::destroyAllWindows();

    }

    // Définir les matrices intrinsèques des caméras
    cv::Mat K1 = (cv::Mat_<float>(3, 3) << 459.44732253f, 0.0f, 339.56888157f, 0.0f, 462.62071383f, 222.54341588f, 0.0f, 0.0f, 1.0f);
    cv::Mat K2 = (cv::Mat_<float>(3, 3) << 458.80917086f, 0.0f, 360.12752469f, 0.0f, 462.44782024f, 194.38816358f, 0.0f, 0.0f, 1.0f);

    // Matrices extrinsèques (Rotation et Translation)
    // Origine -> Cam1
    cv::Mat R1 = cv::Mat::eye(3, 3, CV_32F); // Rotation de la caméra 1
    cv::Mat T1 = (cv::Mat_<float>(3, 1) << 0.0f, 0.0f, 0.0f); // Translation de la caméra 1
    
    cv::Mat R2 = (cv::Mat_<float>(3, 3) << 0.0f, 0.0f, 1.0f,
                                        0.0f, 1.0f, 0.0f,
                                        -1.0f, 0.0f, 0.0f); // Rotation de 90° sur Y
    cv::Mat T2 = (cv::Mat_<float>(3, 1) << -30.0f, 0.0f, -30.0f); // Translation de la caméra 2

    // Triangulation pour obtenir les points 3D
    cv::Mat points_2D_felchette = triangulate_point(K1, K2, R1, T1, R2, T2,lowest_point_felchette_cam1, lowest_point_felchette_cam2);

    // Transformation vers le référentiel cible
    cv::Mat T = (cv::Mat_<double>(3, 1) << 0, 0, 30);
    cv::Mat R3 = (cv::Mat_<double>(3, 3) << -1, 0, 0,0, -1, 0,0, 0, 1); // Rotation de 180° sur Z
    cv::Mat R4 = (cv::Mat_<double>(3, 3) << 1, 0, 0,0, -1, 0,0, 0, -1); // Rotation 180° sur X

    cv::Mat point3D_real = R4 * R3* points_2D_felchette + T;

    if (DEBUG) {
        // Affichage des résultats
        std::cout << "Coordonnées de la flechette (repère cam1) :\n";
        std::cout << points_2D_felchette<< std::endl;
        std::cout << "Coordonnées de la flechette (repère centre de la cible) :\n";
        std::cout << point3D_real << std::endl;
    }

    // Extraction des coordonnées
    std::vector<double> coords = {point3D_real.at<double>(0, 0), point3D_real.at<double>(0, 2)};
    return coords;
}

std::pair<cv::Mat, cv::Mat> get_gray_images_both_cameras(int c1,int c2){
    
    cv::Mat image_cam1_colors,image_cam2_colors;
    cv::Mat image_cam1_gray,image_cam2_gray;

    // Ouvre la première caméra
    cv::VideoCapture cap1(c1);
    if (!cap1.isOpened()) {
        std::cerr << "Erreur : Impossible d'ouvrir la première caméra !" << std::endl;
        throw std::runtime_error("Impossible d'ouvrir la première caméra");
    }

    // Définir la résolution de la caméra à 640x480
    cap1.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap1.set(cv::CAP_PROP_FRAME_HEIGHT, 480);

    cap1 >> image_cam1_colors;
    //image_cam1_colors = cropBottomTwoThirds(image_cam1_colors);
    cap1.release();  // On est obligé de fermer le flux sinon ça ne marche pas (Python ça marchait mieux)
        
    // Ouvre la deuxième caméra
    cv::VideoCapture cap2(c2);
    if (!cap2.isOpened()) {
        std::cerr << "Erreur : Impossible d'ouvrir la deuxième caméra !" << std::endl;
        throw std::runtime_error("Impossible d'ouvrir la première caméra");
    }

    // Définir la résolution de la caméra à 640x480
    cap2.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap2.set(cv::CAP_PROP_FRAME_HEIGHT, 480);

    cap2 >> image_cam2_colors;
    //image_cam2_colors = cropBottomTwoThirds(image_cam2_colors);
    cap2.release(); 
        
    // Conversion en nuance de gris
    cv::cvtColor(image_cam1_colors, image_cam1_gray, cv::COLOR_BGR2GRAY);
    cv::cvtColor(image_cam2_colors, image_cam2_gray, cv::COLOR_BGR2GRAY);

    return std::make_pair(image_cam1_gray, image_cam2_gray);
}
