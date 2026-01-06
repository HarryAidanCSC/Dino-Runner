from utils.fix_dpi_scaling import fix_dpi_scaling

fix_dpi_scaling()

from setup_chrome_macro import setup_chrome_macro
import time
from ScreenRecorder import ScreenRecorder
import keyboard
from FrameProcessor import FrameProcessor
import mss

# Get the dino game ready
setup_chrome_macro()
time.sleep(0.8)

frame_processor = FrameProcessor()
screen_recorder = ScreenRecorder(
    dino_template_path="assets/template_dino.png",
    replay_template_path="assets/template_replay.png",
)

time.sleep(0.3)

# Start the game
keyboard.press_and_release("space")

frame_count = 0
with mss.mss() as sct:
    while True:
        frame_count += 1
        img = screen_recorder.grab_frame(sct)

        if frame_processor.should_jump(img):
            keyboard.press("space")
            time.sleep(0.03)
            keyboard.release("space")

        # Check if game has finished every 200 frames.
        if frame_count % 200 == 0:
            # Reset for next round if game is over
            if screen_recorder.is_run_over(sct=sct):
                keyboard.press_and_release("space")
