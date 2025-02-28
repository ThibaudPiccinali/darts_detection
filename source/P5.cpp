#include <iostream>
#include <vector>
#include "processing.h"

int main() {
    cv::Mat base_image_cam1_gray;
    cv::Mat dart_image_cam1_gray;
    cv::Mat dart_image_cam1_colors;
    cv::Mat diff_image_cam1;
    cv::Mat diff_image_cam1_sans_haut;
    cv::Mat diff_image_cam1_sans_haut_sans_bas;

    base_image_cam1_gray = cv::imread("tests/base_image_cam1_colors.png", cv::IMREAD_GRAYSCALE);

    dart_image_cam1_gray = cv::imread("tests/dart_image_cam1_colors.png", cv::IMREAD_GRAYSCALE);
    diff_image_cam1 = binary_diff_images(base_image_cam1_gray, dart_image_cam1_gray);

    diff_image_cam1_sans_haut = filter_by_y(diff_image_cam1, 160);
    diff_image_cam1_sans_haut_sans_bas = filter_by_y(diff_image_cam1_sans_haut,-230);

    dart_image_cam1_colors = cv::imread("tests/dart_image_cam1_colors.png");

    cv::imshow("diff_image_cam1_sans_haut_sans_bas", diff_image_cam1_sans_haut_sans_bas);
    cv::waitKey(0);
    cv::destroyAllWindows();

    // Detection de la droite

    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(diff_image_cam1_sans_haut_sans_bas, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    if (contours.empty()) {
        std::cerr << "Aucun contour trouvé" << std::endl;
        return -1;
    }

    // Trouver le plus grand contour
    std::vector<cv::Point> contour = *std::max_element(contours.begin(), contours.end(),
        [](const std::vector<cv::Point>& a, const std::vector<cv::Point>& b) {
            return cv::contourArea(a) < cv::contourArea(b);
        });
    
    // Calculer les moments
    cv::Moments M = cv::moments(contour);
    int Cx = (M.m00 != 0) ? static_cast<int>(M.m10 / M.m00) : 0;
    int Cy = (M.m00 != 0) ? static_cast<int>(M.m01 / M.m00) : 0;

    // Convertir les points du contour pour PCA
    cv::Mat pointsMat(contour.size(), 2, CV_32F);
    for (size_t i = 0; i < contour.size(); i++) {
        pointsMat.at<float>(i, 0) = contour[i].x;
        pointsMat.at<float>(i, 1) = contour[i].y;
    }

    // Appliquer PCA
    cv::PCA pca(pointsMat, cv::Mat(), cv::PCA::DATA_AS_ROW);
    cv::Point2f eigenvector(pca.eigenvectors.at<float>(0, 0), pca.eigenvectors.at<float>(0, 1));
    double vx = eigenvector.x, vy = eigenvector.y;

    // Définir les points de la ligne
    int w = diff_image_cam1_sans_haut.cols;
    int h = diff_image_cam1_sans_haut.rows;

    cv::Point2f pt1(Cx - eigenvector.x * w, Cy - eigenvector.y * w);
    cv::Point2f pt2(Cx + eigenvector.x * w, Cy + eigenvector.y * w);

    // Tracer l'axe principal sur l'image
    cv::Mat output;
    cv::cvtColor(dart_image_cam1_gray, output, cv::COLOR_GRAY2BGR);
    cv::line(output, pt1, pt2, cv::Scalar(0, 0, 255), 2);
    cv::circle(output, cv::Point(Cx, Cy), 5, cv::Scalar(0, 255, 0), -1);

    // Afficher l'image
    cv::imshow("Tronc avec droite ajustée", output);
    cv::waitKey(0);
    cv::destroyAllWindows();
    
    // Filtrage
    cv::Mat filtered_image = cv::Mat::zeros(h, w, CV_8UC1);
    // Filtrage des pixels proches de la droite
    for (int x = 0; x < w; ++x) {
        for (int y = 0; y < h; ++y) {
            if (diff_image_cam1_sans_haut.at<uchar>(y, x) == 255) {
                double d = std::abs((x - Cx) * vy - (y - Cy) * vx);
                if (d <= 5) {
                    filtered_image.at<uchar>(y, x) = 255;
                }
            }
        }
    }
    // Filtrage median
    cv::medianBlur(filtered_image, filtered_image, 3);

    // Détection des composantes connectées
    cv::Mat labels, stats, centroids;
    int num_labels = cv::connectedComponentsWithStats(filtered_image, labels, stats, centroids, 8);
    int nb_points = 100;

    cv::Mat filtered_image_2 = cv::Mat::zeros(h, w, CV_8UC1);
    for (int i = 1; i < num_labels; ++i) { // Ignore le fond (label 0)
        if (stats.at<int>(i, cv::CC_STAT_AREA) >= nb_points) {
            filtered_image_2.setTo(255, labels == i);
        }
    }

    cv::imshow("filtered_image_2", filtered_image_2);
    cv::waitKey(0);
    cv::destroyAllWindows();

    // Extraction du point le plus bas
    cv::Point2f lowest_point_felchette = find_lowest_white_pixel(filtered_image_2);
    std::cout << "Le point le plus bas : " << lowest_point_felchette << std::endl;

    cv::circle(dart_image_cam1_colors, lowest_point_felchette, 3, cv::Scalar(0, 255, 0), -1);
    // Afficher l'image avec le cercle
    cv::imshow("Pointe flechette cam 1", dart_image_cam1_colors);
    cv::waitKey(0);
    cv::destroyAllWindows();
    return 0;
}
