#ifndef VISION
#define VISION

#include <opencv2/opencv.hpp>
#include <iostream>

std::pair<cv::Mat, cv::Mat> get_gray_images_both_cameras(int c1,int c2,int frame_width,int frame_height);
std::vector<double> get_coord_dart(const cv::Mat& diff_image_cam1, const cv::Mat& diff_image_cam2,int frame_height,const cv::Mat& K1,const cv::Mat& K2,const cv::Mat& RCAM1,const cv::Mat& TCAM1,const cv::Mat& RCAM2,const cv::Mat& TCAM2,const cv::Mat& T_target,const cv::Mat& dist1,const cv::Mat& dist2,bool DEBUG);

#endif
