from mediapipe.python.solutions import face_mesh, drawing_utils, drawing_styles
import open3d as o3d
import open3d.visualization.rendering as rendering
import cv2

def draw_landmark_point(landmark, image, color = (255, 0, 0), radius = 5):
    try:
        image_rows, image_cols, _ = image.shape
        keypoint_px = drawing_utils._normalized_to_pixel_coordinates(landmark.x, landmark.y,
                                image_cols, image_rows)
        center_coordinates = (int(keypoint_px[0]), int(keypoint_px[1]))
        return cv2.circle(image, center_coordinates, radius, color, 2)
    except Exception as e:
        print(e)
        return image

def draw_3d_face(landmarks, image):
    # create pointcloid with open3d
    frame_width, frame_height, channels = image.shape
    try:
        render = rendering.OffscreenRenderer(frame_width, frame_height)        
        vector = o3d.utility.Vector3dVector(landmarks[0:3].T)
        pcd = o3d.geometry.PointCloud(vector)
        #o3d.visualization.draw_geometries([pcd])
        yellow = rendering.MaterialRecord()
        yellow.base_color = [1.0, 0.75, 0.0, 1.0]
        yellow.shader = "defaultLit"
        render.scene.add_geometry("pcd", pcd, yellow)
        # Optionally set the camera field of view (to zoom in a bit)
        vertical_field_of_view = 15.0  # between 5 and 90 degrees
        aspect_ratio = frame_width / frame_height  # azimuth over elevation
        near_plane = 0.1
        far_plane = 150
        fov_type = o3d.visualization.rendering.Camera.FovType.Vertical
        render.scene.camera.set_projection(vertical_field_of_view, aspect_ratio, near_plane, far_plane, fov_type)

        # Look at the origin from the front (along the -Z direction, into the screen), with Y as Up.
        center = [0, 0, 0]  # look_at target
        eye = [0, 0, 80]  # camera position
        up = [0, 1, 0]  # camera orientation
        render.scene.camera.look_at(center, eye, up)
        render.scene.set_background([0, 0, 0, 0])

        img = render.render_to_image()
        return img
    except Exception as e:
        print(e)
        