import cv2
import os

def detect_main_subject(video_path, shots, face_cascade_path):
    """
    For each shot, detect faces (per frame) and compute an 'average face bounding box'.
    We'll return a single bounding box per shot to be used for FFmpeg cropping.
    
    Args:
        video_path (str): Path to video file.
        shots (list): List of (start_sec, end_sec) shot boundaries.
        face_cascade_path (str): Path to Haar cascade XML file for face detection.
    
    Returns:
        dict: 
          {
            shot_idx: {
              "start": float,    # start time (sec)
              "end": float,      # end time (sec)
              "crop_box": (x, y, w, h) or None if no faces found,
            },
            ...
          }
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not os.path.isfile(face_cascade_path):
        raise FileNotFoundError(f"Haar cascade not found: {face_cascade_path}")

    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    
    # Open the video once
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    shot_data = {}
    
    for idx, (start_sec, end_sec) in enumerate(shots, start=1):
        start_frame = int(start_sec * fps)
        end_frame = int(end_sec * fps)

        centers = []  # list of (cx, cy)
        face_sizes = []  # list of (w, h) for main face in each frame

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        current_frame = start_frame
        
        while cap.isOpened() and current_frame <= end_frame:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) > 0:
                # pick the largest face
                (x, y, w, h) = max(faces, key=lambda box: box[2] * box[3])
                cx = x + w/2
                cy = y + h/2
                centers.append((cx, cy))
                face_sizes.append((w, h))
            
            current_frame += 1
        
        if len(centers) == 0:
            crop_box = None
        else:
            avg_cx = sum([c[0] for c in centers]) / len(centers)
            avg_cy = sum([c[1] for c in centers]) / len(centers)
            avg_w = sum([fs[0] for fs in face_sizes]) / len(face_sizes)
            avg_h = sum([fs[1] for fs in face_sizes]) / len(face_sizes)

            crop_box = (avg_cx - avg_w/2, avg_cy - avg_h/2, avg_w, avg_h)
        
        shot_data[idx] = {
            "start": start_sec,
            "end": end_sec,
            "crop_box": crop_box
        }

    cap.release()
    return shot_data
