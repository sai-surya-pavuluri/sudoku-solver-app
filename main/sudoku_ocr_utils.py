import cv2
import numpy as np
import pytesseract

def extract_sudoku_puzzle(img):
    """
    Extract digits from a Sudoku puzzle image and return a dict: {"row,col": digit}.
    """
    # 1. Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Apply adaptive threshold to binarize the image
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # 3. Find the largest square contour
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    biggest = None
    for c in contours:
        area = cv2.contourArea(c)
        if area > max_area:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if len(approx) == 4:
                biggest = approx
                max_area = area

    if biggest is None:
        return {}

    # 4. Reorder and warp perspective
    def reorder(pts):
        pts = pts.reshape((4, 2))
        new_pts = np.zeros((4, 2), dtype=np.float32)
        add = pts.sum(1)
        diff = np.diff(pts, axis=1)
        new_pts[0] = pts[np.argmin(add)]
        new_pts[2] = pts[np.argmax(add)]
        new_pts[1] = pts[np.argmin(diff)]
        new_pts[3] = pts[np.argmax(diff)]
        return new_pts

    biggest = reorder(biggest)
    pts1 = np.float32(biggest)
    pts2 = np.float32([[0, 0], [450, 0], [450, 450], [0, 450]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    warp = cv2.warpPerspective(gray, matrix, (450, 450))

    # 5. Preprocess warped grid
    _, warp_bin = cv2.threshold(warp, 128, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((2, 2), np.uint8)
    warp_bin = cv2.dilate(warp_bin, kernel, iterations=1)

    # 6. Slice into 81 cells and OCR
    cell_w = warp.shape[1] // 9
    cell_h = warp.shape[0] // 9
    result = {}
    config = '--psm 10 --oem 3 -c tessedit_char_whitelist=123456789'

    for r in range(9):
        for c in range(9):
            cell = warp_bin[r*cell_h:(r+1)*cell_h, c*cell_w:(c+1)*cell_w]

            # Crop central part of the cell to remove borders
            margin = 4
            cell = cell[margin:-margin, margin:-margin]

            # Resize for OCR
            cell = cv2.resize(cell, (32, 32), interpolation=cv2.INTER_AREA)

            digit = pytesseract.image_to_string(cell, config=config)
            digit = ''.join(filter(str.isdigit, digit))

            if digit:
                result[f"{r},{c}"] = int(digit)

    return result
