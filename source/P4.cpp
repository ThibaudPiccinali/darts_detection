#include <opencv2/opencv.hpp>
#include <iostream>
#include "processing.h"
#include "vision.h"

int main() {
    // Déclare les matrices pour les images
    cv::Mat base_image_cam1_colors, base_image_cam2_colors;
    cv::Mat base_image_cam1_gray,base_image_cam2_gray;
    cv::Mat dart_image_cam1_colors, dart_image_cam2_colors;
    cv::Mat dart_image_cam1_gray,dart_image_cam2_gray;
    cv::Mat diff_image_cam1, diff_image_cam2;

    // Charger l'image en niveaux de gris
    // base_image_cam1_colors = cv::imread("tests/base_image_cam1_colors.png");
    // base_image_cam2_colors = cv::imread("tests/base_image_cam2_colors.png");
    // dart_image_cam1_colors = cv::imread("tests/dart_image_cam1_colors.png");
    // dart_image_cam2_colors = cv::imread("tests/dart_image_cam2_colors.png");

    // cv::cvtColor(base_image_cam1_colors, base_image_cam1_gray, cv::COLOR_BGR2GRAY);
    // cv::cvtColor(base_image_cam2_colors, base_image_cam2_gray, cv::COLOR_BGR2GRAY);
    // cv::cvtColor(dart_image_cam1_colors, dart_image_cam1_gray, cv::COLOR_BGR2GRAY);
    // cv::cvtColor(dart_image_cam2_colors, dart_image_cam2_gray, cv::COLOR_BGR2GRAY);

    // cv::imshow("base_image_cam1_gray",base_image_cam1_gray);
    // cv::imshow("base_image_cam2_gray",base_image_cam2_gray);
    // cv::imshow("dart_image_cam1_gray",dart_image_cam1_gray);
    // cv::imshow("dart_image_cam2_gray",dart_image_cam2_gray);

    // diff_image_cam1 = binary_diff_images(base_image_cam1_gray, dart_image_cam1_gray);
    // diff_image_cam2 = binary_diff_images(base_image_cam2_gray, dart_image_cam2_gray);
    
    diff_image_cam1 = cv::imread("tests/cam1.png");
    diff_image_cam2 = cv::imread("tests/cam2.png");

    cv::imshow("diff_image_cam1",diff_image_cam1);
    cv::imshow("diff_image_cam2",diff_image_cam2);

    cv::waitKey(0);
    cv::destroyAllWindows();

    cv::cvtColor(diff_image_cam2, diff_image_cam2, cv::COLOR_BGR2GRAY);
    cv::cvtColor(diff_image_cam1, diff_image_cam1, cv::COLOR_BGR2GRAY);

    std::vector<double> coords = get_coord_dart(diff_image_cam1,diff_image_cam2,true);
    // Affichage des éléments de l'array
    std::cout << "Coordonnées Dart: (" << coords[0] << ", " << coords[1] << ")" << std::endl;
    return 0;
}
