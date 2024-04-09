const leftPaddle = document.getElementById("leftPaddle");
const rightPaddle = document.getElementById("rightPaddle");
const ball = document.getElementById("ball");
const gameArea = document.querySelector(".game-area");

const paddleHeight = parseInt(window.getComputedStyle(leftPaddle).height); /* Height of the paddles */
const paddleWidth = parseInt(window.getComputedStyle(leftPaddle).width); /* Width of the paddles */
/* Can assume the Left and right paddle will share the same height and width */
const borderWidth = paddleWidth+parseInt(window.getComputedStyle(leftPaddle).left)

let ballSpeed = 10; /* Speed of the ball  */
let centerX = gameArea.clientWidth / 2; /* Center of the game area */
let centerY = gameArea.clientHeight / 2; /* Center of the game area */
let ballX = centerX;
let ballY = centerY;
let leftPaddleY = gameArea.clientHeight / 2;
let rightPaddleY = gameArea.clientHeight / 2;

let ballVelocity = get_vector_components(ballSpeed, get_random_radians()); /* Initial speed of the ball in X and Y directions */
let ballVelocityX = ballVelocity[0];
let ballVelocityY = ballVelocity[1]; 

let Keys = [];

const paddleSpeed = 10; /* Speed of the paddles */

/* Pick a random direction for rotation within set bounds, return radians */
function get_random_radians() {
    let random_degrees = Math.random() * 30 - 60; /* See https://www.desmos.com/calculator/k3qp8ogywl for derivation, chooses between the middle third of the 1st and 4th quadrant */
    let up_or_down = Math.random() < 0.5 ? -1 : 1; /* Randomly choose up or down [-1, 1]*/
    return up_or_down * random_degrees * (Math.PI / 180); /* Convert degrees to radians */
}

/* Given magnitude and direction in radians, return X and Y components */
function get_vector_components(magnitude, direction) {
    let x = magnitude * Math.cos(direction); /* Convert magnitude to horizontal component */
    let y = magnitude * Math.sin(direction); /* Convert magnitude to vertical component */
    return [x, y];
}

/* Update the game stat */
function update() {
    // Update ball position
    ballX += ballVelocityX;
    ballY += ballVelocityY;

    // Ball collision with top and bottom of game area
    if (ballY >= gameArea.clientHeight || ballY <= 0) {
        ballVelocityY = -ballVelocityY; // invert vertical velocity
    }

    // Ball collision with paddles
    if (
        (ballX <= borderWidth && ballY >= leftPaddleY && ballY <= leftPaddleY + paddleHeight) || // left borderWidth pixels, within left paddle's height
        (ballX >= gameArea.clientWidth - borderWidth && ballY >= rightPaddleY && ballY <= rightPaddleY + paddleHeight) // right borderWidth pixels, within right paddle's height
    ) {
        ballVelocityX = -ballVelocityX; // invert horizontal velocity
    }

    // Ball out of bounds (left or right side of game area)
    if (ballX < 0 || ballX > gameArea.clientWidth) {
        ballX = centerX; // reset ball position
        ballY = centerY;
        ballVelocity = get_vector_components(ballSpeed, get_random_radians()); // reset ball speed to new direction
        ballVelocityX = ballVelocity[0]; 
        ballVelocityY = ballVelocity[1];
    }

    // Move right paddle (AI)
    if (ballY > rightPaddleY + borderWidth) {
        rightPaddleY += paddleSpeed;
    } else if (ballY < rightPaddleY + borderWidth) {
        rightPaddleY -= paddleSpeed;
    }

    // Update elements position
    ball.style.left = ballX + "px";
    ball.style.top = ballY + "px";
    leftPaddle.style.top = leftPaddleY + "px";
    rightPaddle.style.top = rightPaddleY + "px";

    if ("W" in Keys && Keys["W"])
    {
        leftPaddleY -= paddleSpeed;
    }
    if ("S" in Keys && Keys["S"])
    {
        leftPaddleY += paddleSpeed;
    }
}

/* Handle keydown event */
function keyDown(e) {
    // if (e.key === "w" && leftPaddleY > 0) { /* Only allow movement up if the paddle is not at the top of the game area */
    //     leftPaddleY -= paddleSpeed; /* Move the paddle up*/
    // } else if (e.key === "s" && leftPaddleY < gameArea.clientHeight - paddleHeight) { /* Only allow movement down if the paddle is not at the bottom of the game area */
    //     leftPaddleY += paddleSpeed; /* Move the paddle down */
    // }

    Keys[String.fromCharCode(e.keyCode)] = true;
    // console.log(String.fromCharCode(e.keyCode) +" should be true - "+
    // Keys[String.fromCharCode(e.keyCode)]);
}

function keyUp(e) {
    Keys[String.fromCharCode(e.keyCode)] = false;
    // console.log(String.fromCharCode(e.keyCode) +" should be false - "+
    // Keys[String.fromCharCode(e.keyCode)]);
}

/* Listen for keydown event */
document.addEventListener("keydown", keyDown);
document.addEventListener("keyup", keyUp);

/* Game loop to constant update the game */
function gameLoop() {
    update();
    requestAnimationFrame(gameLoop);
}

gameLoop();
