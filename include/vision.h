#ifndef VISION
#define VISION

#include <opencv2/opencv.hpp>

// Déclaration de la fonction
std::vector<double> get_coord_dart(
    const cv::Mat& diff_image_cam1, const cv::Mat& diff_image_cam2,
    bool DEBUG = false);
std::pair<cv::Mat, cv::Mat> get_gray_images_both_cameras(int c1,int c2);

#endif // VISION
