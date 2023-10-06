import turtle

WIDTH = 800
HEIGHT = 600

wn = turtle.Screen()
wn.title("Sophias pong game")
wn.bgcolor("pink")
wn.setup(WIDTH, HEIGHT)
wn.tracer(0)

# Score
score_a = 0
score_b = 0

# Paddle A
paddle_a = turtle.Turtle()
paddle_a.speed(0)
paddle_a.shape("square")
paddle_a.color("blue")
paddle_a.shapesize(stretch_wid=5, stretch_len=1)
paddle_a.penup()
paddle_a.goto(-350, 0)

# Paddle B
paddle_b = turtle.Turtle()
paddle_b.speed(0)
paddle_b.shape("square")
paddle_b.color("red")
paddle_b.shapesize(stretch_wid=5, stretch_len=1)
paddle_b.penup()
paddle_b.goto(350, 0)

# Ball
ball = turtle.Turtle()
ball.speed(0)
ball.shape("square")
ball.color("orange")
ball.penup()
ball.goto(0, 0)
ball.dx = .5
ball.dy = .5

# Pen
pen = turtle.Turtle()
pen.speed()
pen.color("green")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Player A: 0  Player B: 0", align="center", font=("Courier", 16, "bold"))


# Functions for moving paddle
def paddle_a_up():
    y = paddle_a.ycor()
    y += 100
    paddle_a.sety(y)

def paddle_a_down():
    y = paddle_a.ycor()
    y -= 100
    paddle_a.sety(y)

def paddle_b_up():
    y = paddle_b.ycor()
    y += 100
    paddle_b.sety(y)

def paddle_b_down():
    y = paddle_b.ycor()
    y -= 100
    paddle_b.sety(y)


# Keyboard binding
wn.listen()
wn.onkeypress(paddle_a_up, "w")
wn.onkeypress(paddle_a_down, "s")
wn.onkeypress(paddle_b_up, "Up")
wn.onkeypress(paddle_b_down, "Down")

# Main game loop
running = True
while running:
    wn.update()

    # Move the Ball
    ball.setx(ball.xcor() + ball.dx)
    ball.sety(ball.ycor() + ball.dy)

    # Border checking
    if ball.ycor() > 285:
        ball.sety(285)
        ball.dy *= -1

    if ball.ycor() < -285:
        ball.sety(-285)
        ball.dy *= -1

    if ball.xcor() > 385:
        ball.goto(0, 0)
        ball.dx *= -1
        score_a += 1
        pen.clear()
        pen.write("Player A: {}  Player B: {}".format(score_a, score_b), align="center", font=("Courier", 14, "normal"))

    if ball.xcor() < -385:
        ball.goto(0, 0)
        ball.dx *= -1
        score_b += 1
        pen.clear()
        pen.write("Player A: {}  Player B: {}".format(score_a, score_b), align="center", font=("Courier", 14, "normal"))

    # Paddle and Ball Collisions
    if (ball.xcor() > 340 and ball.xcor() < 350) and (ball.ycor() < paddle_b.ycor() + 40 and ball.ycor() > paddle_b.ycor() - 40):
        ball.setx(340)
        ball.dx *= -1

    if (ball.xcor() < -340 and ball.xcor() > -350) and (ball.ycor() < paddle_a.ycor() + 40 and ball.ycor() > paddle_a.ycor() - 40):
        ball.setx(-340)
        ball.dx *= -1




