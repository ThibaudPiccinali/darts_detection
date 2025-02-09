#include <opencv2/opencv.hpp>
#include <iostream>

int main() {
    // Ouvre les deux caméras
    cv::VideoCapture cap1(0); // Première caméra
    cv::VideoCapture cap2(2); // Deuxième caméra

    // Vérifie si les caméras sont ouvertes correctement
    if (!cap1.isOpened()) {
        std::cerr << "Erreur : Impossible d'ouvrir la première caméra !" << std::endl;
        return -1;
    }
    if (!cap2.isOpened()) {
        std::cerr << "Erreur : Impossible d'ouvrir la deuxième caméra !" << std::endl;
        return -1;
    }

    // Déclare les matrices pour les images
    cv::Mat frame1, frame2;

    // Compteur pour les fichiers de sortie
    int frame_count = 0;

    while (true) {
        // Capture les images des deux caméras
        cap1 >> frame1;
        cap2 >> frame2;

        // Vérifie que les images sont valides
        if (frame1.empty() || frame2.empty()) {
            std::cerr << "Erreur : Une des caméras n'a pas fourni d'image valide !" << std::endl;
            break;
        }

        // Sauvegarde les images dans des fichiers
        std::string filename1 = "camera1_frame_" + std::to_string(frame_count) + ".png";
        std::string filename2 = "camera2_frame_" + std::to_string(frame_count) + ".png";
        cv::imwrite(filename1, frame1);
        cv::imwrite(filename2, frame2);

        // Incrémente le compteur de frames
        frame_count++;

        // Attends une touche pour continuer ou arrêter la capture
        char key = cv::waitKey(1);
        if (key == 27) { // 27 est la touche 'Esc'
            break;
        }
    }

    // Libère les caméras et ferme les fenêtres
    cap1.release();
    cap2.release();

    return 0;
}
