import cv2
import glob
import yaml
import time
import numpy as np

def open_stream(list_index,frame_width,frame_height):
    cap = [0 for i in range(len(list_index))]
    j = 0
    for i in list_index:
        cap[j] = cv2.VideoCapture(i)
        if not cap[j].isOpened():
            print(f"Erreur : impossible d'ouvrir la caméra {i}")
        else:
            # Forcer la résolution
            cap[j].set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
            cap[j].set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
        j +=1
    return cap

def get_frame(cap):
    ret, frame = cap.read()
    # Vérifie que la frame a bien été capturée
    if not ret:
        print(f"Erreur : impossible de lire l'image de la caméra {cap}")
    return frame

def calibrate_camera(images_folder):
    images_names = sorted(glob.glob(images_folder))
    images = []
    for imname in images_names:
        im = cv2.imread(imname, 1)
        images.append(im)
 
    #criteria used by checkerboard pattern detector.
    #Change this if the code can't find the checkerboard
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
 
    rows = 4 #number of checkerboard rows.
    columns = 7 #number of checkerboard columns.
    world_scaling = 3.19 #change this to the real world square size. Or not.
 
    #coordinates of squares in the checkerboard world space
    objp = np.zeros((rows*columns,3), np.float32)
    objp[:,:2] = np.mgrid[0:rows,0:columns].T.reshape(-1,2)
    objp = world_scaling* objp
 
    #frame dimensions. Frames should be the same size.
    width = images[0].shape[1]
    height = images[0].shape[0]
 
    #Pixel coordinates of checkerboards
    imgpoints = [] # 2d points in image plane.
 
    #coordinates of the checkerboard in checkerboard world space.
    objpoints = [] # 3d point in real world space
 
 
    for frame in images:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
 
        #find the checkerboard
        ret, corners = cv2.findChessboardCorners(gray, (rows, columns), None)
 
        if ret == True:
 
            #Convolution size used to improve corner detection. Don't make this too large.
            conv_size = (11, 11)
 
            #opencv can attempt to improve the checkerboard coordinates
            corners = cv2.cornerSubPix(gray, corners, conv_size, (-1, -1), criteria)
            cv2.drawChessboardCorners(frame, (rows,columns), corners, ret)
            cv2.imshow('img', frame)
            k = cv2.waitKey(50)
 
            objpoints.append(objp)
            imgpoints.append(corners)
 
 
 
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, (width, height), None, None)
    print('rmse:', ret)
    print('camera matrix:\n', mtx)
    print('distortion coeffs:', dist)
    # print('Rs:\n', rvecs)
    # print('Ts:\n', tvecs)
 
    return mtx, dist

def stereo_calibrate(mtx1, dist1, mtx2, dist2, frames_folder_cam1,frames_folder_cam2):
    #read the synched frames
    c1_images_names = sorted(glob.glob(frames_folder_cam1))
    c2_images_names = sorted(glob.glob(frames_folder_cam2))
 
    c1_images = []
    c2_images = []
    for im1, im2 in zip(c1_images_names, c2_images_names):
        _im = cv2.imread(im1, 1)
        c1_images.append(_im)
 
        _im = cv2.imread(im2, 1)
        c2_images.append(_im)

    #change this if stereo calibration not good.
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.0001)
 
    rows = 4 #number of checkerboard rows.
    columns = 7 #number of checkerboard columns.
    world_scaling = 3.19 #change this to the real world square size. Or not.
 
    #coordinates of squares in the checkerboard world space
    objp = np.zeros((rows*columns,3), np.float32)
    objp[:,:2] = np.mgrid[0:rows,0:columns].T.reshape(-1,2)
    objp = world_scaling* objp
 
    #frame dimensions. Frames should be the same size.
    width = c1_images[0].shape[1]
    height = c1_images[0].shape[0]
 
    #Pixel coordinates of checkerboards
    imgpoints_left = [] # 2d points in image plane.
    imgpoints_right = []
 
    #coordinates of the checkerboard in checkerboard world space.
    objpoints = [] # 3d point in real world space
 
    for frame1, frame2 in zip(c1_images, c2_images):
        gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        c_ret1, corners1 = cv2.findChessboardCorners(gray1, (rows, columns), None)
        c_ret2, corners2 = cv2.findChessboardCorners(gray2, (rows, columns), None)
 
        if c_ret1 == True and c_ret2 == True:
            corners1 = cv2.cornerSubPix(gray1, corners1, (11, 11), (-1, -1), criteria)
            corners2 = cv2.cornerSubPix(gray2, corners2, (11, 11), (-1, -1), criteria)
 
            cv2.drawChessboardCorners(frame1, (rows, columns), corners1, c_ret1)
            cv2.imshow('img', frame1)
 
            cv2.drawChessboardCorners(frame2, (rows, columns), corners2, c_ret2)
            cv2.imshow('img2', frame2)
            k = cv2.waitKey(50)
 
            objpoints.append(objp)
            imgpoints_left.append(corners1)
            imgpoints_right.append(corners2)
 
    stereocalibration_flags = cv2.CALIB_FIX_INTRINSIC
    ret, CM1, dist1, CM2, dist2, R, T, E, F = cv2.stereoCalibrate(objpoints, imgpoints_left, imgpoints_right, mtx1, dist1,
                                                                 mtx2, dist2, (width, height), criteria = criteria, flags = stereocalibration_flags)
 
    print('rmse:', ret)
    return R, T

