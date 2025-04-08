import os
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

def detect_scenes(video_path, threshold=27.0, min_scene_len=15):
    """
    Detect scene/shot boundaries in the given video using PySceneDetect.
    
    Args:
        video_path (str): Path to input video file.
        threshold (float): Sensitivity for scene detection.
        min_scene_len (int): Minimum length of a scene in frames.
    
    Returns:
        List of (start_sec, end_sec) for each shot.
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold, min_scene_len=min_scene_len))

    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)

    scene_list = scene_manager.get_scene_list()
    scenes_seconds = []
    fps = video_manager.get_framerate()

    for scene in scene_list:
        start_frame = scene[0].get_frames()
        end_frame = scene[1].get_frames()

        start_time = start_frame / fps
        end_time = end_frame / fps

        scenes_seconds.append((start_time, end_time))

    video_manager.release()
    return scenes_seconds
