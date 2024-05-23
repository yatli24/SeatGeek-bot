import cv2
import numpy as np
from collections import Counter
from matplotlib import colors

def get_predominant_color(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixels = image.reshape(-1, 3)
    pixels = [tuple(pixel) for pixel in pixels]
    pixel_counts = Counter(pixels)
    predominant_color = pixel_counts.most_common(1)[0][0]
    return predominant_color

def generate_comment(color):
    hex_color = colors.to_hex([c/255.0 for c in color])
    color_comments = {
        "#ff0000": "The image is dominated by a vibrant red hue.",
        "#00ff00": "The image is full of refreshing green.",
        "#0000ff": "The image has a calming blue tone.",
        "#ffffff": "The image is mostly white and bright.",
        "#000000": "The image is quite dark with predominant black.",
        "#ffff00": "The image is glowing with yellow.",
        "#ff00ff": "The image is filled with a playful magenta.",
        "#00ffff": "The image has a cool cyan color."
    }
    return color_comments.get(hex_color, f"The predominant color in the image is {hex_color}.")

def main(image_path):
    predominant_color = get_predominant_color(image_path)
    comment = generate_comment(predominant_color)
    print(comment)

image_path = 'path.jpg'
main(image_path)
