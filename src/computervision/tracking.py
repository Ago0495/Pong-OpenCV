import cv2
import numpy as np
import mss

def capture_game():
    with mss.mss() as sct:
        # Set the region to capture (coordinates and size of the game window)
        game_region = {'top': 190, 'left': 80, 'width': 800, 'height': 600}

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
