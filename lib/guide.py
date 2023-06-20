import os
import cv2
from PIL import Image
from imagehash import average_hash

def identify_image(image_path, image_folder):
    image = cv2.imread(image_path)
    image_hash = average_hash(Image.fromarray(image))
    min_diff = float("inf")
    closest_image = None
    for filename in os.listdir(image_folder):
        if filename.endswith(".png") or filename.endswith(".jpg"):
            candidate_image = cv2.imread(os.path.join(image_folder, filename))
            candidate_hash = average_hash(Image.fromarray(candidate_image))
            diff = candidate_hash - image_hash
            if diff < min_diff:
                min_diff = diff
                closest_image = filename
    return closest_image.split(".")[0]  # Return name without extension
