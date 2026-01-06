import cv2
import numpy as np
import mss
from typing import Tuple


class ScreenRecorder:
    def __init__(self, dino_template_path: str):
        """Construct a ScreenRecorder to capture the dino game in the chrome browser.

        Args:
            dino_template_path (str): Path to the template dino

        Raises:
            FileNotFoundError: Image can't be found.
        """
        # Load the template in grayscale
        self.template = cv2.imread(dino_template_path, 0)

        if self.template is None:
            raise FileNotFoundError(f"Could not find {dino_template_path}")

        # Get original dimensions
        self.t_h, self.t_w = self.template.shape[:2]

    def scan_for_image_on_steup(
        self, monitor_num: int = 0, threshold: float = 0.8
    ) -> bool:
        """Find the starting position of the dino on the correct monitor. Keep track of the dino's inital vision range.

        Args:
            monitor_num (int, optional): Which monitor to capture. Defaults to 0.
            threshold (float, optional): Similarity between template dino and image. Defaults to 0.8.

        Returns:
            bool: Whether the template was found.
        """

        with mss.mss() as sct:
            # Grab Screen
            mon = sct.monitors[monitor_num]
            sct_img = sct.grab(mon)

            # Convert to Grayscale
            img = np.array(sct_img)
            screen_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

            # Explore different scales, if using monitor with different resolution
            scales = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]

            best_score = 0
            best_scale = 1.0
            best_loc = 0

            for scale in scales:
                # Resize the template
                new_width = int(self.t_w * scale)
                new_height = int(self.t_h * scale)

                # If resized template is bigger than screen, skip it
                if new_width > mon["width"] or new_height > mon["height"]:
                    continue

                resized_template = cv2.resize(self.template, (new_width, new_height))

                # Match
                result = cv2.matchTemplate(
                    screen_gray, resized_template, cv2.TM_CCOEFF_NORMED
                )

                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                # Keep track of the best match found so far
                if max_val > best_score:
                    best_score = max_val
                    best_scale = scale
                    best_loc = max_loc

                # If we found a "perfect" match, stop looking
                if best_score > 0.9:
                    break

            if best_score >= threshold:

                self.monitor = monitor_num
                self.top = best_loc[1]  # pyright: ignore[reportIndexIssue]
                self.left = best_loc[2]  # pyright: ignore[reportIndexIssue]
                self.width = 110
                self.height = 68
                self.scale = best_scale

                return True
            else:

                return False
