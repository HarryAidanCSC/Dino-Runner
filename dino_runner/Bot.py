from utils.fix_dpi_scaling import fix_dpi_scaling

fix_dpi_scaling()

from setup_chrome_macro import setup_chrome_macro
import time
from ScreenRecorder import ScreenRecorder
import keyboard
from FrameProcessor import FrameProcessor
import mss
import statistics
import gc


class Bot:
    """Bot to orchestrate the dino."""

    def __init__(self) -> None:
        """Constructs a new bot."""
        # Get the dino game ready
        setup_chrome_macro()
        time.sleep(0.8)

        self.frame_processor = FrameProcessor(edge_threshold=60)
        self.screen_recorder = ScreenRecorder(
            dino_template_path="assets/template_dino.png",
            replay_template_path="assets/template_replay.png",
        )

        self.scores = []

        # Constants to calculate ROI scaling (pixels)
        self.SCALE_RATE = 1.3 # Pixels per second
        self.MAX_DELTA_WIDTH = 140

    def play(self) -> None:
        """Play the chrome dino game."""
        # Start the game
        try:
            with mss.mss() as sct:
                while True:
                    keyboard.press_and_release("space")
                    self._play_round(sct=sct)
                    time.sleep(0.5)
        except KeyboardInterrupt:
            # End the game only with a keyboard interrupt
            self._print_end()

    def _play_round(self, sct) -> None:
        """Play a round of the dino game.

        Args:
            sct (MSSBase): MSS connection.
        """
        frame_count = 0
        start_time = time.time()
        width_delta = 0
        frames_since_last_jump = 0
        # Evaluate each frame
        while True:
            frame_count += 1
            elapsed_time = time.time() - start_time

            # Screen grab with scaled width delta
            img = self.screen_recorder.grab_frame_plus_width(
                sct=sct, d_width=width_delta
            )

            should_jump,obstacle_height= self.frame_processor.should_jump(img)
            if should_jump:
                
                # If the game is new then always moon jump
                if obstacle_height < 15 or elapsed_time < 48:
                    keyboard.press("space")
                    time.sleep(0.16)
                    keyboard.release("space")
                else:
                    keyboard.press_and_release("space")
                frames_since_last_jump = 0

            # Update ROI every 5 frames
            if frame_count % 5 == 0:
                width_delta = self._calculate_roi(elapsed_time=elapsed_time)

            # Check if game has finished every 15 frames.
            if frame_count % 15 == 0:
                if self.screen_recorder.is_run_over(sct=sct):
                    break

            # Catch all - reset if we haven't jumped in a long time
            if frames_since_last_jump >= 2500:
                break

            frames_since_last_jump += 1
        # Post-round cleanup
        self.scores.append(time.time() - start_time)
        print(f"Round: {len(self.scores)}: {self.scores[-1]:.0f} Vision: {width_delta}")
        
        # Force garbage collection to free memory from screen captures
        gc.collect()

    def _calculate_roi(self, elapsed_time: float = 0.0) -> int:
        """Calculate the additional range for the dino based on elapsed time this round.

        Args:
            elapsed_time (float, optional): Elapsed time since the start of the run. Defaults to 0.0.

        Returns:
            int: Number of pixels to add to the ROI width.
        """

        additonal_roi = int(elapsed_time * self.SCALE_RATE)
        new_roi = min(self.MAX_DELTA_WIDTH, additonal_roi)  # type: ignore
        return new_roi

    def _print_end(self) -> None:
        """Display statistics for this Bot's performance"""
        if not self.scores:
            return

        print("=" * 30)
        print(
            f"Bot played {len(self.scores)} time{"s" if len(self.scores) > 1 else ""}\n"
        )
        print(f"Best Score:   {max(self.scores):.2f}")
        print(f"Worst Score:  {min(self.scores):.2f}")
        print(f"Mean Score:   {statistics.mean(self.scores):.2f}")
        print(f"Median Score: {statistics.median(self.scores):.2f}")
        print("=" * 30)
