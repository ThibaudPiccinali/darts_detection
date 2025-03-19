#include "config.h"

// Matrices intrinsèques des caméras
const cv::Mat K1 = (cv::Mat_<float>(3, 3) << 690.14277479f, 0.0f, 676.04812155f, 0.0f, 691.13753231f, 343.43178529f, 0.0f, 0.0f, 1.0f);
const cv::Mat K2 = (cv::Mat_<float>(3, 3) << 690.19862724f, 0.0f, 676.3834275f, 0.0f, 689.99201574f, 302.30485088f, 0.0f, 0.0f, 1.0f);

// Transformation vers le référentiel des caméra (cam1)
const cv::Mat RCAM1 = cv::Mat::eye(3, 3, CV_32F); // Rotation de la caméra 1
const cv::Mat TCAM1 = (cv::Mat_<float>(3, 1) << 0.0f, 0.0f, 0.0f); // Translation de la caméra 1
    
const cv::Mat RCAM2 = (cv::Mat_<float>(3, 3) << 0.0f, 0.0f, 1.0f,
                                        0.0f, 1.0f, 0.0f,
                                        -1.0f, 0.0f, 0.0f); // Rotation de 90° sur Y

const cv::Mat TCAM2 = (cv::Mat_<float>(3, 1) << -29.55f, 0.0f, -29.55f); // Translation de la caméra 2

// Transformation vers le référentiel cible
const cv::Mat T = (cv::Mat_<double>(3, 1) << 0.0, 0.0, 30.0);
const cv::Mat R1 = (cv::Mat_<double>(3, 3) << -1.0, 0.0, 0.0,0.0, -1.0, 0.0f,0.0, 0.0, 1.0); // Rotation de 180° sur Z
const cv::Mat R2 = (cv::Mat_<double>(3, 3) << 1.0, 0.0, 0.0,0.0, -1.0, 0.0f,0.0, 0.0, -1.0); // Rotation 180° sur X