"""
NFM-X OCR Preprocessing Module
===============================

Image preprocessing functions for OCR optimization.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple, Any
from enum import Enum


class PreprocessingType(Enum):
    NONE = "none"
    DENOISE = "denoise"
    DESKEW = "deskew"
    BINARIZE = "binarize"
    ENHANCE_CONTRAST = "enhance_contrast"
    SHARPEN = "sharpen"
    AUTO = "auto"


def convert_to_cv2(image: Any) -> np.ndarray:
    if isinstance(image, np.ndarray):
        if len(image.shape) == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
        return image
    elif isinstance(image, Image.Image):
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    elif isinstance(image, str):
        img = cv2.imread(image)
        if img is None:
            raise ValueError(f"Cannot read image from path: {image}")
        return img
    else:
        raise TypeError(f"Unsupported image type: {type(image)}")


def denoise_image(image: Any, method: str = 'median', kernel_size: int = 3) -> np.ndarray:
    img = convert_to_cv2(image)
    if method == 'median':
        return cv2.medianBlur(img, kernel_size)
    elif method == 'gaussian':
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
    elif method == 'bilateral':
        return cv2.bilateralFilter(img, kernel_size, 75, 75)
    return img


def preprocess_image(image: Any, denoise: bool = True, deskew: bool = True, binarize: bool = True) -> np.ndarray:
    img = convert_to_cv2(image)
    if denoise:
        img = denoise_image(img, method='median', kernel_size=3)
    if binarize:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary
    return img


# Urdu: NFM-X OCR پری پراسیسنگ ماڈول