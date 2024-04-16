import cv2
import numpy as np
import mss
import json
import os
import pyautogui
import time
import keyboard

# Global constants

# Canvas dimensions
global canvas_width; canvas_width = 800
global canvas_height; canvas_height = 600
global paddle_offset; paddle_offset = 73
global paddle_width; paddle_width = 8
global paddle_height; paddle_height = 60
global ball_radius; ball_radius = 10

# Collision bounds
# Right boundary of the canvas
right_bound = canvas_width-paddle_offset-paddle_width
# Upper boundary of the canvas
upper_bound = canvas_height - ball_radius
# Lower boundary of the canvas
lower_bound = 0+ball_radius

#Store past trajectories to calculate the average until the next bounce
trajectories = [] 

# Define some frequently used colors
global blue; blue = (255, 0, 0)
global green; green = (0, 255, 0)
global red; red = (0, 0, 255)
global aqua; aqua = (255, 255, 0)

# Settings
# Number of frames to skip before starting to track the ball again, 
# frame rate of the display/tracker will be 1/(frames_to_skip+1)
# I.e. 4 frames to skip will result in a frame rate of 1/5th of the actual frame rate
# Lower frames_to_skip is more performance heavy. Being less than 5 may cause some innaccuracy in tracking as tracking fractional pixels leads to inaccurate readings
# Higher frames_to_skip will result in a more accurate tracking but will be slower to react
frames_to_skip = 5
# Time in minutes before the program terminates itself to prevent accidental key presses while AFK
max_program_time_minutes = 5

# Time the program was ran
start_time = time.time()

permit_key_presses = False
time_pressed_last = time.time() - 2 #Time the 'p' key was last pressed, initially set to 2 seconds ago to allow key presses

