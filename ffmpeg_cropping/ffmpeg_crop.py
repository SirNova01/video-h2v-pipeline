# # File: my_h2v_project/ffmpeg_cropping/ffmpeg_crop.py

# import os
# import math
# import subprocess

# def crop_shots_with_ffmpeg(
#     input_video, 
#     shots_data, 
#     output_dir,
#     crop_width=720, 
#     crop_height=1280,
#     reencode=True
# ):
#     """
#     Crops each shot using FFmpeg, producing one file per shot, and returns the file paths.
    
#     Args:
#         input_video (str): Path to original video.
#         shots_data (dict): The result from detect_main_subject() e.g.:
#           {
#             shot_idx: {
#               "start": float,
#               "end": float,
#               "crop_box": (x, y, w, h) or None
#             },
#             ...
#           }
#         output_dir (str): Directory to store cropped shot outputs.
#         crop_width (int): Desired width for portrait (9:16).
#         crop_height (int): Desired height for portrait (9:16).
#         reencode (bool): If True, we'll re-encode with libx264. If False, we do -c copy for video.
#                          (But -c copy won't let you crop, so you generally must re-encode.)
    
#     Returns:
#         list of str: Paths to cropped shot files.
#     """
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
    
#     cropped_paths = []
    
#     # Sort shots by their start time
#     sorted_shots = sorted(shots_data.items(), key=lambda x: x[1]['start'])
    
#     for shot_idx, shot_info in sorted_shots:
#         start_sec = shot_info["start"]
#         end_sec = shot_info["end"]
#         duration = end_sec - start_sec
        
#         # We'll define a default center if crop_box is None
#         crop_box = shot_info["crop_box"]
        
#         # We'll assume we know the source video resolution. If you need it, parse with ffprobe or pass it in.
#         # For 9:16, we place the center at crop_box center (if we have it),
#         # and clamp so we stay in bounds. But let's keep it simple here:
#         if crop_box is not None:
#             (face_x, face_y, face_w, face_h) = crop_box
#             # The center of the face
#             cx = face_x + face_w/2
#             cy = face_y + face_h/2
#         else:
#             # If no face, just center the crop in the middle of the frame, 
#             # but we don't know the source resolution here, so let's guess 1920x1080
#             # (Better: get actual from ffprobe or from your detection code)
#             src_w, src_h = 1920, 1080
#             cx = src_w/2
#             cy = src_h/2
        
#         # We'll compute top-left corner:
#         crop_x = int(cx - crop_width/2)
#         crop_y = int(cy - crop_height/2)
        
#         # clamp to [0, src_w - crop_width] etc. (Again, we need actual W,H.)
#         # For simplicity, let's assume 1920x1080 (you can get real dims from detection or ffprobe)
#         src_w, src_h = 1920, 1080
#         crop_x = max(0, min(crop_x, src_w - crop_width))
#         crop_y = max(0, min(crop_y, src_h - crop_height))
        
#         # Prepare FFmpeg command
#         # -ss {start_sec} to seek
#         # -t {duration} to limit
#         # -vf "crop={crop_width}:{crop_height}:{crop_x}:{crop_y}"
#         # If reencode, we do -c:v libx264 -c:a aac (or copy audio)
#         # If not reencoding, we can't crop without reencode, so let's assume reencode = True
#         filter_str = f"crop={crop_width}:{crop_height}:{crop_x}:{crop_y}"
        
#         shot_output = os.path.join(output_dir, f"shot_{shot_idx}_cropped.mp4")
        
#         if reencode:
#             cmd = [
#                 "ffmpeg",
#                 "-y",               # overwrite
#                 "-ss", str(start_sec),
#                 "-i", input_video,
#                 "-t", str(duration),
#                 "-vf", filter_str,
#                 "-c:v", "libx264",  # re-encode with H.264
#                 "-crf", "23",       # quality
#                 "-preset", "medium",
#                 "-c:a", "aac",      # re-encode audio
#                 "-strict", "experimental",
#                 shot_output
#             ]
#         else:
#             # Not recommended if cropping, but as an example:
#             cmd = [
#                 "ffmpeg",
#                 "-y",
#                 "-ss", str(start_sec),
#                 "-i", input_video,
#                 "-t", str(duration),
#                 "-vf", filter_str,
#                 "-c:v", "copy",
#                 "-c:a", "copy",
#                 shot_output
#             ]
        
#         print(f"[INFO] Cropping Shot {shot_idx}: {start_sec:.2f}s to {end_sec:.2f}s")
#         subprocess.run(cmd, check=True)
#         cropped_paths.append(shot_output)
    
#     return cropped_paths


# def concat_videos_ffmpeg(cropped_paths, output_file):
#     """
#     Concatenate multiple videos into one using FFmpeg's concat demuxer.
    
#     Args:
#         cropped_paths (list of str): The path to each cropped video, in order.
#         output_file (str): Path for final combined file.
#     """
#     # We'll write out a temporary list file for FFmpeg's concat demuxer
#     list_file = "concat_list.txt"
#     with open(list_file, "w") as f:
#         for p in cropped_paths:
#             # Each line in the list file: file 'path/to/file'
#             f.write(f"file '{os.path.abspath(p)}'\n")
    
