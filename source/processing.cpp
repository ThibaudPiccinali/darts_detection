#include "processing.h"

cv::Mat binary_diff_images(const cv::Mat& pixels_list_a, const cv::Mat& pixels_list_b) {
    if (pixels_list_a.size() != pixels_list_b.size()) {
        throw std::invalid_argument("Les images doivent avoir la même taille");
    }

    cv::Mat diff, result;
    cv::absdiff(pixels_list_a, pixels_list_b, diff);  // Différence absolue pixel par pixel
    cv::threshold(diff, result, 30, 255, cv::THRESH_BINARY);  // Seuillage

    return result;
}

cv::Mat filter_by_y(const cv::Mat& image, int y_ref) {
    cv::Mat filtered_image = cv::Mat::zeros(image.size(), image.type());
    int h = image.rows;
    int w = image.cols;

    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            if (y_ref > 0) {
                if (y > y_ref && image.at<uchar>(y, x) == 255) {
                    filtered_image.at<uchar>(y, x) = 255;
                }
            } else {
                if (y < h + y_ref && image.at<uchar>(y, x) == 255) {
                    filtered_image.at<uchar>(y, x) = 255;
                }
            }
        }
    }

    return filtered_image;
}

cv::Point2d center_of_mass(const cv::Mat& image) {
    std::vector<cv::Point> coordinates;
    cv::findNonZero(image, coordinates);  // Trouve tous les pixels blancs
    
    if (coordinates.empty()) {
        return cv::Point2d(0, 0);  // Si l'image est vide, retour (0,0)
    }

    cv::Point2d center(0, 0);
    for (const auto& point : coordinates) {
        center.x += point.x;
        center.y += point.y;
    }
    center.x /= coordinates.size();
    center.y /= coordinates.size();
    
    return center;
}

cv::Mat filter_by_centroid(const cv::Mat& image, double radius) {
    cv::Mat filtered_image = cv::Mat::zeros(image.size(), CV_8U);
    cv::Point2d center = center_of_mass(image);

    for (int y = 0; y < image.rows; ++y) {
        for (int x = 0; x < image.cols; ++x) {
            if (image.at<uchar>(y, x) == 255) {  // Vérifie si c'est un pixel blanc
                double distance = cv::norm(cv::Point2d(x, y) - center);
                if (distance <= radius) {
                    filtered_image.at<uchar>(y, x) = 255;
                }
            }
        }
    }
    return filtered_image;
}

cv::Point find_lowest_white_pixel(const cv::Mat& image) {
    for (int y = image.rows - 1; y >= 0; --y) {
        for (int x = 0; x < image.cols; ++x) {
            if (image.at<uchar>(y, x) == 255) {
                return cv::Point(x, y);  // Retourne le premier pixel blanc trouvé en bas
            }
        }
    }
    return cv::Point(-1, -1);  // Retourne un point invalide si aucun pixel blanc trouvé
}

cv::Mat triangulate_point(const cv::Mat& K1, const cv::Mat& K2, const cv::Mat& R1, const cv::Mat& T1,
    const cv::Mat& R2, const cv::Mat& T2, const cv::Point2f& pt1, const cv::Point2f& pt2) {
    // Calcul des matrices de projection pour chaque caméra
    cv::Mat P1 = cv::Mat::zeros(3, 4, CV_32F);
    cv::Mat P2 = cv::Mat::zeros(3, 4, CV_32F);

    // Matrice de projection pour la première caméra
    cv::hconcat(R1, T1, P1);
    P1 = K1 * P1;

    // Matrice de projection pour la deuxième caméra
    cv::hconcat(R2, T2, P2);
    P2 = K2 * P2;

    // Points 2D dans les images (en homogène)
    cv::Mat points1(2, 1, CV_32F);
    cv::Mat points2(2, 1, CV_32F);

    points1.at<float>(0, 0) = pt1.x;
    points1.at<float>(1, 0) = pt1.y;
    
    points2.at<float>(0, 0) = pt2.x;
    points2.at<float>(1, 0) = pt2.y;

    // Effectuer la triangulation des points
    cv::Mat points3D;
    cv::triangulatePoints(P1, P2, points1, points2, points3D);

    // Convertir en coordonnées cartésiennes
    cv::Mat points3D_cart;
    points3D.rowRange(0, 3).copyTo(points3D_cart); // Copier les trois premières lignes

    // Convertir la quatrième ligne en CV_64F avant de faire la division
    cv::Mat points3D_w = points3D.row(3);
    points3D_w.convertTo(points3D_w, CV_64F); // Conversion du type

    // Diviser par la quatrième ligne (coordonnées homogènes)
    points3D_cart = points3D_cart / points3D_w;

    // Vérifier le type après la conversion
    points3D_cart.convertTo(points3D_cart, CV_64F);

return points3D_cart;
}