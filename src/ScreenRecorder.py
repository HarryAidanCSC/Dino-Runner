import cv2
from cv2.typing import Point
import numpy as np
import mss
import time
import keyboard
from typing import Tuple, Optional


class ScreenRecorder:
    """Represents class to setup the camera and record the Dino Run."""

    def __init__(
        self,
        dino_template_path: str,
        replay_template_path: str,
        default_monitor_num: int = 0,
        dino_threshold: float = 0.8,
    ) -> None:
        """Construct a ScreenRecorder to capture the dino game in the chrome browser. Ensures it is constructed with a template dino.
        Determine coordinates of the dino and positon camera.

        Args:
            dino_template_path (str): Path to the template dino.
            replay_template_path (str): Path to the template replay button.
            default_monitor_num (int, optional): Default monitor to use. Defaults to 0.
            dino_threshold (float, optional): Similarity between template dino and image. Defaults to 0.8.

        Raises:
            FileNotFoundError: Image can't be found.
            RuntimeError: Dino can't be found.
        """
        # Load the template in grayscale
        self.dino_template = self._load_template(img_path=dino_template_path)
        self.replay_template = self._load_template(img_path=replay_template_path)

        # Dimensions
        self.monitor = None
        self.top = None
        self.left = None
        self.width = None
        self.height = None
        self.scale = None
        self.monitor_num = default_monitor_num

        # Open connection to window manager
        with mss.mss() as sct:
            self._scan_for_image_on_steup(
                monitor_num=default_monitor_num, threshold=dino_threshold, sct=sct
            )

        # Protect against no dino
        if not self.monitor:
            raise RuntimeError(
                "Monitor has not been instantiated (most likely becuase the dino couldn't be found)."
            )

    def _load_template(self, img_path: str) -> np.ndarray:
        """Helper function to gather an image from a file path and convert to a matrix for CV compatability.

        Args:
            img_path (str): Path to the image file.

        Raises:
            FileNotFoundError: Image cannot be loaded correctly.

        Returns:
            np.ndarray: Matrix representation of the image.
        """
        img = cv2.imread(img_path, 0)
        if img is None:
            raise FileNotFoundError(f"Could not find {img_path}")

        return img

    def _scan_for_image_on_steup(self, monitor_num: int, threshold: float, sct) -> bool:
        """Find the starting position of the dino on the correct monitor. Keep track of the dino's inital vision range.

        Args:
            monitor_num (int, optional): Which monitor to capture. Defaults to 0.
            threshold (float, optional): Similarity between template dino and image. Defaults to 0.8.
            sct: (MSSInstance): Connection to make screen grabs.

        Returns:
            bool: Whether the template was found.
        """

        # Grab Screen
        mon = sct.monitors[monitor_num]
        sct_img = sct.grab(mon)

        # Convert to Grayscale
        img = np.array(sct_img)
        screen_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

        # Explore different scales, if using monitor with different resolution
        scales = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]

        best_score = 0
        best_scale = 1.0
        best_loc = 0

        for scale in scales:
            max_val, max_loc = self._match_to_template(
                screen_gray, self.dino_template, scale
            )

            # Keep track of the best match found so far
            if max_val > best_score:
                best_score = max_val
                best_scale = scale
                best_loc = max_loc

            # If we found a "perfect" match, stop looking
            if best_score > 0.9:
                break

        if best_score >= threshold:
            self.monitor_num = monitor_num
            self.top = best_loc[1]  # pyright: ignore[reportIndexIssue]
            self.left = best_loc[0] - 1815  # + 55 # pyright: ignore[reportIndexIssue]
            self.width = 110
            self.height = 56
            self.scale = best_scale

            # Define default base monitor to grab
            self.monitor = {
                "top": self.top,
                "left": self.left,
                "width": self.width,
                "height": self.height,
                "mon": self.monitor_num,
            }

            self.base_monitor = self.monitor.copy()
            return True
        else:
            print(f"No dino found, best match = {best_score:.2f}")
            return False

    def _match_to_template(
        self,
        primary_img: np.ndarray,
        comparison_img: np.ndarray,
        scale: float = 1.0,
    ) -> Tuple[float, Point]:
        """Match an image with another image. If it matches then return the threshold and location.

        Args:
            primary_img (np.ndarray): Image to locate the comparison upon.
            comparison_img (np.ndarray): Image to compare.
            scale (float, optional): Comparison image scaling factor. Defaults to 1.0.

        Returns:
            Tuple[float, Point]: Similarity score and positon of comparison image in the primary_img.
        """

        # Resize dimensions
        height, width = comparison_img.shape
        new_width = int(width * scale)
        new_height = int(height * scale)
        resized_comparison_img = cv2.resize(comparison_img, (new_width, new_height))

        # Match
        result = cv2.matchTemplate(
            primary_img, resized_comparison_img, cv2.TM_CCOEFF_NORMED
        )

        # Return closest match
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        return max_val, max_loc

    def take_video(self, fps=10) -> None:
        """Record a video of the dino's ROI.

        Args:
            fps (int, optional): Frames per second to record. Defaults to 10.

        Raises:
            ValueError: self.scan_for_image_on_setup() hasn't been called.
        """
        # Define compression and dimensions
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # type:ignore
        out = cv2.VideoWriter(
            "m.mp4", fourcc, 10, (self.width, self.height)  # type:ignore
        )

        print(f"Recording started - Press 'q' to stop.")
        try:
            with mss.mss() as sct:
                while True:
                    start_time = time.time()

                    # Convert screen grab to a grame
                    frame = self.grab_frame(sct, greyscale=False)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    out.write(frame)

                    # Stop logic
                    if keyboard.is_pressed("q"):
                        print("\n⏹️ Stopping recording...")
                        break

                    # Ensure 10 FPS
                    elapsed = time.time() - start_time
                    time.sleep(max(0, (1.0 / fps) - elapsed))

        except KeyboardInterrupt:
            pass

        finally:
            out.release()
            print(f"Video saved")

    def display_delta_screen_grab(
        self, d_width: int = 0, d_height: int = 0, d_top: int = 0, d_left: int = 0
    ) -> None:
        """Display screen grab to the user. Not to be used by the bot

        Args:
            d_width (int, optional): Width delta (px). Defaults to 0.
            d_height (int, optional): Height delta (px). Defaults to 0.
            d_top (int, optional): Top position delta (px). Defaults to 0.
            d_left (int, optional): Left position delta (px) . Defaults to 0.
        """
        if self.monitor is None:
            raise ValueError("Monitor not instantiated")

        with mss.mss() as sct:
            # Create new custom monitor configuration
            delta_monitor = {
                **self.monitor,
                "left": self.monitor["left"] + d_left,
                "top": self.monitor["top"] + d_top,
                "height": self.monitor["height"] + d_height,
                "width": self.monitor["width"] + d_width,
            }

            # Grab screenshot
            sct_img = sct.grab(delta_monitor)
            img_array = np.array(sct_img)
            cv2.imshow("Screenshot Preview (Press any key to close)", img_array)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def grab_frame(
        self, sct, greyscale: bool = True, monitor: Optional[dict] = None
    ) -> np.ndarray:
        """Grab a frame of the dino run and optionally add greyscaling.

        Args:
            sct (MSSBase): MSS class instance.
            greyscale (bool, optional): Whether to apply greyscaling. Defaults to True.
            monitor: (dict, optional): Custom monitor.

        Returns:
            np.ndarray: Array representation of the frame.
        """
        if not monitor:
            monitor = self.monitor
        img = np.array(sct.grab(monitor))

        if greyscale:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        return img

    def is_run_over(self, sct, similarity_threshold=0.8) -> bool:
        """Has the run ended? I.e. Has the replay button appeared.

        Args:
            sct (MSSBase): MSS class instance.
            similarity_threshold (float, optional): Required threshold to confirm run is over.

        Returns:
            bool. Has the run ended.
        """
        # Guard against no dino
        if not self.monitor:
            raise RuntimeError(
                "Monitor has not been instantiated (most likely becuase the dino couldn't be found)."
            )

        custom_monitor = {
            **self.monitor,
            "left": self.monitor["left"] + 200,
            "top": self.monitor["top"] - 25,
            "height": self.monitor["height"] + 10,
        }
        screen_grab = self.grab_frame(sct=sct, greyscale=True, monitor=custom_monitor)
        # (dleft=200, dwidth=0, dtop=-25, dheight=10)

        match_score, _ = self._match_to_template(
            primary_img=screen_grab, comparison_img=self.replay_template, scale=1.0
        )
        print(match_score)
        return match_score > similarity_threshold
