import cv2
import numpy as np
from collections import Counter
from matplotlib import colors

# Load YOLO deep learning model
def load_yolo():
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return net, classes, output_layers

# Define Object Detection
def detect_objects(img, net, output_layers):
    height, width, channels = img.shape
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    class_ids = []
    confidences = []
    boxes = []
    # Detection Algorithm
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    return class_ids, confidences, boxes

# Get Predominant Color of Image
def get_predominant_color(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pixels = image.reshape(-1, 3)
    pixels = [tuple(pixel) for pixel in pixels]
    pixel_counts = Counter(pixels)
    predominant_color = pixel_counts.most_common(1)[0][0]
    return predominant_color

def generate_color_comment(color):
    hex_color = colors.to_hex([c/255.0 for c in color])
    color_comments = {
        "#ff0000": "A vibrant, glorious red hue.",
        "#00ff00": "A crisp refreshing green.",
        "#0000ff": "Ahh... blue like the ocean.",
        "#ffffff": "A flash of mostly bright white.",
        "#000000": "A dark and mysterious sight.",
        "#ffff00": "Make sure to bring sunglasses to view the sunny yellow glow!",
        "#ff00ff": "A playful, curious magenta.",
        "#00ffff": "The cool cyan color reminds me of the sky."
    }
    return color_comments.get(hex_color, f"The predominant color in the image is {hex_color}.")


def generate_object_comment(class_ids, classes):
    object_comments = {
        "person": "I see a person. Who is that?",
        "car": "Cool car!",
        "bicycle": "How many miles are on that bike?",
        "dog": "That is a lovely dog!",
        "cat": "What a nice cat!",
        "horse": "Neigh! Ginny!",
    }
    comments = set()
    for class_id in class_ids:
        class_name = classes[class_id]
        if class_name in object_comments:
            comments.add(object_comments[class_name])
    if comments:
        return " ".join(comments)
    else:
        return "The image does not contain any recognizable objects or figures."

def main(image_path):
    image = cv2.imread(image_path)
    net, classes, output_layers = load_yolo()
    class_ids, confidences, boxes = detect_objects(image, net, output_layers)
    predominant_color = get_predominant_color(image_path)
    color_comment = generate_color_comment(predominant_color)
    object_comment = generate_object_comment(class_ids, classes)
    print(color_comment)
    print(object_comment)
    
image_path = 'image_path.jpg'
main(image_path)
