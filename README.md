# H2V Algorithm Pipeline

This project implements a pipeline for converting horizontal videos (16:9) into vertical portrait videos (9:16) while keeping the main subject (determined via face detection) centered. The pipeline consists of three main stages:

1. **Scene/Shot Detection:** Uses [PySceneDetect](https://pyscenedetect.readthedocs.io/) to break the input video into shots.
2. **Face Detection / Subject Localization:** Uses [OpenCV](https://opencv.org/) to detect faces in each shot and computes an average bounding box for the main subject.
3. **Cropping & Concatenation with FFmpeg:** Uses FFmpeg (called via Python’s `subprocess` module) to crop each shot to a valid 9:16 region and then concatenates the cropped shots into one final portrait video. The cropping is performed by first cropping a native 9:16 region from a 1920x1080 source (608×1080) and then scaling that to the final desired resolution (e.g., 720×1280).

> **Note:** This pipeline assumes the source video is 1920×1080. If your source is different, you may need to update the cropping parameters accordingly or parse the source dimensions using FFprobe.



## How the Pipeline Works

1. **Scene/Shot Detection:**
   - The script in `shot_detection/detect_shots.py` uses PySceneDetect to parse the input video and determine shot boundaries based on content changes.
2. **Face Detection/Subject Localization:**
   - The script in `subject_detection/detect_subjects.py` processes each shot by reading frames between the detected boundaries.
   - It uses OpenCV’s Haar Cascade (provided as `haarcascade_frontalface_default.xml` in the `subject_detection/` folder) to find faces.
   - For each shot, an average face bounding box is computed to be used as the center point for cropping.
3. **Cropping & Concatenation with FFmpeg:**
   - The script in `ffmpeg_cropping/ffmpeg_crop.py` takes the shot data and determines a native crop region with a 9:16 aspect ratio.  
   - Since the native crop from a 1920×1080 video is limited to **608×1080** (to maintain the 9:16 ratio), the filter first crops to this size and then scales to your final desired output (e.g., 720×1280).
   - Finally, the cropped shots are concatenated into a final portrait video. Audio is re-encoded along with the video in the process.



## Usage

1. **Prepare Your Video and Cascade:**
   - Place your input video file (e.g., `sample_video.mp4`) in the `data/` folder.
   - Ensure the `haarcascade_frontalface_default.xml` file is in the `subject_detection/` folder.

2. **Run the Pipeline:**
   - From the project’s root directory, execute:
     ```bash
     python main.py
     ```
   - The script will:
     - Detect shot boundaries.
     - Detect the main subject (face) for each shot.
     - Crop each shot using FFmpeg (the cropped files are stored in `results/cropped_shots_ffmpeg/`).
     - Concatenate the cropped shots into a final portrait video stored in `results/final_portrait.mp4`.

3. **Playback:**
   - Open the final video file (`results/final_portrait.mp4`) with your favorite media player (e.g., VLC).


## Results

The results can be downloaded [here](https://drive.google.com/file/d/189rn4nm3FrQ_VSv2s_zGqBBNw9iCu6G_/view?usp=sharing)