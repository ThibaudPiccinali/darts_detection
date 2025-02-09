#ifndef PROCESSING
#define PROCESSING

#include <opencv2/opencv.hpp>

// Déclaration de la fonction
cv::Mat binary_diff_images(const cv::Mat& pixels_list_a, const cv::Mat& pixels_list_b);
cv::Mat cropBottomTwoThirds(const cv::Mat& image);
cv::Point2d center_of_mass(const cv::Mat& image);
cv::Mat filter_by_centroid(const cv::Mat& image, double radius);
cv::Point find_lowest_white_pixel(const cv::Mat& image);
cv::Mat triangulate_point(const cv::Mat& K1, const cv::Mat& K2, const cv::Mat& R1, const cv::Mat& T1,
    const cv::Mat& R2, const cv::Mat& T2, const cv::Point2f& pt1, const cv::Point2f& pt2);

#endif // PROCESSING
