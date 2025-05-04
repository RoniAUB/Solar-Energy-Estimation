import cv2
import numpy as np
import os

def extract_yellow_lines(image):
    """Detect horizontal yellow lines and return their Y positions (sorted from top to bottom)."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    yellow_lower = np.array([20, 100, 100])
    yellow_upper = np.array([40, 255, 255])
    mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    
    # Morphology to enhance lines
    kernel = np.ones((1, 10), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # Find contours (lines)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    y_positions = [cv2.boundingRect(c)[1] for c in contours]
    y_positions = sorted(y_positions)
    
    return y_positions

def extract_green_bars(image, yellow_lines):
    """Detect green bars and map each height to kW based on yellow lines."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    green_lower = np.array([35, 100, 100])
    green_upper = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, green_lower, green_upper)
    
    # Morphology to reduce noise
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Find contours for each bar
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bar_info = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w > 5 and h > 10:  # Filter noise
            bar_info.append((x, y, h))

    # Sort by x-coordinate to get in order (left to right)
    bar_info = sorted(bar_info, key=lambda b: b[0])
    
    # Estimate kW per bar using yellow line spacing
    if len(yellow_lines) < 2:
        return []
    pixel_per_kw = abs(yellow_lines[1] - yellow_lines[0])
    bottom = yellow_lines[-1]
    
    kw_values = []
    for x, y, h in bar_info:
        top_of_bar = y
        pixel_height = bottom - top_of_bar
        kw = pixel_height / pixel_per_kw
        kw_values.append(round(kw, 2))
    
    return kw_values

def process_images_in_directory(directory):
    results = {}
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(directory, filename)
            image = cv2.imread(filepath)

            yellow_lines = extract_yellow_lines(image)
            production = extract_green_bars(image, yellow_lines)
            
            results[filename] = production
    
    return results

# Example usage
if __name__ == "__main__":
    directory = "path_to_your_image_directory"
    production_data = process_images_in_directory(directory)
    for filename, production in production_data.items():
        print(f"{filename}: {production}")
