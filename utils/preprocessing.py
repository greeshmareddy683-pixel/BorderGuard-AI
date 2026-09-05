import cv2
import numpy as np
from PIL import Image

def preprocess_image_for_ocr(image_input):
    """
    Applies CLAHE contrast enhancement, noise reduction, and binarization
    to improve OCR accuracy on passport/ID scans.
    """
    if isinstance(image_input, Image.Image):
        img_np = np.array(image_input.convert("RGB"))
    else:
        img_np = image_input.copy()

    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    
    # Adaptive Histogram Equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # Bilateral Filter for noise smoothing while preserving text edges
    smoothed = cv2.bilateralFilter(enhanced, 9, 75, 75)
    
    return Image.fromarray(smoothed)