def capture_game():
    global permit_key_presses #Allow key presses to be sent to the game
    global time_pressed_last #Time the 'p' key was last pressed

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

        img_previous = None #Previous frame is initially None
        frame_counter = 0 #Counter to keep track of frames
        
        # Main loop
        while True:
            # If 'p' is pressed, permit keybinds to be sent
            if keyboard.is_pressed('p'):
                # If the key was pressed last at least 2 seconds ago, toggle the key presses
                if time.time() - time_pressed_last > 2:
                    print('p was pressed')
                    # if the key was pressed for less than 1 second, toggle the key presses
                    permit_key_presses = not permit_key_presses
                    time_pressed_last = time.time()
                    if permit_key_presses:
                        print("Key presses enabled.")
                    else:
                        print("Key presses disabled.")
            
            # If 'q' is pressed even outside of the capture window, terminate the program
            if keyboard.is_pressed('q'):
                print("'q' was pressed, terminating program.")
                exit()
                

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
                # Track paddle's current location
                paddle_x, paddle_y, paddle_w, paddle_h = track_paddle(img) #track paddle's current location

                # Track ball movement
                predicted_x, predicted_y, frame_tracked = track_ball_movement(img, img_previous) #track ball movement from previous frame to current frame
                
                # Draw rectangle around the paddle
                padding = 2 #Extra padding around the paddle used to account for rounding errors
                if paddle_x is not None and paddle_y is not None:
                    cv2.rectangle(frame_tracked, (paddle_x - paddle_w//2 - padding,  #top left x
                                                  paddle_y - paddle_h//2 - padding), #top left y
                                                 (paddle_x + paddle_w//2 + padding,  #bottom right x
                                                  paddle_y + paddle_h//2 + padding), #bottom right y
                                                  aqua, 2)
                    
                # Move the paddle to the predicted point
                if permit_key_presses: 
                    if predicted_x is not None and paddle_x is not None:
                        # Calculate the vertical distance between the paddle and the predicted point
                        distance = round(predicted_y - paddle_y)
                        nearness_threshold = paddle_height//3 # Paddle will stop moving when this many pixels away from the predicted point

                        # If the distance is greater than 15 pixels, move the paddle to the predicted point
                        if distance>0 and distance > nearness_threshold:   # Need to move up
                            pyautogui.keyUp('i')            # Stop moving up
                            if not keyboard.is_pressed('k'):
                                pyautogui.keyDown('k')      # Start moving down
                                print(f"Now moving paddle DOWN {distance}")
                        elif distance<0 and distance < -nearness_threshold: # Need to move down
                            pyautogui.keyUp('k')            # Stop moving down
                            if not keyboard.is_pressed('i'):
                                pyautogui.keyDown('i')      # Start moving up
                                print(f"Now moving paddle UP {distance}")
                        else: # Reached destination
                            pyautogui.keyUp('k')    # Stop moving down
                            pyautogui.keyUp('i')    # Stop moving up
                            print("Paddle STOPPED")

                    else:
                        # If it was determined to not track the ball, immedietely stop sending key inputs
                        pyautogui.keyUp('k')    # Stop moving down
                        pyautogui.keyUp('i')    # Stop moving up


            else:
                frame_tracked = img_previous #Show previous frame

            # If the program has been running for more than max_program_time_minutes minutes, terminate the program to prevent accidental key presses while AFK
            if time.time() - start_time > 60*max_program_time_minutes: #5 minutes
                print(f"Program has been running for more than {max_program_time_minutes} minutes. Terminating program to prevent accidental key presses.")
                exit()

            cv2.imshow('Game Capture', frame_tracked)

            # Update the previous frame
            if not skip_this_frame:
                img_previous = img

            # Exit the loop if 'q' is pressed
            # Program should already terminate if q is pressed regardless of the active window, this is a safety check
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break

            # Increment the frame counter
            frame_counter += 1

        cv2.destroyAllWindows()

# Given a frame, detect and return circles using HoughCircles
def hough_circles(frame):
    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Gaussian blur 5x5
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect circles using HoughCircles
    circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=5, maxRadius=20)

    return circles

# Track the movement of the ball
# Parameters are current and previous frame
# Returns the current frame with the ball tracked and the coordinates of the final destination
def track_ball_movement(curr_frame, prev_frame):
    # Use HoughCircles to detect the ball in the current and previous frame
    prev_circle = hough_circles(prev_frame)
    curr_circle = hough_circles(curr_frame)

    # If trajectory should not be predicted, return None coordinates
    new_x = None
    new_y = None
    
    # If no circles are detected in either frame, return the current frame without a circle drawn
    if prev_circle is None or curr_circle is None:
        return new_x, new_y, curr_frame
    
    # Grab just the first circle found from each
    prev_circle = prev_circle[:1]
    curr_circle = curr_circle[:1]

    # Convert the circles to integer values
    curr_circle = np.uint16(np.around(curr_circle))

    # Draw the circle around the ball
    cv2.circle(curr_frame, (curr_circle[0][0][0], curr_circle[0][0][1]), 10 , green,2)

    # If ball is moving right, predict point to show where the ball will land
    if curr_circle[0][0][0] > prev_circle[0][0][0]:

        # Clear the trajectories if the ball is past the right paddle
        if prev_circle[0][0][0] > canvas_width-paddle_offset-paddle_width:
            trajectories.clear()
        else:
            # Calculate slope of the ball's trajectory
            slope = (curr_circle[0][0][1] - prev_circle[0][0][1]) / (curr_circle[0][0][0] - prev_circle[0][0][0])
            
            # Track the average trajectory of every curr_frame before the last bounce
            trajectory = (curr_circle[0][0][0], curr_circle[0][0][1], slope)

            # If the new trajectory has a slope of opposite direction to the previous trajectory, clear the trajectories
            if len(trajectories) > 0 and trajectories[-1][2] * slope < 0:
                trajectories.clear()
            trajectories.append(trajectory)

            # Calculate the average trajectory
            avg_slope = sum([t[2] for t in trajectories]) / len(trajectories)
            # Redefine trajectory with the average slope
            trajectory = (curr_circle[0][0][0], curr_circle[0][0][1], avg_slope)

            # Recursively call the function to predict the trajectory after it hits the right boundary
            new_x, new_y, slope = predict_trajectory(trajectory[0], trajectory[1], trajectory[2])

            # Draw the predicted point
            if new_x is not None:
                cv2.circle(curr_frame, (int(new_x), int(new_y)), 5, red, 2)

    return new_x, new_y, curr_frame

# Tracking the current location of the paddle, but not the movement
def track_paddle(curr_frame):
    # Crop the frame to the right half so that the left paddle isn't tracked on accident
    # Keep track of the width that was cropped to add it to the rectangle coordinates at the end
    width_lost = canvas_width // 2
    right_frame = curr_frame[:, width_lost:]

    # Convert the frame to grayscale
    gray = cv2.cvtColor(right_frame, cv2.COLOR_BGR2GRAY)

    # Gaussian blur 5x5
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Threshold the image
    _, thresh = cv2.threshold(blur, 240, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Filter out contours that are too small
    min_contour_area = 50
    max_contour_area = 250
    min_aspect_ratio = 1.5 #Ratio of height to width such that the ball isn't detected as a paddle
    # Can't be too harsh as the paddle can go half off-screen where the aspect ratio will be skewed

    paddle_contour = None
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_contour_area < area < max_contour_area:
            # Calculate aspect ratio of the contour
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(h) / w
            if aspect_ratio > min_aspect_ratio:
                paddle_contour = contour
                break

    # If no contours are found, return the current frame without a paddle tracked
    if len(contours) == 0:
        return None, None, None, None

    # Print the contour area for debugging
    #print(cv2.contourArea(contours[0]))

    # If paddle contour is found, track its position
    if paddle_contour is not None:
        # Get bounding rectangle of the paddle contour
        x, y, w, h = cv2.boundingRect(paddle_contour)
        x += width_lost # Need to add width back in since the frame was cropped

        # Calculate paddle center
        paddle_center_x = x + w // 2 
        paddle_center_y = y + h // 2

        # Return paddle dimensions
        return paddle_center_x, paddle_center_y, w, h

    return None, None, None, None


# Function to predict the linear trajectory of the ball
# If the ball's slope points it to the bottom or top of the screen, invert the slope and set new point to the border, call self recursively
# Until arriving at the right side of the screen, return the point
def predict_trajectory(x, y, slope):
    # If F(width) is within 0 and the canvas height, return the final boundary point
    new_x = right_bound
    new_y = slope * (new_x-x) + y
    if new_y > lower_bound and new_y < upper_bound:
        return new_x, new_y, slope

    # If F(width) is: 

    # Above the upper bound - Invert the slope, set new point to F_inverse(upper_bound) and call recursively
    elif new_y > upper_bound:
        new_y = upper_bound
        return predict_trajectory((new_y - y) / slope + x, new_y, -slope)  
    # Below below lower bound - Invert the slope, set new point to F_inverse(lower_bound) and call recursively
    elif new_y < lower_bound:
        new_y = lower_bound
        return predict_trajectory((new_y - y) / slope + x, new_y, -slope)  

    # ball is not moving right but was missed by initial check
    raise ValueError("predict_trajectory(): Ball is not moving right but was missed by the check in track_ball_movement()") 


if __name__ == "__main__":
    capture_game()
