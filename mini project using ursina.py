from ursina import *
import random

app = Ursina()

# Window settings
window.title = 'Ursina Breakout'
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# Game environment elements
# Walls and ceiling
floor = Entity(model='quad', x=0, y=-4, scale=(16, 0.2), collider='box', color=color.orange)
ceiling = Entity(model='quad', x=0, y=4, scale=(16, 0.2), collider='box', color=color.orange)
left_wall = Entity(model='quad', x=-7.2, y=0, scale=(0.2, 10), collider='box', color=color.orange)
right_wall = Entity(model='quad', x=7.2, y=0, scale=(0.2, 10), collider='box', color=color.orange)

# Ball entity
ball = Entity(model='circle', scale=0.2, collider='box', dx=0.05, dy=0.05, visible=False)

# Paddle entity
paddle = Entity(model='quad', x=0, y=-3.5, scale=(2, 0.2), collider='box', color=color.orange, visible=False)

# Game variables
score = 0
lives = 3  # Number of lives
bricks = []  # List to hold brick entities
powerups = []  # List to hold power-up entities
game_state = 'menu'  # Possible states: 'menu', 'playing', 'game_over'

# --- UI Elements ---
# Score display
score_text = Text(text=f'Score: {score}', position=window.top_left + Vec2(0.02, -0.02), origin=(0, 0), scale=2, color=color.white, shadow=True, enabled=False)

# Lives display
lives_text = Text(text=f'Lives: {lives}', position=window.top_right + Vec2(-0.1, -0.02), origin=(0, 0), scale=2, color=color.white, shadow=True, enabled=False)

# Instructions for the menu screen
instructions = Text(text='Use Left/Right Arrow Keys to move the paddle.\nBreak all bricks to win!\n\nPress any key to start', position=window.center - Vec2(0, 0.1), origin=(0, 0), scale=1.5, color=color.white, shadow=True, enabled=True)

# Game over/Win message text
game_over_text = Text(text='', origin=(0, 0), scale=3, color=color.orange, enabled=False)

# Function to create all the bricks for the game
def create_bricks():
    global bricks
    for brick in bricks:
        destroy(brick)
    bricks.clear()

    for x_pos in range(-65, 75, 10):
        for y_pos in range(3, 7):
            brick = Entity(model='quad', x=x_pos / 10, y=y_pos / 3, scale=(0.9, 0.3), collider='box', color=color.red)
            bricks.append(brick)

# Function to create a power-up
def create_powerup(x, y):
    powerup = Entity(model='quad', x=x, y=y, scale=(0.5, 0.2), collider='box', color=color.green)
    powerups.append(powerup)

# Function to set up and start a new game or restart an existing one
def start_game():
    global score, lives, game_state

    score = 0
    lives = 3
    score_text.text = f'Score: {score}'
    lives_text.text = f'Lives: {lives}'
    score_text.enabled = True
    lives_text.enabled = True

    create_bricks()

    ball.position = (0, 0)
    ball.dx = 0.05
    ball.dy = 0.05
    ball.visible = True

    paddle.position = (0, -3.5)
    paddle.visible = True

    instructions.enabled = False
    game_over_text.enabled = False

    game_state = 'playing'

# The 'update' function is called every frame by Ursina
def update():
    global game_state, score, lives

    if game_state == 'playing':
        ball.x += ball.dx
        ball.y += ball.dy

        paddle.x += (held_keys['right arrow'] - held_keys['left arrow']) * time.dt * 5
        paddle.x = max(-6.5, min(6.5, paddle.x))

        hit_info = ball.intersects()
        if hit_info.hit:
            if hit_info.entity == left_wall or hit_info.entity == right_wall:
                ball.dx = -ball.dx
            elif hit_info.entity == ceiling:
                ball.dy = -ball.dy
            elif hit_info.entity in bricks:
                destroy(hit_info.entity)
                bricks.remove(hit_info.entity)
                ball.dy = -ball.dy
                score += 1
                score_text.text = f'Score: {score}'

                # Randomly create a power-up when a brick is destroyed
                if random.random() < 0.2:  # 20% chance to drop a power-up
                    create_powerup(hit_info.entity.x, hit_info.entity.y + 0.5)

            elif hit_info.entity == paddle:
                ball.dy = -ball.dy
                ball.dx = 0.05 * (ball.x - paddle.x)

        # Check for power-up collisions
        for powerup in powerups:
            if ball.intersects(powerup).hit:
                destroy(powerup)
                powerups.remove(powerup)
                lives += 1
                lives_text.text = f'Lives: {lives}'

        # Game Over Conditions
        if ball.y < -5:
            lives -= 1
            lives_text.text = f'Lives: {lives}'
            if lives <= 0:
                game_state = 'game_over'
                game_over_text.text = f'You LOST! Final Score: {score}\nPress R to Restart or ESC to Exit.'
                game_over_text.position = (0, 0)
                game_over_text.enabled = True
                ball.visible = False
                paddle.visible = False
                score_text.enabled = False
                lives_text.enabled = False

        if len(bricks) == 0:
            game_state = 'game_over'
            game_over_text.text = f'You WON! Final Score: {score}\nPress R to Restart or ESC to Exit.'
            game_over_text.position = (0, 0)
            game_over_text.enabled = True
            ball.visible = False
            paddle.visible = False
            score_text.enabled = False
            lives_text.enabled = False

# Input handling function
def input(key):
    global game_state

    if key == 'escape':
        application.quit()

    if game_state == 'menu':
        start_game()
    elif game_state == 'game_over':
        if key == 'r':
            start_game()

# Start the Ursina application
app.run()
