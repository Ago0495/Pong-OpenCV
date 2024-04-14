import cv2
import numpy as np
import mss
import json
import os
import math

#Global constants
global canvas_width
canvas_width = 800

global canvas_height
canvas_height = 600

global paddle_offset
paddle_offset = 73

global paddle_width
paddle_width = 8

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
        frames_to_skip = 10 #Number of frames to skip before starting to track the ball
        frame_counter = 0 #Counter to keep track of frames
        while True:
            # Capture the screen within the specified region
            screenshot = sct.grab(game_region)

            # Convert the screenshot to a numpy array
            img = np.array(screenshot)

            # If the previous frame is not yet assigned (first frame), set it to the current frame and skip the rest of the loop
            if img_previous is None:
                img_previous = img
                continue

            # Track ball movement only if the frame is not skipped
            skip_this_frame = frame_counter % (frames_to_skip + 1) != 0
            if not skip_this_frame:
                frame_tracked = track_ball_movement(img, img_previous)
            else:
                frame_tracked = img_previous

            # Draw a dot in each of the 4 corners for reference
            cv2.circle(frame_tracked, (0, 0), 5, color, -1)
            cv2.circle(frame_tracked, (0, game_region['height']), 5, color, -1)
            cv2.circle(frame_tracked, (game_region['width'], 0), 5, color, -1)
            cv2.circle(frame_tracked, (game_region['width'], game_region['height']), 5, color, -1)
                
            cv2.imshow('Game Capture', frame_tracked)

            # Update the previous frame
            if not skip_this_frame:
                img_previous = img

            # Exit the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Increment the frame counter
            frame_counter += 1

        cv2.destroyAllWindows()

# Function to track ball movement
def track_ball_movement(frame, prev_frame):
    # # Convert frames to grayscale for processing
    gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    prev_circle = cv2.HoughCircles(gray2, cv2.HOUGH_GRADIENT,1,20, param1=50,param2=30,minRadius=5,maxRadius=20)
    curr_circle = cv2.HoughCircles(gray1, cv2.HOUGH_GRADIENT,1,20, param1=50,param2=30,minRadius=5,maxRadius=20)
    
    if prev_circle is None or curr_circle is None:
        return frame
    
    # Grab just the first circle found from each
    prev_circle = prev_circle[:1]
    curr_circle = curr_circle[:1]

    curr_circle = np.uint16(np.around(curr_circle))

    # If ball is moving right, predict point to show where the ball will land
    if curr_circle[0][0][0] > prev_circle[0][0][0]:
        if verify_distance(prev_circle[0][0], curr_circle[0][0]) is not None:
            slope = (curr_circle[0][0][1] - prev_circle[0][0][1]) / (curr_circle[0][0][0] - prev_circle[0][0][0])
            new_x, new_y, slope = predict_trajectory(curr_circle[0][0][0], curr_circle[0][0][1], slope)
            if new_x is not None:
                cv2.circle(frame, (int(new_x), int(new_y)), 5, (0, 0, 255), 2)

    return frame

distances = [] #List to store distances between consecutive points, used to skip outliers
def verify_distance(point1, point2):
    x1, y1, _ = point1
    x2, y2, _ = point2

    # Skip if the ball is already past the paddle
    if x2>canvas_width-paddle_offset-paddle_width:
        return None

    # Calculate distance between point1 and point2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    # Skip outliers by keeping track of the last 5 distances
    if len(distances) > 5:
        distances.pop(0)

    # If the distance is an outlier, return None
    if len(distances) > 4 and distance > 1.5 * max(distances):
        return None
    
    distances.append(distance)

    return distance

# Function to predict the linear trajectory of the ball
# If the ball's slope points it to the bottom or top of the screen, invert the slope and set new point to the border, call self recursively
# Until arriving at the right side of the screen, return the point
right_bound = canvas_width-paddle_offset-paddle_width
def predict_trajectory(x, y, slope):
    # If F(width) is within 0 and the canvas height, return the final boundary point
    new_x = right_bound
    new_y = slope * (new_x-x) + y
    if new_y > 0 and new_y < canvas_height:
        return new_x, new_y, slope

    # If F(width) is above the canvas height or below 0,
    # invert the slope and set the new point to the boundary
    elif new_y > canvas_height:
        new_y = canvas_height
        return predict_trajectory((new_y - y) / slope + x, new_y, -slope)
    
    # If F(width) is below 0
    elif new_y < 0:
        new_y = 0
        return predict_trajectory((new_y - y) / slope + x, new_y, -slope)

    return None, None, None #ball is not moving right

if __name__ == "__main__":
    capture_game()
