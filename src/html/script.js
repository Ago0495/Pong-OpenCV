const leftPaddle = document.getElementById("leftPaddle");
const rightPaddle = document.getElementById("rightPaddle");
const ball = document.getElementById("ball");
const gameArea = document.querySelector(".game-area");

let ballX = 50;
let ballY = 50;
let ballSpeedX = 2;
let ballSpeedY = 2;
let leftPaddleY = 50;
let rightPaddleY = 50;
const paddleSpeed = 5;

function update() {
    // Update ball position
    ballX += ballSpeedX;
    ballY += ballSpeedY;

    // Ball collision with top and bottom of game area
    if (ballY >= gameArea.clientHeight || ballY <= 0) {
        ballSpeedY = -ballSpeedY;
    }

    // Ball collision with paddles
    if (
        (ballX <= 30 && ballY >= leftPaddleY && ballY <= leftPaddleY + 60) ||
        (ballX >= gameArea.clientWidth - 45 && ballY >= rightPaddleY && ballY <= rightPaddleY + 60)
    ) {
        ballSpeedX = -ballSpeedX;
    }

    // Ball out of bounds
    if (ballX < 0 || ballX > gameArea.clientWidth) {
        ballX = 50;
        ballY = 50;
        ballSpeedX = -ballSpeedX;
    }

    // Move right paddle (AI)
    if (ballY > rightPaddleY + 30) {
        rightPaddleY += paddleSpeed;
    } else if (ballY < rightPaddleY + 30) {
        rightPaddleY -= paddleSpeed;
    }

    // Update elements position
    ball.style.left = ballX + "px";
    ball.style.top = ballY + "px";
    leftPaddle.style.top = leftPaddleY + "px";
    rightPaddle.style.top = rightPaddleY + "px";
}

function keyDown(e) {
    if (e.key === "w" && leftPaddleY > 0) {
        leftPaddleY -= paddleSpeed;
    } else if (e.key === "s" && leftPaddleY < gameArea.clientHeight - 60) {
        leftPaddleY += paddleSpeed;
    }
}

document.addEventListener("keydown", keyDown);

function gameLoop() {
    update();
    requestAnimationFrame(gameLoop);
}

gameLoop();
