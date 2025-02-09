#ifndef VISION
#define VISION

#include <opencv2/opencv.hpp>

// Déclaration de la fonction
std::array<double, 2> get_coord_dart(
    const cv::Mat& diff_image_cam1, const cv::Mat& diff_image_cam2,
    bool DEBUG = false);

#endif // VISION
