#include <opencv2/opencv.hpp>
#include <iostream>
#include "processing.h"
#include "vision.h"
#include <unistd.h>

#define CAP1 2
#define CAP2 0

int main() {

    for(int i =1; i<16;i++){
            // Déclare les matrices pour les images
    cv::Mat base_image_cam1_gray, base_image_cam2_gray;
    cv::Mat dart_image_cam1_gray, dart_image_cam2_gray;

    std::pair<cv::Mat, cv::Mat> images_ref_gray = get_gray_images_both_cameras(CAP1, CAP2);
    base_image_cam1_gray = images_ref_gray.first;
    base_image_cam2_gray = images_ref_gray.second;
    std::string filename1 = "tests/" + std::to_string(i) + "/base_image_cam2_gray.png";
    std::string filename2 = "tests/" + std::to_string(i) + "/base_image_cam1_gray.png";
    cv::imwrite(filename1, base_image_cam2_gray);
    cv::imwrite(filename2, base_image_cam1_gray);

    printf("Goooo\n");
    sleep(5);

    std::pair<cv::Mat, cv::Mat> images_dart_gray = get_gray_images_both_cameras(CAP1, CAP2);
    dart_image_cam1_gray = images_dart_gray.first;
    dart_image_cam2_gray = images_dart_gray.second;
    std::string filename3 = "tests/" + std::to_string(i) + "/dart_image_cam1_gray.png";
    std::string filename4 = "tests/" + std::to_string(i) + "/dart_image_cam2_gray.png";
    cv::imwrite(filename3, dart_image_cam1_gray);
    cv::imwrite(filename4, dart_image_cam2_gray);
    printf("Finnn\n");
    sleep(10);
    }

}