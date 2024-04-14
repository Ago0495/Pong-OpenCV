import cv2
import numpy as np
import mss
import json
import os
import math

def capture_game():
    with mss.mss() as sct:
        # Set the region to capture (coordinates and size of the game window)
        # If GameRegion.json doesn't exist, use the template and refer the user to it
        # Get current working directory
        cwd = os.getcwd()
        cwd = os.path.join(cwd, 'src/computervision/config')
        config_file = os.path.join(cwd,'GameRegion.json')
        if not os.path.exists(config_file):
            print('Please create a GameRegion.json file in the config folder.')
            print('You can use the config/GameRegionTemplate.json file as a reference.')
            print('The template file will be used in the mean time, the canvas size may not be correct.')
            config_file = os.path.join(cwd,'GameRegionTemplate.json')
        with open(config_file) as f:
            game_region_data = json.load(f)
        
        game_region = {'top': game_region_data['top'], 'left': game_region_data['left'], 'width': 800, 'height': 600}
        color = (255, 0, 0) #red color for the drawn lines

        img_previous = None #Previous frame is initially None
        while True:
            # Capture the screen within the specified region
            screenshot = sct.grab(game_region)
            # Convert the screenshot to a numpy array
            img = np.array(screenshot)
            # Convert the image from BGR to RGB (OpenCV uses BGR, but most other libraries use RGB)
            #img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # If the previous frame is not yet assigned (first frame), set it to the current frame and skip the rest of the loop
            if img_previous is None:
                img_previous = img
                continue

            # Track ball movement
            frame_tracked = track_ball_movement(img, img_previous)

            # Update the previous frame
            img_previous = img
            cv2.imshow('img', img)
            cv2.imshow('img_previous', img_previous)
            
            # Perform computer vision tasks here (e.g., object detection, image processing, etc.)
            # For example, you can display the captured frame:
            cv2.imshow('Game Capture', frame_tracked)

            # Exit the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

# Function to track ball movement
def track_ball_movement(frame, prev_frame):
    # Convert frames to grayscale for processing
    gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    # Calculate the absolute difference between the two frames
    diff = cv2.absdiff(gray1, gray2)

    # Apply a threshold to get a binary image
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Find contours in the binary image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize variables for storing ball positions
    prev_center = None
    curr_center = None

    for contour in contours:
        # Approximate the contour to a circle
        (x, y), radius = cv2.minEnclosingCircle(contour)
        center = (int(x), int(y))

        # Filter out small contours (noise)
        if radius > 10:
            # Draw circle on the frame for visualization
            cv2.circle(prev_frame, center, int(radius), (0, 255, 0), 2)

            # Store the current center
            prev_center = curr_center
            curr_center = center

    # Draw a line connecting the previous and current positions
    if prev_center is not None and curr_center is not None:
        predicted_point = predict_point(prev_center, curr_center)
        if predicted_point is not None:
            cv2.line(prev_frame, curr_center, predicted_point, (0, 0, 255), 2)

    return prev_frame

# Function to predict the next point based on the previous two points, used to draw a connecting line that represents trajectory
def predict_point(point1, point2, scale=30):
    x1, y1 = point1
    x2, y2 = point2

    # Calculate distance between point1 and point2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    # Calculate unit vector components
    if distance != 0:  # Avoid division by zero
        ux = (x2 - x1) / distance
        uy = (y2 - y1) / distance
    else:
        # If distance is zero, return the same point
        return None

    # Calculate new point coordinates
    x_shift = scale * distance * ux
    y_shift = scale * distance * uy
    new_x = x1 + x_shift
    new_y = y1 + y_shift

    return (int(new_x), int(new_y))


if __name__ == "__main__":
    capture_game()