def click_event(event, x, y, flags, params):
    img,points = params 
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'({x},{y})')
        points.append(np.array([[[x, y]]], dtype=np.float32))
        cv2.putText(img, f'({x},{y})',(x,y),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.circle(img, (x,y), 3, (0,255,255), -1)

def DLT(P1, P2, point1, point2):
 
    A = [point1[1]*P1[2,:] - P1[1,:],
         P1[0,:] - point1[0]*P1[2,:],
         point2[1]*P2[2,:] - P2[1,:],
         P2[0,:] - point2[0]*P2[2,:]
        ]
    A = np.array(A).reshape((4,4))
    #print('A: ')
    #print(A)
 
    B = A.transpose() @ A
    from scipy import linalg
    U, s, Vh = linalg.svd(B, full_matrices = False)
 
    # print('Triangulated point: ')
    # print(Vh[3,0:3]/Vh[3,3])
    return Vh[3,0:3]/Vh[3,3]

if __name__ == '__main__':
    
    with open("config.yaml", "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    # Récupérer les valeurs
    frame_width = data["frame_width"]
    frame_height = data["frame_height"]
    
    # Calibration des caméras (permet d'exporter matrice intrinséque et coefficients de distortion)
    mtx1, dist1 = calibrate_camera("setup_images/calibration/cam1/*")
    mtx2, dist2 = calibrate_camera("setup_images/calibration/cam2/*")

    # Permet d'obtenir la rotation et la translation de la caméra 2 par rapport à 1
    R, T = stereo_calibrate(mtx1, dist1, mtx2, dist2, "setup_images/synch/cam1/*","setup_images/synch/cam2/*")
    
    # Detmine le centre de la cible
    
    cap1,cap2= open_stream([0,2],frame_width,frame_height)
    _ = get_frame(cap1)
    _ = get_frame(cap2)
    time.sleep(1) 
    
    pixels_cam1 = get_frame(cap1)
    pixels_cam2 = get_frame(cap2)
    
    points_centre = []
    
    cv2.namedWindow('Cam1')
    cv2.setMouseCallback('Cam1', click_event,(pixels_cam1,points_centre))

    cv2.imshow('Cam1', pixels_cam1)
    cv2.waitKey(0)

    cv2.namedWindow('Cam2')
    cv2.setMouseCallback('Cam2', click_event,(pixels_cam2,points_centre))
    
    cv2.imshow('Cam2', pixels_cam2)
    cv2.waitKey(0)
    
    cv2.destroyAllWindows()
    
    R1 = np.eye(3)
    T1 = [[float(0)],[float(0)],[float(0)]]
    
    RT1 = np.concatenate([R1, T1], axis = -1)
    P1 = mtx1 @ RT1
    RT2 = np.concatenate([R, T], axis = -1)
    P2 = mtx2 @ RT2
    
    points_undistorted_1 = cv2.undistortPoints(points_centre[0], mtx1, dist1, None, mtx1)
    points_undistorted_2 = cv2.undistortPoints(points_centre[1], mtx2, dist2, None, mtx2)
        
    point_centre_reel = -DLT(P1,P2,points_undistorted_1[0][0],points_undistorted_2[0][0])
    
    # Structuration des données pour YAML
    data = {
        "frame_width": frame_width,
        "frame_height": frame_height,
        "camera1": {"intrinsics": mtx1.flatten().tolist(),"distortion_coeffs": dist1[0].tolist()},
        "camera2": {"intrinsics": mtx2.flatten().tolist(),"distortion_coeffs": dist2[0].tolist()},
        "rotation_cam1":R1.flatten().tolist(),
        "translation_cam1":[T1[0][0],T1[1][0],T1[2][0]],
        "rotation_cam2":R.flatten().tolist(),
        "translation_cam2":[T[0].tolist()[0],T[1].tolist()[0],T[2].tolist()[0]],
        "translation_centre_cible":point_centre_reel.tolist()
    }
    
    with open("config.yaml", "w", encoding="utf-8") as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)