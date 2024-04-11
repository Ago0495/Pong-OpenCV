import cv2
import numpy as np
import mss
import json
import os

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

        while True:
            # Capture the screen within the specified region
            screenshot = sct.grab(game_region)
            # Convert the screenshot to a numpy array
            img = np.array(screenshot)
            # Convert the image from BGR to RGB (OpenCV uses BGR, but most other libraries use RGB)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Perform computer vision tasks here (e.g., object detection, image processing, etc.)
            # For example, you can display the captured frame:
            cv2.imshow('Game Capture', img_rgb)

            # Exit the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_game()
