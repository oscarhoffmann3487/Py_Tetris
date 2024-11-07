import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
s_width = 800
s_height = 700
play_width = 300  # 10 blocks wide
play_height = 600  # 20 blocks high
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

# Shape formats
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

# List of shapes and their colors
shapes = [S, Z, I, O, J, L, T]
shape_colors = [
    (0, 255, 0),    # Green
    (255, 0, 0),    # Red
    (0, 255, 255),  # Cyan
    (255, 255, 0),  # Yellow
    (255, 165, 0),  # Orange
    (0, 0, 255),    # Blue
    (128, 0, 128)   # Purple
]

class Piece:
    def __init__(self, x, y, shape):
        """Initialize the piece."""
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # Number from 0-3

def create_grid(locked_positions={}):
    """Create a grid with locked positions."""
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                grid[i][j] = locked_positions[(j, i)]
    return grid

def convert_shape_format(piece):
    """Convert the shape format to grid positions."""
    positions = []
    format_shape = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format_shape):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))

    return positions

def valid_space(piece, grid):
    """Check if the position is valid (no collision)."""
    accepted_positions = [
        [(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)]
        for i in range(20)
    ]
    accepted_positions = [pos for sublist in accepted_positions for pos in sublist]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions and pos[1] > -1:
            return False
    return True

def check_lost(positions):
    """Check if any locked positions are above the top of the grid."""
    for pos in positions:
        _, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    """Return a random new piece."""
    return Piece(5, 0, random.choice(shapes))

def draw_text_middle(text, size, color, surface):
    """Draw text in the middle of the screen."""
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)

    surface.blit(
        label,
        (
            top_left_x + play_width / 2 - label.get_width() / 2,
            top_left_y + play_height / 2 - label.get_height() / 2,
        ),
    )

def draw_grid(surface, grid):
    """Draw grid lines."""
    for i in range(len(grid)):
        pygame.draw.line(
            surface,
            (128, 128, 128),
            (top_left_x, top_left_y + i * block_size),
            (top_left_x + play_width, top_left_y + i * block_size),
        )  # Horizontal lines
        for j in range(len(grid[i])):
            pygame.draw.line(
                surface,
                (128, 128, 128),
                (top_left_x + j * block_size, top_left_y),
                (top_left_x + j * block_size, top_left_y + play_height),
            )  # Vertical lines

def clear_rows(grid, locked):
    """Clear completed rows and shift the above rows down."""
    inc = 0
    ind = []
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind.append(i)
            # Remove the locked positions from the cleared row
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except KeyError:
                    continue

    if inc > 0:
        # Shift every row above down
        for key in sorted(list(locked.keys()), key=lambda x: x[1])[::-1]:
            x, y = key
            num = 0
            for i in ind:
                if y < i:
                    num += 1
            if num > 0:
                new_key = (x, y + num)
                locked[new_key] = locked.pop(key)
    return inc

def draw_next_shape(piece, surface):
    """Display the next shape to the player."""
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', True, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format_shape = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format_shape):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(
                    surface,
                    piece.color,
                    (
                        sx + j * block_size,
                        sy + i * block_size,
                        block_size,
                        block_size,
                    ),
                    0,
                )

    surface.blit(label, (sx + 10, sy - 30))

def update_score(new_score):
    """Update the high score if the new score is higher."""
    score = max_score()

    with open('highscore.txt', 'w') as f:
        if int(score) > new_score:
            f.write(str(score))
        else:
            f.write(str(new_score))

def max_score():
    """Retrieve the current high score from the file."""
    try:
        with open('highscore.txt', 'r') as f:
            lines = f.readlines()
            score = lines[0].strip()
    except:
        score = '0'

    return score

def draw_window(surface, grid, score=0, last_score=0, lines_cleared=0, level=1):
    """Draw the main game window."""
    surface.fill((0, 0, 0))
    # Title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('TETRIS', True, (255, 255, 255))

    surface.blit(
        label, (top_left_x + play_width / 2 - label.get_width() / 2, 30)
    )

    # Current score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), True, (255, 255, 255))

    sx = top_left_x - 270
    sy = top_left_y + 200

    surface.blit(label, (sx + 20, sy + 160))

    # High score
    label = font.render('High Score: ' + last_score, True, (255, 255, 255))
    surface.blit(label, (sx + 20, sy + 200))

    # Lines cleared
    label = font.render('Lines: ' + str(lines_cleared), True, (255, 255, 255))
    surface.blit(label, (sx + 20, sy + 240))

    # Level
    label = font.render('Level: ' + str(level), True, (255, 255, 255))
    surface.blit(label, (sx + 20, sy + 280))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(
                surface,
                grid[i][j],
                (
                    top_left_x + j * block_size,
                    top_left_y + i * block_size,
                    block_size,
                    block_size,
                ),
                0,
            )

    # Draw grid and border
    draw_grid(surface, grid)
    pygame.draw.rect(
        surface,
        (255, 0, 0),
        (top_left_x, top_left_y, play_width, play_height),
        5,
    )

def pause_game(surface):
    """Pause the game."""
    paused = True
    draw_text_middle('Paused', 60, (255, 255, 255), surface)
    pygame.display.update()
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False

def main():
    """Main game loop."""
    global win
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')

    last_score = max_score()
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    paused = False
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    level_time = 0
    score = 0
    lines_cleared = 0
    level = 1

    while run:
        grid = create_grid(locked_positions)
        if not paused:
            fall_time += clock.get_rawtime()
            level_time += clock.get_rawtime()
        clock.tick()

        # Increase speed over time
        if level_time / 1000 > 20:
            level_time = 0
            if fall_speed > 0.15:
                fall_speed -= 0.005
                level += 1

        # Piece falling logic
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        pause_game(win)
                if not paused:
                    # Move left
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1
                    # Move right
                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1
                    # Rotate
                    elif event.key == pygame.K_UP:
                        current_piece.rotation += 1
                        if not valid_space(current_piece, grid):
                            current_piece.rotation -= 1
                    # Move down
                    elif event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid):
                            current_piece.y -= 1
                    # Drop piece
                    elif event.key == pygame.K_SPACE:
                        while valid_space(current_piece, grid):
                            current_piece.y += 1
                        current_piece.y -= 1
                        change_piece = True

        shape_pos = convert_shape_format(current_piece)

        # Add piece to the grid
        for pos in shape_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color

        # Piece hit the ground
        if change_piece:
            for pos in shape_pos:
                locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # Clear rows
            cleared_rows = clear_rows(grid, locked_positions)
            if cleared_rows > 0:
                lines_cleared += cleared_rows
                score += cleared_rows * 100

        draw_window(win, grid, score, last_score, lines_cleared, level)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # Check for game over
        if check_lost(locked_positions):
            draw_text_middle('GAME OVER', 80, (255, 255, 255), win)
            pygame.display.update()
            pygame.time.delay(2000)
            run = False
            update_score(score)

def main_menu():
    """Display the main menu."""
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle('Press Any Key To Play', 60, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()

if __name__ == '__main__':
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')
    main_menu()
