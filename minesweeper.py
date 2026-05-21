import pygame
import random
import sys
import time

import minesweeper_db

# -----------------------------
# PYGAME SETUP
# -----------------------------
pygame.init()

WIDTH, HEIGHT = 600, 600
ROWS, COLS = 15, 15
TILE_SIZE = WIDTH // COLS
MINES_COUNT = 30

# Colors
GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

font = pygame.font.SysFont(None, 30)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

# -----------------------------
# GAME VARIABLES
# -----------------------------
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
revealed = [[False for _ in range(COLS)] for _ in range(ROWS)]
flagged = [[False for _ in range(COLS)] for _ in range(ROWS)]

start_time = time.time()

game_over = False
game_won = False


# -----------------------------
# PLACE MINES
# -----------------------------
def place_mines(grid):

    mines = 0

    while mines < MINES_COUNT:

        x = random.randint(0, COLS - 1)
        y = random.randint(0, ROWS - 1)

        if grid[y][x] != "M":
            grid[y][x] = "M"
            mines += 1


# -----------------------------
# COUNT ADJACENT MINES
# -----------------------------
def count_adjacent_mines(grid, x, y):

    count = 0

    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:

            nx = x + dx
            ny = y + dy

            if 0 <= nx < COLS and 0 <= ny < ROWS:

                if grid[ny][nx] == "M":
                    count += 1

    return count


# -----------------------------
# SETUP GRID
# -----------------------------
def setup_grid(grid):

    for y in range(ROWS):
        for x in range(COLS):

            if grid[y][x] != "M":
                grid[y][x] = count_adjacent_mines(grid, x, y)


# -----------------------------
# DRAW GRID
# -----------------------------
def draw_grid():

    for y in range(ROWS):
        for x in range(COLS):

            rect = pygame.Rect(
                x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE
            )

            if revealed[y][x]:

                pygame.draw.rect(screen, WHITE, rect)

                if grid[y][x] == "M":
                    pygame.draw.circle(
                        screen, BLACK, rect.center, TILE_SIZE // 4
                    )

                elif grid[y][x] > 0:

                    text = font.render(str(grid[y][x]), True, BLUE)

                    screen.blit(text, text.get_rect(center=rect.center))

            else:

                pygame.draw.rect(screen, GRAY, rect)

                if flagged[y][x]:
                    pygame.draw.rect(screen, RED, rect)

            pygame.draw.rect(screen, BLACK, rect, 1)


# -----------------------------
# REVEAL TILE
# -----------------------------
def reveal_tile(x, y):

    if revealed[y][x] or flagged[y][x]:
        return

    revealed[y][x] = True

    if grid[y][x] == 0:

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:

                nx = x + dx
                ny = y + dy

                if 0 <= nx < COLS and 0 <= ny < ROWS:
                    reveal_tile(nx, ny)


# -----------------------------
# CHECK WIN
# -----------------------------
def check_win():

    for y in range(ROWS):
        for x in range(COLS):

            if grid[y][x] != "M" and not revealed[y][x]:
                return False

    return True


# -----------------------------
# RESTART GAME
# -----------------------------
def restart_game():

    global grid
    global revealed
    global flagged
    global game_over
    global game_won
    global start_time

    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

    revealed = [[False for _ in range(COLS)] for _ in range(ROWS)]

    flagged = [[False for _ in range(COLS)] for _ in range(ROWS)]

    place_mines(grid)
    setup_grid(grid)

    game_over = False
    game_won = False

    start_time = time.time()


# -----------------------------
# INITIALIZE GAME
# -----------------------------
place_mines(grid)
setup_grid(grid)

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:

    screen.fill(WHITE)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                restart_game()

            # SHOW LEADERBOARD
            if event.key == pygame.K_l:

                scores = minesweeper_db.get_top_scores()

                print("\n=== LEADERBOARD ===")
                print(f"{'ID':<5} | {'Player Name':<20} | {'Time Taken'}")
                print("-" * 45)

                for score in scores:
                    print(f"{score[0]:<5} | {score[1]:<20} | {score[2]}")

            # CREATE SCORE (Manual)
            if event.key == pygame.K_c:
                name = input("\nEnter name to insert: ")
                try:
                    time_val = float(input("Enter time taken: "))
                    minesweeper_db.insert_score(name, time_val)
                    print(f"Inserted score for {name} ({time_val}s)!")
                except ValueError:
                    print("Invalid time entered.")

            # READ ALL SCORES
            if event.key == pygame.K_a:
                scores = minesweeper_db.get_all_scores()
                print("\n=== ALL SCORES ===")
                print(f"{'ID':<5} | {'Player Name':<20} | {'Time Taken'}")
                print("-" * 45)
                for score in scores:
                    print(f"{score[0]:<5} | {score[1]:<20} | {score[2]}")

            # UPDATE SCORE
            if event.key == pygame.K_u:
                try:
                    score_id = int(input("\nEnter ID to update: "))
                    existing = minesweeper_db.get_score_by_id(score_id)
                    if not existing:
                        print(f"No score found with ID {score_id}")
                    else:
                        old_name, old_time = existing
                        new_name = input(f"Enter new name (leave blank to keep '{old_name}'): ")
                        if not new_name.strip():
                            new_name = old_name
                        time_input = input(f"Enter new time (leave blank to keep {old_time}): ")
                        new_time = float(time_input) if time_input.strip() else old_time
                        if minesweeper_db.update_score(score_id, new_name, new_time):
                            print(f"Updated score ID {score_id} to Name: {new_name}, Time: {new_time}s!")
                except ValueError:
                    print("Invalid input entered.")

            # DELETE SCORE
            if event.key == pygame.K_d:
                try:
                    score_id = int(input("\nEnter ID to delete: "))
                    minesweeper_db.delete_score(score_id)
                    print(f"Deleted score ID {score_id}!")
                except ValueError:
                    print("Invalid ID entered.")

        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:

            mx, my = pygame.mouse.get_pos()

            x = mx // TILE_SIZE
            y = my // TILE_SIZE

            # LEFT CLICK
            if event.button == 1:

                if grid[y][x] == "M":

                    game_over = True

                    # Reveal mines
                    for ry in range(ROWS):
                        for rx in range(COLS):

                            if grid[ry][rx] == "M":
                                revealed[ry][rx] = True

                else:
                    reveal_tile(x, y)

            # RIGHT CLICK
            elif event.button == 3:
                flagged[y][x] = not flagged[y][x]

    draw_grid()

    # -----------------------------
    # WIN CONDITION
    # -----------------------------
    if check_win() and not game_over:

        game_over = True
        game_won = True

        end_time = time.time()

        total_time = round(end_time - start_time, 2)

        print("YOU WIN!")
        print("Time:", total_time)

        player_name = input("Enter your name: ")

        minesweeper_db.insert_score(player_name, total_time)

        print("Score saved!")

    # -----------------------------
    # GAME OVER DISPLAY
    # -----------------------------
    if game_over:

        if game_won:
            message = "YOU WIN!"
            color = BLUE
        else:
            message = "GAME OVER!"
            color = RED

        text = font.render(message, True, color)

        screen.blit(
            text,
            (
                WIDTH // 2 - text.get_width() // 2,
                HEIGHT // 2 - text.get_height() // 2,
            ),
        )

        restart_text = font.render("Press R to Restart", True, BLACK)

        screen.blit(
            restart_text,
            (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 30),
        )

    pygame.display.flip()
