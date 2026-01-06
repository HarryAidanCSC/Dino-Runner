import numpy as np
import cv2


class FrameProcessor:
    """Represents a class which processes frames for the dino."""

    def __init__(self, edge_threshold: int = 50) -> None:
        """Constructs a new frame processor.

        Args:
            edge_threshold (int, optional): Number of edges required for the dino to jump. Defaults to 50.
        """
        self.edge_threshold = edge_threshold

    def should_jump(self, roi: np.ndarray) -> bool:
        """Determine whether the bot should jump based on a frame.

        Args:
            roi (np.ndarray): Range of interest in front of the dino.

        Returns:
            bool: Whether the bot should jump.
        """

        # Number of edges identified
        edges = cv2.Canny(roi, 100, 200)

        # Count number of edges
        if np.count_nonzero(edges) > self.edge_threshold:
            return True
        return False
