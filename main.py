import os

from shot_detection.detect_shots import detect_scenes
from subject_detection.detect_subjects import detect_main_subject
from ffmpeg_cropping.ffmpeg_crop import crop_shots_with_ffmpeg, concat_videos_ffmpeg

def main():
    video_path = os.path.join("data", "sample_video.mp4")
    face_cascade_path = os.path.join("subject_detection", "haarcascade_frontalface_default.xml")
    results_dir = "results"
    cropped_shots_dir = os.path.join(results_dir, "cropped_shots_ffmpeg")
    final_output = os.path.join(results_dir, "final_portrait.mp4")

    # Create the results directory if it doesn't exist.
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    shots = detect_scenes(video_path, threshold=27.0, min_scene_len=15)
    print("=== Detected Shots ===")
    for i, (start_sec, end_sec) in enumerate(shots, start=1):
        print(f"  Shot {i}: {start_sec:.2f}s -> {end_sec:.2f}s")
    
    subject_info = detect_main_subject(video_path, shots, face_cascade_path)
    print("\n=== Average Face Bounding Box per Shot ===")
    for shot_idx, info in subject_info.items():
        print(f"  Shot {shot_idx}: start={info['start']:.2f}s, end={info['end']:.2f}s, crop_box={info['crop_box']}")
    
    print("\n[INFO] Cropping each shot with FFmpeg into 9:16 ...")
    cropped_files = crop_shots_with_ffmpeg(
        input_video=video_path,
        shots_data=subject_info,
        output_dir=cropped_shots_dir,
        final_width=720,    
        final_height=1280,  
        reencode=True
    )
    
    print("\n[INFO] Concatenating all cropped shots into the final portrait video ...")
    concat_videos_ffmpeg(cropped_files, final_output)

    print(f"\n[INFO] Pipeline complete! Final portrait video: {final_output}")

if __name__ == "__main__":
    main()
