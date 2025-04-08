import os
import unittest
import tempfile

from shot_detection.detect_shots import detect_scenes
from subject_detection.detect_subjects import detect_main_subject
from ffmpeg_cropping.ffmpeg_crop import crop_shots_with_ffmpeg, concat_videos_ffmpeg

class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Define paths used in tests.
        cls.video_path = os.path.join("data", "sample_video.mp4")
        cls.face_cascade = os.path.join("subject_detection", "haarcascade_frontalface_default.xml")
        
    @unittest.skipUnless(os.path.exists("data/sample_video.mp4"),
                         "sample_video.mp4 not found in data/ folder")
    def test_detect_scenes(self):
        """Test scene detection returns a list of (start, end) tuples."""
        scenes = detect_scenes(self.video_path, threshold=27.0, min_scene_len=15)
        self.assertIsInstance(scenes, list)
        if scenes:
            self.assertIsInstance(scenes[0], tuple)
            self.assertEqual(len(scenes[0]), 2)
    
    @unittest.skipUnless(os.path.exists(self.video_path) and os.path.exists(self.face_cascade),
                         "Required sample video or haar cascade not found")
    def test_detect_main_subject(self):
        """
        Test main subject detection returns a dictionary with expected keys
        for each shot. This test uses a minimal shot (e.g. 0 to 1 sec) for speed.
        """
        # Create a dummy shot list for a short segment.
        dummy_shots = [(0, 1)]
        subject_info = detect_main_subject(self.video_path, dummy_shots, self.face_cascade)
        self.assertIsInstance(subject_info, dict)
        # Each shot should have keys: 'start', 'end', and 'crop_box'
        for shot in subject_info.values():
            self.assertIn("start", shot)
            self.assertIn("end", shot)
            self.assertIn("crop_box", shot)
    
    def test_concat_videos_ffmpeg_empty(self):
        """
        Test that calling the concat function with an empty list raises an error.
        """
        with self.assertRaises(FileNotFoundError):
            # Since the list is empty, ffmpeg should fail to find files to concatenate.
            concat_videos_ffmpeg([], "dummy_output.mp4")
    
    def test_crop_shots_with_ffmpeg_invalid_video(self):
        """
        Test that passing a non-existent video file to crop_shots_with_ffmpeg raises an error.
        """
        with self.assertRaises(Exception):
            crop_shots_with_ffmpeg("non_existent_video.mp4", {}, tempfile.mkdtemp(), 
                                     final_width=720, final_height=1280, reencode=True)

if __name__ == '__main__':
    unittest.main()