#     # -f concat -safe 0 -i list_file -c copy output.mp4
#     cmd = [
#         "ffmpeg",
#         "-y",
#         "-f", "concat",
#         "-safe", "0",
#         "-i", list_file,
#         "-c:v", "libx264",  # re-encode or copy. We'll re-encode to ensure consistent parameters
#         "-c:a", "aac",
#         output_file
#     ]
#     print("[INFO] Concatenating cropped shots into final video...")
#     subprocess.run(cmd, check=True)

#     # Remove the temp list file if you like
#     os.remove(list_file)





































# File: my_h2v_project/ffmpeg_cropping/ffmpeg_crop.py

import os
import subprocess

def crop_shots_with_ffmpeg(
    input_video, 
    shots_data, 
    output_dir,
    final_width=720, 
    final_height=1280,
    reencode=True
):
    """
    For each shot, crop using FFmpeg with a valid native crop region from a 1920x1080 source,
    then scale up to the desired output (e.g. 720x1280). Returns the file paths of cropped shots.
    
    Args:
        input_video (str): Path to the original video.
        shots_data (dict): The result from detect_main_subject(), e.g.:
          {
            shot_idx: {
              "start": float,
              "end": float,
              "crop_box": (x, y, w, h) or None
            },
            ...
          }
        output_dir (str): Directory for the cropped shot outputs.
        final_width (int): Desired final video width (e.g. 720).
        final_height (int): Desired final video height (e.g. 1280).
        reencode (bool): Must be True because cropping requires re-encoding.
    
    Returns:
        list of str: Paths to the cropped shot files.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    cropped_paths = []
    
    # For this example, we assume the source video is 1920x1080.
    # (You can obtain actual dimensions via FFprobe if needed.)
    src_w, src_h = 1920, 1080

    # The largest native 9:16 crop you can get from 1080 height is:
    native_crop_h = src_h                # 1080
    native_crop_w = int(round(src_h * (9/16)))  # ≈608
    
    # Process shots in chronological order.
    sorted_shots = sorted(shots_data.items(), key=lambda x: x[1]['start'])
    
    for shot_idx, shot_info in sorted_shots:
        start_sec = shot_info["start"]
        end_sec = shot_info["end"]
        duration = end_sec - start_sec
        
        # Use the provided crop_box if available; otherwise, default to center.
        crop_box = shot_info["crop_box"]
        if crop_box is not None:
            # crop_box = (face_x, face_y, face_w, face_h)
            face_x, face_y, face_w, face_h = crop_box
            # Center of the face.
            cx = face_x + face_w / 2
            cy = face_y + face_h / 2
        else:
            # Default center is the center of the source.
            cx = src_w / 2
            cy = src_h / 2
        
        # Calculate the top-left corner of the native crop.
        crop_x = int(cx - native_crop_w / 2)
        crop_y = int(cy - native_crop_h / 2)
        
        # Clamp so the crop does not extend beyond the source.
        crop_x = max(0, min(crop_x, src_w - native_crop_w))
        crop_y = max(0, min(crop_y, src_h - native_crop_h))
        
        # Build the filter: first crop the native 9:16 region (608x1080), then scale to final resolution.
        filter_str = f"crop={native_crop_w}:{native_crop_h}:{crop_x}:{crop_y},scale={final_width}:{final_height}"
        
        shot_output = os.path.join(output_dir, f"shot_{shot_idx}_cropped.mp4")
        
        if reencode:
            cmd = [
                "ffmpeg",
                "-y",               # overwrite output file if it exists
                "-ss", str(start_sec),
                "-i", input_video,
                "-t", str(duration),
                "-vf", filter_str,
                "-c:v", "libx264",  # re-encode video using H.264
                "-crf", "23",       # quality level (lower is better quality)
                "-preset", "medium",
                "-c:a", "aac",      # re-encode audio
                "-strict", "experimental",
                shot_output
            ]
        else:
            # Cropping requires re-encoding, so generally reencode should be True.
            cmd = [
                "ffmpeg",
                "-y",
                "-ss", str(start_sec),
                "-i", input_video,
                "-t", str(duration),
                "-vf", filter_str,
                "-c:v", "copy",
                "-c:a", "copy",
                shot_output
            ]
        
        print(f"[INFO] Cropping Shot {shot_idx}: {start_sec:.2f}s to {end_sec:.2f}s")
        subprocess.run(cmd, check=True)
        cropped_paths.append(shot_output)
    
    return cropped_paths


def concat_videos_ffmpeg(cropped_paths, output_file):
    """
    Concatenate multiple videos into a single final video using FFmpeg's concat demuxer.
    
    Args:
        cropped_paths (list of str): Paths to each cropped shot video, in order.
        output_file (str): Path for the final concatenated output.
    """
    # Write a temporary file list for FFmpeg.
    list_file = "concat_list.txt"
    with open(list_file, "w") as f:
        for p in cropped_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    
    # Build and run the FFmpeg command to concatenate.
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        output_file
    ]
    print("[INFO] Concatenating cropped shots into final video...")
    subprocess.run(cmd, check=True)
    
    os.remove(list_file)
