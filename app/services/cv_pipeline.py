"""
Computer-vision pipeline: takes a raw batch image (onions laid out on a tray/
conveyor against a contrasting background) and returns per-onion measurements.

v1 approach (no ML model required): classical CV via OpenCV.
  1. Threshold + contour detection to segment individual onions.
  2. For each contour: measure size (calibrated to mm), shape (circularity),
     and color uniformity (HSV std-dev).

This is intentionally dependency-light so it runs out of the box. Swap in a
proper instance-segmentation model (YOLOv8-seg / Mask R-CNN) later by
replacing `segment_onions()` while keeping the same return shape.
"""

import cv2
import numpy as np

# Assumed calibration: pixels per millimetre. Replace with real calibration
# (e.g. a fixed-size marker in frame) before production use.
PIXELS_PER_MM = 8.0

MIN_CONTOUR_AREA = 1500  # filters out noise / tiny specks


def _load_image(image_path: str) -> np.ndarray:
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image at {image_path}")
    return image


def segment_onions(image_path: str) -> list[dict]:
    """
    Returns a list of dicts, one per detected onion:
    { bbox, size_mm, shape_score, color_uniformity, crop }
    """
    image = _load_image(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    # Otsu thresholding assumes a reasonably contrasting background
    # (e.g. dark tray/conveyor under onions).
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Clean up small noise / merge close blobs
    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    results = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_CONTOUR_AREA:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        diameter_px = (w + h) / 2
        size_mm = round(diameter_px / PIXELS_PER_MM, 1)

        # Shape score: circularity = 4*pi*area / perimeter^2 (1.0 = perfect circle)
        perimeter = cv2.arcLength(cnt, True)
        circularity = 0.0
        if perimeter > 0:
            circularity = float(4 * np.pi * area / (perimeter ** 2))
        shape_score = round(min(circularity, 1.0), 2)

        # Color uniformity: lower HSV std-dev within the onion region = more uniform skin
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        hsv_region = hsv[mask == 255]
        if len(hsv_region) > 0:
            std_dev = float(np.mean(np.std(hsv_region, axis=0)))
            # Normalize roughly into a 0-1 "uniformity" score (lower std = higher score)
            color_uniformity = round(max(0.0, 1.0 - min(std_dev / 60.0, 1.0)), 2)
        else:
            color_uniformity = None

        crop = image[y:y + h, x:x + w]

        results.append({
            "bbox": {"x": float(x), "y": float(y), "width": float(w), "height": float(h)},
            "size_mm": size_mm,
            "shape_score": shape_score,
            "color_uniformity": color_uniformity,
            "crop": crop,
        })

    return results
