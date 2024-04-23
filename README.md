# OpenCV-Based Pong

Ball trajectory tracking and prediction

## Description
A computer vision software system capable of tracking a ball in a game of Pong and autonomously moving a paddle to interact with the ball. 
Computer vision techniques will be used to track the ball's movement on the screen and control one of the paddles to intercept the ball and beat the player.

## Preparation
* Open src\html\PongGame.html in your favorite browser and put it on the left half of your screen
* Run src\computervision\tracking.py, the displayed camera will be using template configuration and likely wont be capturing the precise corners.
* Create src\computervision\config\GameRegion.json using src\computervision\config\GameRegionTemplate.json as a template, shift the top left corner until the captured game region is 100% black and therefore is centered properly
* Rerun tracking.py then switch focus to the PongGame.html in your browser
* Press 'p' to allow the script to start moving the right paddle up and down with 'i' and 'k' keys
* Press 'w' or 's' to move the left paddle up or down to try to beat the AI!

## Objectives
* Interpret the screen from the game environment and send it to the algorithm
* Detect current location of the ball
* Predict the trajectory of the ball
* Calculate the input needed to move the AI’s paddle to the correct location
* Interpet the input needed and send it to the game environment
* Beat the player