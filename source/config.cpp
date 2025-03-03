#include "config.h"

// Matrices intrinsèques des caméras
const cv::Mat K1 = (cv::Mat_<float>(3, 3) << 459.44732253f, 0.0f, 339.56888157f, 0.0f, 462.62071383f, 222.54341588f, 0.0f, 0.0f, 1.0f);
const cv::Mat K2 = (cv::Mat_<float>(3, 3) << 458.80917086f, 0.0f, 360.12752469f, 0.0f, 462.44782024f, 194.38816358f, 0.0f, 0.0f, 1.0f);

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