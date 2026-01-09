import numpy as np
import cv2

class FrameProcessor:
    """Represents a class which processes frames for the dino."""

    def __init__(self, edge_threshold: int = 60) -> None:
        """Constructs a new frame processor.

        Args:
            edge_threshold (int, optional): Number of edges required for the dino to jump. Defaults to 50.
        """
        self.edge_threshold = edge_threshold

    def should_jump(self, roi: np.ndarray) -> tuple[bool, int]:
        """Determine whether the bot should jump based on a frame. Determine the height of the highest edge.

        Args:
            roi (np.ndarray): Range of interest in front of the dino.

        Returns:
            bool: Whether the bot should jump.
            int: The height of the highest edge.
        """

        # Number of edges identified 
        edges = cv2.Canny(roi, 90, 170)

        # Count number of edges
        edge_count = np.count_nonzero(edges)
        
        # Find the height of the highest edge (topmost row with edges)
        if edge_count > 0:
            rows_with_edges = np.where(edges.any(axis=1))[0]
            highest_edge_row = int(rows_with_edges[0]) if len(rows_with_edges) > 0 else roi.shape[0]
        else:
            highest_edge_row = roi.shape[0]  # Bottom of ROI if no edges
        
        should_jump = edge_count > self.edge_threshold
        return should_jump, highest_edge_row
