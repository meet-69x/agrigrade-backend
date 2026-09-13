"""
Defect detection for a single cropped onion image.

v1: simple color/threshold heuristics (no training data required to start).
  - "rot"       -> significant very-dark/black patches on the surface
  - "sprouting" -> green patches concentrated near the top of the crop
  - "damage"    -> irregular bright patches suggesting exposed inner flesh

To upgrade: replace `detect_defects()` internals with a call to a trained
CNN/YOLO model. Keep the same return shape: (defect_tags: list[str], confidence: float)
so nothing else in the codebase needs to change.
"""

import cv2
import numpy as np


def detect_defects(crop: np.ndarray) -> tuple[list[str], float]:
    if crop is None or crop.size == 0:
        return [], 0.0

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    h, w = crop.shape[:2]
    total_pixels = h * w
    tags = []

    # --- Rot / dark decay patches ---
    dark_mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, 50))
    dark_ratio = float(np.sum(dark_mask > 0)) / total_pixels
    if dark_ratio > 0.06:
        tags.append("rot")

    # --- Sprouting (green shoots), concentrated in top third of the crop ---
    top_third = hsv[: h // 3, :, :]
    green_mask = cv2.inRange(top_third, (35, 40, 40), (85, 255, 255))
    green_ratio = float(np.sum(green_mask > 0)) / max(top_third.size / 3, 1)
    if green_ratio > 0.08:
        tags.append("sprouting")

    # --- Mechanical damage: very bright/whitish exposed-flesh patches ---
    bright_mask = cv2.inRange(hsv, (0, 0, 200), (180, 60, 255))
    bright_ratio = float(np.sum(bright_mask > 0)) / total_pixels
    if bright_ratio > 0.10:
        tags.append("damage")

    # Confidence: naive heuristic - fewer/clearer signals = higher confidence.
    # Replace with real model softmax confidence once a trained classifier is used.
    signal_strength = max(dark_ratio, green_ratio, bright_ratio)
    confidence = round(min(0.6 + signal_strength * 2, 0.98), 2) if tags else round(0.9, 2)

    return tags, confidence
