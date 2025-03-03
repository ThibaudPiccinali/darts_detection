#include <opencv2/opencv.hpp>
#include <iostream>
#include "processing.h"
#include "config.h"

std::vector<double> get_coord_dart(
    const cv::Mat& diff_image_cam1, const cv::Mat& diff_image_cam2,
    bool DEBUG = false) {

    cv::Mat diff_image_cam1_sans_haut;
    cv::Mat diff_image_cam1_sans_haut_sans_bas;
    cv::Mat diff_image_cam2_sans_haut;
    cv::Mat diff_image_cam2_sans_haut_sans_bas;

    // On extrait la zone centrale
    
    diff_image_cam1_sans_haut = filter_by_y(diff_image_cam1, 160);
    diff_image_cam1_sans_haut_sans_bas = filter_by_y(diff_image_cam1_sans_haut,-230);

    diff_image_cam2_sans_haut = filter_by_y(diff_image_cam2, 160);
    diff_image_cam2_sans_haut_sans_bas = filter_by_y(diff_image_cam2_sans_haut,-230);
    
    if (DEBUG) {
        cv::imshow("diff_image_cam1", diff_image_cam1);
        cv::imshow("diff_image_cam2", diff_image_cam2);
        cv::imshow("diff_image_cam1_sans_haut_sans_bas", diff_image_cam1_sans_haut_sans_bas);
        cv::imshow("diff_image_cam2_sans_haut_sans_bas", diff_image_cam2_sans_haut_sans_bas);

        cv::waitKey(0);
        cv::destroyAllWindows();
    }

    // Detection de la droite

    std::vector<std::vector<cv::Point>> contours_cam1;
    std::vector<std::vector<cv::Point>> contours_cam2;

    cv::findContours(diff_image_cam1_sans_haut_sans_bas, contours_cam1, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
    cv::findContours(diff_image_cam2_sans_haut_sans_bas, contours_cam2, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    if (contours_cam1.empty()) {
        std::cerr << "Aucun contour trouvé sur la cam1" << std::endl;
        exit(EXIT_FAILURE);
    }
    if (contours_cam2.empty()) {
        std::cerr << "Aucun contour trouvé sur la cam1" << std::endl;
        exit(EXIT_FAILURE);
    }

    // Trouver le plus grand contour
    std::vector<cv::Point> contour_cam1 = *std::max_element(contours_cam1.begin(), contours_cam1.end(),
    [](const std::vector<cv::Point>& a, const std::vector<cv::Point>& b) {
        return cv::contourArea(a) < cv::contourArea(b);
    });
    // Trouver le plus grand contour
    std::vector<cv::Point> contour_cam2 = *std::max_element(contours_cam2.begin(), contours_cam2.end(),
    [](const std::vector<cv::Point>& a, const std::vector<cv::Point>& b) {
        return cv::contourArea(a) < cv::contourArea(b);
    });

    // Calculer les moments
    cv::Moments M_cam1 = cv::moments(contour_cam1);
    int Cx_cam1 = (M_cam1.m00 != 0) ? static_cast<int>(M_cam1.m10 / M_cam1.m00) : 0;
    int Cy_cam1 = (M_cam1.m00 != 0) ? static_cast<int>(M_cam1.m01 / M_cam1.m00) : 0;

    cv::Moments M_cam2 = cv::moments(contour_cam2);
    int Cx_cam2 = (M_cam2.m00 != 0) ? static_cast<int>(M_cam2.m10 / M_cam2.m00) : 0;
    int Cy_cam2 = (M_cam2.m00 != 0) ? static_cast<int>(M_cam2.m01 / M_cam2.m00) : 0;

    // Convertir les points du contour pour PCA
    cv::Mat pointsMat_cam1(contour_cam1.size(), 2, CV_32F);
    for (size_t i = 0; i < contour_cam1.size(); i++) {
        pointsMat_cam1.at<float>(i, 0) = contour_cam1[i].x;
        pointsMat_cam1.at<float>(i, 1) = contour_cam1[i].y;
    }

    cv::Mat pointsMat_cam2(contour_cam2.size(), 2, CV_32F);
    for (size_t i = 0; i < contour_cam2.size(); i++) {
        pointsMat_cam2.at<float>(i, 0) = contour_cam2[i].x;
        pointsMat_cam2.at<float>(i, 1) = contour_cam2[i].y;
    }

    // Appliquer PCA
    cv::PCA pca_cam1(pointsMat_cam1, cv::Mat(), cv::PCA::DATA_AS_ROW);
    cv::Point2f eigenvector_cam1(pca_cam1.eigenvectors.at<float>(0, 0), pca_cam1.eigenvectors.at<float>(0, 1));
    double vx_cam1 = eigenvector_cam1.x, vy_cam1 = eigenvector_cam1.y;

    cv::PCA pca_cam2(pointsMat_cam2, cv::Mat(), cv::PCA::DATA_AS_ROW);
    cv::Point2f eigenvector_cam2(pca_cam2.eigenvectors.at<float>(0, 0), pca_cam2.eigenvectors.at<float>(0, 1));
    double vx_cam2 = eigenvector_cam2.x, vy_cam2 = eigenvector_cam2.y;

    int w = diff_image_cam1_sans_haut.cols;
    int h = diff_image_cam1_sans_haut.rows;

    // Filtrage
    cv::Mat filtered_image_cam1 = cv::Mat::zeros(h, w, CV_8UC1);
    cv::Mat filtered_image_cam2 = cv::Mat::zeros(h, w, CV_8UC1);
    // Filtrage des pixels proches de la droite
    for (int x = 0; x < w; ++x) {
        for (int y = 0; y < h; ++y) {
            if (diff_image_cam1_sans_haut.at<uchar>(y, x) == 255) {
                double d = std::abs((x - Cx_cam1) * vy_cam1 - (y - Cy_cam1) * vx_cam1);
                if (d <= 5) {
                    filtered_image_cam1.at<uchar>(y, x) = 255;
                }
            }
            if (diff_image_cam2_sans_haut.at<uchar>(y, x) == 255) {
                double d = std::abs((x - Cx_cam2) * vy_cam2 - (y - Cy_cam2) * vx_cam2);
                if (d <= 5) {
                    filtered_image_cam2.at<uchar>(y, x) = 255;
                }
            }
        }
    }

    if(DEBUG){
        cv::imshow("Image_cam1_proche_axe_flechette", filtered_image_cam1);
        cv::imshow("Image_cam2_proche_axe_flechette", filtered_image_cam2);
        cv::waitKey(0);
        cv::destroyAllWindows();
    }

    cv::Mat labels_cam1, stats_cam1, centroids_cam1;
    int num_labels_cam1 = cv::connectedComponentsWithStats(filtered_image_cam1, labels_cam1, stats_cam1, centroids_cam1, 8);
    int nb_points_cam1 = 50;
    cv::Mat filtered_image_cam1_2 = cv::Mat::zeros(h, w, CV_8UC1);
    for (int i = 1; i < num_labels_cam1; ++i) { // Ignore le fond (label 0)
        if (stats_cam1.at<int>(i, cv::CC_STAT_AREA) >= nb_points_cam1) {
            filtered_image_cam1_2.setTo(255, labels_cam1 == i);
        }
    }

    cv::Mat labels_cam2, stats_cam2, centroids_cam2;
    int num_labels_cam2 = cv::connectedComponentsWithStats(filtered_image_cam2, labels_cam2, stats_cam2, centroids_cam2, 8);
    int nb_points_cam2 = 50;
    cv::Mat filtered_image_cam2_2 = cv::Mat::zeros(h, w, CV_8UC1);
    for (int i = 1; i < num_labels_cam2; ++i) { // Ignore le fond (label 0)
        if (stats_cam2.at<int>(i, cv::CC_STAT_AREA) >= nb_points_cam2) {
            filtered_image_cam2_2.setTo(255, labels_cam2 == i);
        }
    }

    if(DEBUG){
        cv::imshow("Image_cam1_proche_axe_flechette_filtre", filtered_image_cam1_2);
        cv::imshow("Image_cam2_proche_axe_flechette_filtre", filtered_image_cam2_2);
        cv::waitKey(0);
        cv::destroyAllWindows();
    }

    // Extraction du point le plus bas
    cv::Point2f lowest_point_felchette_cam1 = find_lowest_white_pixel(filtered_image_cam1_2);
    cv::Point2f lowest_point_felchette_cam2 = find_lowest_white_pixel(filtered_image_cam2_2);
    
    if(DEBUG){
        std::cout << "Le point le plus bas sur cam1 : " << lowest_point_felchette_cam1 << std::endl;
        std::cout << "Le point le plus bas sur cam2 : " << lowest_point_felchette_cam2 << std::endl;
    }

    // Triangulation pour obtenir les points 3D
    cv::Mat points_2D_felchette = triangulate_point(K1, K2, RCAM1, TCAM1, RCAM2, TCAM2,lowest_point_felchette_cam1, lowest_point_felchette_cam2);

    cv::Mat point3D_real = R2 * R1* points_2D_felchette + T;

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
