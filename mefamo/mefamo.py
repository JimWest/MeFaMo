import cv2
import os
import mediapipe as mp
from mediapipe.python.solutions import face_mesh, drawing_utils, drawing_styles
import numpy as np
import socket
import threading
import time
import math
import transforms3d
import open3d as o3d

from pylivelinkface import PyLiveLinkFace, FaceBlendShape

from mefamo.utils.drawing import Drawing
from mefamo.blendshapes.blendshape_calculator import BlendshapeCalculator

# taken from: https://github.com/Rassibassi/mediapipeDemos
from mefamo.custom.face_geometry import (  # isort:skip
    PCF,
    get_metric_landmarks,
    procrustes_landmark_basis,
)

# points of the face model that will be used for SolvePnP later
points_idx = [33, 263, 61, 291, 199]
points_idx = points_idx + [key for (key, val) in procrustes_landmark_basis]
points_idx = list(set(points_idx))
points_idx.sort()

# Calculates the 3d rotation and 3d landmarks from the 2d landmarks
def calculate_rotation(face_landmarks, pcf: PCF, image_shape):
    frame_width, frame_height, channels = image_shape
    focal_length = frame_width
    center = (frame_width / 2, frame_height / 2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]],
        dtype="double",
    )

    dist_coeff = np.zeros((4, 1))

    landmarks = np.array(
        [(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark[:468]]

    )
    # print(landmarks.shape)
    landmarks = landmarks.T

    metric_landmarks, pose_transform_mat = get_metric_landmarks(
        landmarks.copy(), pcf
    )

    model_points = metric_landmarks[0:3, points_idx].T
    image_points = (
        landmarks[0:2, points_idx].T
        * np.array([frame_width, frame_height])[None, :]
    )

    success, rotation_vector, translation_vector = cv2.solvePnP(
        model_points,
        image_points,
        camera_matrix,
        dist_coeff,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )

    return pose_transform_mat, metric_landmarks, rotation_vector, translation_vector

   
class Mefamo():
    def __init__(self, input = 0, ip = '127.0.0.1', port = 11111, show_3d = False, hide_image = False, show_debug = False) -> None:

        self.input = input
        self.show_image = not hide_image
        self.show_3d = show_3d
        self.show_debug = show_debug

        self.face_mesh = face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

        self.live_link_face = PyLiveLinkFace(fps = 30, filter_size = 4)
        self.blendshape_calulator = BlendshapeCalculator()

        self.ip = ip
        self.upd_port = int(port)
        
        self.image_height, self.image_width, channels = (480, 640, 3)

        # pseudo camera internals
        focal_length = self.image_width
        center = (self.image_width / 2, self.image_height / 2)
        camera_matrix = np.array(
            [[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]],
            dtype="double",
        )

        self.pcf = PCF(
            near=1,
            far=10000,
            frame_height=self.image_height,
            frame_width=self.image_width,
            fy=camera_matrix[1, 1],
        )
        self.drawing_spec = drawing_utils.DrawingSpec(thickness=1, circle_radius=1)        
        self.lock = threading.Lock()
        self.got_new_data = False
        self.network_data = b''
        self.network_thread = threading.Thread(target=self._network_loop, daemon=True)
        self.image = None
    
    # starts the program and all its threads
    def start(self):        
        cap = None
        image = None

        # check if input is an image        
        if isinstance(self.input, str) and (self.input.lower().endswith(".jpg") or self.input.lower().endswith(".png")):
            image = cv2.imread(self.input)
            self.file = True   
        else:   
            input = self.input  
            try:
                input = int(self.input)
            except ValueError:
                input = self.input  

        if os.name == 'nt':
            # will improve webcam input startup on windows 
            cap = cv2.VideoCapture(input, cv2.CAP_DSHOW)   
        else:
            cap = cv2.VideoCapture(input)                

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.image_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.image_height)
        
        # run the network loop in a separate thread
        self.network_thread.start()

        if cap is not None:
            # for camera and videos
            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    continue
                if not self._process_image(image):
                    break    
            print("Video capture received no more frames.")                
            cap.release()
        
        else:
            # for input images
            while image is not None:
                if not self._process_image(image):
                    break

    def _network_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:            
            s.connect((self.ip, self.upd_port))
            while True: 
                with self.lock:
                    if self.got_new_data:                               
                        s.sendall(self.network_data)
                        self.got_new_data = False
                time.sleep(0.01)

    def _process_image(self, image):   
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image)

        # Draw the face mesh annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        face_image_3d = None
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:

                pose_transform_mat, metric_landmarks, rotation_vector, translation_vector = calculate_rotation(face_landmarks, self.pcf, image.shape)  
                # draw a 3d image of the face
                if self.show_3d:
                    face_image_3d = Drawing.draw_3d_face(metric_landmarks, image)

                # draw the face mesh 
                drawing_utils.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=drawing_styles
                    .get_default_face_mesh_tesselation_style())

                # draw the face contours
                drawing_utils.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=drawing_styles
                    .get_default_face_mesh_contours_style())
            
                 # draw iris points
                image = Drawing.draw_landmark_point(face_landmarks.landmark[468], image, color = (0, 0, 255))
                image = Drawing.draw_landmark_point(face_landmarks.landmark[473], image, color = (0, 255, 0))

                # calculate and set all the blendshapes                
                self.blendshape_calulator.calculate_blendshapes(
                    self.live_link_face, metric_landmarks[0:3].T, face_landmarks.landmark)

                # calculate the head rotation out of the pose matrix
                eulerAngles = transforms3d.euler.mat2euler(pose_transform_mat)
                pitch = -eulerAngles[0]
                yaw = eulerAngles[1]
                roll = eulerAngles[2]
                self.live_link_face.set_blendshape(
                    FaceBlendShape.HeadPitch, pitch)
                self.live_link_face.set_blendshape(
                    FaceBlendShape.HeadRoll, roll)
                self.live_link_face.set_blendshape(FaceBlendShape.HeadYaw, yaw)

        # Flip the image horizontally for a selfie-view display.
        self.image = cv2.flip(image, 1).astype('uint8')

        # Debug format settings
        white_bg = 0 * np.ones(shape=[720, 720, 3], dtype=np.uint8)
        text_coordinates = [25, 25]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.50
        color = (0, 255, 0)

        if self.show_image:
            cv2.imshow('MediaPipe Face Mesh', image.astype('uint8'))  
            if face_image_3d is not None and type(face_image_3d) == o3d.geometry.Image: 
                # show the 3d image if it exists
                img_3d = np.asarray(face_image_3d)
                img_3d = cv2.flip(img_3d, 1)
                cv2.imshow('Open3D Image', np.asarray(face_image_3d)) 

            if self.show_debug:
                for shape in FaceBlendShape:
                    shape_debug_text = f'{shape.name}: {self.live_link_face.get_blendshape(FaceBlendShape(shape.value)):.3f}'
                    cv2.putText(img=white_bg, text=shape_debug_text, org=tuple(text_coordinates), fontFace=font, fontScale=font_scale, color=color, thickness=1)
                    text_coordinates[1] += 20
                    if shape.value == 30: #start new column
                        text_coordinates = [300, 25]

                cv2.imshow('Debug', white_bg)

            if cv2.waitKey(1) & 0xFF == 27:
                return False

        with self.lock:
            self.got_new_data = True
            self.network_data = self.live_link_face.encode()

        return True
