import cv2
import mediapipe as mp
import os

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import matplotlib.pyplot as plt
from mediapipe import solutions
import time
import datetime as dt



def draw_landmarks_on_image(rgb_image, detection_result):
  face_landmarks_list = detection_result.face_landmarks
  annotated_image = np.copy(rgb_image)

  # Loop through the detected faces to visualize.
  for idx in range(len(face_landmarks_list)):
    face_landmarks = face_landmarks_list[idx]

    # Draw the face landmarks.
    face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    face_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in face_landmarks
    ])

    solutions.drawing_utils.draw_landmarks(
        image=annotated_image,
        landmark_list=face_landmarks_proto,
        connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp.solutions.drawing_styles
        .get_default_face_mesh_tesselation_style())
    solutions.drawing_utils.draw_landmarks(
        image=annotated_image,
        landmark_list=face_landmarks_proto,
        connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp.solutions.drawing_styles
        .get_default_face_mesh_contours_style())
    solutions.drawing_utils.draw_landmarks(
        image=annotated_image,
        landmark_list=face_landmarks_proto,
        connections=mp.solutions.face_mesh.FACEMESH_IRISES,
          landmark_drawing_spec=None,
          connection_drawing_spec=mp.solutions.drawing_styles
          .get_default_face_mesh_iris_connections_style())

  return annotated_image


def plot_face_blendshapes_bar_graph(face_blendshapes):
  # Extract the face blendshapes category names and scores.
  face_blendshapes_names = [face_blendshapes_category.category_name for face_blendshapes_category in face_blendshapes]
  face_blendshapes_scores = [face_blendshapes_category.score for face_blendshapes_category in face_blendshapes]
  # The blendshapes are ordered in decreasing score value.
  face_blendshapes_ranks = range(len(face_blendshapes_names))

  fig, ax = plt.subplots(figsize=(12, 12))
  bar = ax.barh(face_blendshapes_ranks, face_blendshapes_scores, label=[str(x) for x in face_blendshapes_ranks])
  ax.set_yticks(face_blendshapes_ranks, face_blendshapes_names)
  ax.invert_yaxis()

  # Label each bar with values
  for score, patch in zip(face_blendshapes_scores, bar.patches):
    plt.text(patch.get_x() + patch.get_width(), patch.get_y(), f"{score:.4f}", va="top")

  ax.set_xlabel('Score')
  ax.set_title("Face Blendshapes")
  plt.tight_layout()
  plt.show()

def getting_eye_val(detection_result):
    # print(detection_result)
    try:
       faceblendshapes = detection_result.face_blendshapes[0]
    except Exception as e:
       print(e)
       return None
    eyes_data = faceblendshapes[9:22]
    return eyes_data
    
    

def run(path):
  base_options = python.BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task')

  options = vision.FaceLandmarkerOptions(base_options=base_options,
                                        output_face_blendshapes=True,
                                        output_facial_transformation_matrixes=True,
                                        num_faces=1)

  detector = vision.FaceLandmarker.create_from_options(options)

  ch_frames=0
  nch_frames=0


  print('Proctoring started...')



  cap = cv2.VideoCapture(path)
  # print('Check 1')
  ret, img = cap.read()
  # print('Check 2')
  # cv2.imshow('image',img)
  thresh = img.copy()
  # print('Check 3')

  while(True):
      ret, img = cap.read()
      if not ret:
         break
      cv2.imwrite("buffer.jpg",img=img)

      image = mp.Image.create_from_file("buffer.jpg")
      detection_result = detector.detect(image)
      eye_data = getting_eye_val(detection_result=detection_result)
      if eye_data is None:
        break
      thresholds = [0.75, 0.75,2.5, 2.5,0.75, 0.75, 0.50, 0.50, 0.50,0.50,0.50,0.50,0.75]
      preds = [i.score for i in eye_data]
      # print(eye_data)
      font = cv2.FONT_HERSHEY_SIMPLEX
      font_scale = 1.5

      # Define the color and thickness of the text
      color = (255, 0, 0)  # BGR color (blue in this example)
      thickness = 2

      # Define the position to start writing the text
      position = (50, 50)
      is_cheating = False
      for pred,threshs in zip(preds, thresholds):
          if pred>threshs:
              is_cheating=True
              # print(preds)
              # print(pred)
      if is_cheating:
        ch_frames+=1
        print("look in the screennnn")
        text = "cheaterrrr detected"
      else:
        nch_frames+=1
        print("good good")
        text = "good"

      #   cv2.imshow("image", img)
      
      # annotated_img = draw_landmarks_on_image(image.numpy_view(), detection_result)
      # cv2.imshow("detection_res", annotated_img)
      # cv2.putText(img, text, position, font, font_scale, color, thickness)
      # cv2.imshow("image", img)

      if cv2.waitKey(1) & 0xFF ==ord('q'):
          return ch_frames,nch_frames

  cap.release()
  cv2.destroyAllWindows()
  return ch_frames,nch_frames

def score(path):
   chf,nchf= run(path)
   print('Cheating Frames: ',chf)
   print('No cheating Frames: ',nchf)

# score('video.mp4')