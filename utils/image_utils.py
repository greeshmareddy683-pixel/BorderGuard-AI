import cv2
import numpy as np
from PIL import Image
import io

def pil_to_cv(pil_img):
    """Converts PIL Image to OpenCV BGR numpy array."""
    return cv2.cvtColor(np.array(pil_img.convert("RGB")), cv2.COLOR_RGB2BGR)

def cv_to_pil(cv_img):
    """Converts OpenCV BGR numpy array to PIL Image."""
    return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))

def get_image_bytes(pil_img, format="JPEG"):
    """Returns byte buffer of a PIL Image."""
    buf = io.BytesIO()
    pil_img.save(buf, format=format)
    return buf.getvalue()
