import pygame
import random
import heapq
import os

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 600, 500  # Increased the height to add space for buttons
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game with A* Pathfinding")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 128)
OVERLAY = (0, 0, 0, 180)  # Semi-transparent black

# Grid settings
CELL_SIZE = 20
SCORE_HEIGHT = 50  # Height reserved for score display
GRID_HEIGHT = (HEIGHT - SCORE_HEIGHT - 50) // CELL_SIZE  # Adjusted for button space
GRID_WIDTH = WIDTH // CELL_SIZE

# Directions
DIRECTIONS = {
    'UP': (0, -1),
    'DOWN': (0, 1),
    'LEFT': (-1, 0),
    'RIGHT': (1, 0)
}

# A* Algorithm components
class Node:
    def __init__(self, x, y, cost, heuristic, parent=None):
        self.x = x
        self.y = y
        self.cost = cost
        self.heuristic = heuristic
        self.parent = parent

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(start, goal, snake_body):
    open_list = []
    heapq.heappush(open_list, Node(start[0], start[1], 0, heuristic(start, goal)))
    closed_list = set()

    while open_list:
        current = heapq.heappop(open_list)
        if (current.x, current.y) == goal:
            path = []
            while current:
                path.append((current.x, current.y))
                current = current.parent
            return path[::-1][1:]

        closed_list.add((current.x, current.y))
        for direction in DIRECTIONS.values():
            neighbor = (current.x + direction[0], current.y + direction[1])
            if 0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT and neighbor not in snake_body:
                if neighbor not in closed_list:
                    neighbor_node = Node(neighbor[0], neighbor[1], current.cost + 1, heuristic(neighbor, goal), current)
                    heapq.heappush(open_list, neighbor_node)

    return None

# Drawing functions
def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(WIN, GRAY, (x, SCORE_HEIGHT), (x, HEIGHT - 50))
    for y in range(SCORE_HEIGHT, HEIGHT - 50, CELL_SIZE):
        pygame.draw.line(WIN, GRAY, (0, y), (WIDTH, y))

def draw_snake(snake):
    for segment in snake:
        pygame.draw.rect(WIN, GREEN, pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE + SCORE_HEIGHT, CELL_SIZE, CELL_SIZE))

def draw_food(food):
    pygame.draw.rect(WIN, RED, pygame.Rect(food[0] * CELL_SIZE, food[1] * CELL_SIZE + SCORE_HEIGHT, CELL_SIZE, CELL_SIZE))

def draw_score(score, high_score):
    font = pygame.font.SysFont('comicsans', 30)
    score_text = font.render(f'Score: {score}', True, WHITE)
    high_score_text = font.render(f'High Score: {high_score}', True, WHITE)
    WIN.blit(score_text, (10, 0))
    WIN.blit(high_score_text, (WIDTH - 250, 0))

def draw_buttons():
    font = pygame.font.SysFont('comicsans', 20)
    
    # Restart Button
    restart_button = pygame.Rect(WIDTH // 4 - 75, HEIGHT - 45, 150, 40)  # Positioned on the bottom left
    pygame.draw.rect(WIN, DARK_BLUE, restart_button, border_radius=12)
    pygame.draw.rect(WIN, LIGHT_BLUE, restart_button.inflate(-4, -4), border_radius=12)
    restart_text = font.render("Restart", True, WHITE)
    WIN.blit(restart_text, (restart_button.x + (restart_button.width - restart_text.get_width()) // 2, 
                            restart_button.y + (restart_button.height - restart_text.get_height()) // 2))

    # Quit Button
    quit_button = pygame.Rect(WIDTH * 3 // 4 - 75, HEIGHT - 45, 150, 40)  # Positioned on the bottom right
    pygame.draw.rect(WIN, DARK_BLUE, quit_button, border_radius=12)
    pygame.draw.rect(WIN, LIGHT_BLUE, quit_button.inflate(-4, -4), border_radius=12)
    quit_text = font.render("Quit", True, WHITE)
    WIN.blit(quit_text, (quit_button.x + (quit_button.width - quit_text.get_width()) // 2, 
                         quit_button.y + (quit_button.height - quit_text.get_height()) // 2))

    # End Game Button
    end_game_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 45, 150, 40)  # Positioned at the bottom center
    pygame.draw.rect(WIN, DARK_BLUE, end_game_button, border_radius=12)
    pygame.draw.rect(WIN, LIGHT_BLUE, end_game_button.inflate(-4, -4), border_radius=12)
    end_game_text = font.render("End Game", True, WHITE)
    WIN.blit(end_game_text, (end_game_button.x + (end_game_button.width - end_game_text.get_width()) // 2, 
                             end_game_button.y + (end_game_button.height - end_game_text.get_height()) // 2))

    return restart_button, quit_button, end_game_button


def draw_obstacles(obstacles):
    for obs in obstacles:
        pygame.draw.rect(WIN, BLUE, pygame.Rect(obs[0] * CELL_SIZE, obs[1] * CELL_SIZE + SCORE_HEIGHT, CELL_SIZE, CELL_SIZE))

def game_over_screen():
    overlay_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay_surface.fill(OVERLAY)
    WIN.blit(overlay_surface, (0, 0))

    # Change font size for "GAME OVER" text
    game_over_font = pygame.font.SysFont('comicsans', 60, bold=True)  # Adjust the size to your preference
    game_over_text = game_over_font.render("GAME OVER", True, RED)
    shadow = game_over_font.render("GAME OVER", True, BLACK)
    WIN.blit(shadow, (WIDTH // 2 - game_over_text.get_width() // 2 + 2, HEIGHT // 3 - game_over_text.get_height() // 2 + 2))
    WIN.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 3 - game_over_text.get_height() // 2))
    
    # Keep the button size the same
    font = pygame.font.SysFont('comicsans', 20, bold=True)  # Font size for the buttons

    restart_button = pygame.Rect(WIDTH // 4 - 75, HEIGHT // 2 + 50, 150, 50)
    quit_button = pygame.Rect(WIDTH * 3 // 4 - 75, HEIGHT // 2 + 50, 150, 50)

    pygame.draw.rect(WIN, DARK_BLUE, restart_button, border_radius=12)
    pygame.draw.rect(WIN, LIGHT_BLUE, restart_button.inflate(-4, -4), border_radius=12)
    pygame.draw.rect(WIN, DARK_BLUE, quit_button, border_radius=12)
    pygame.draw.rect(WIN, LIGHT_BLUE, quit_button.inflate(-4, -4), border_radius=12)

    restart_text = font.render("Restart", True, WHITE)
    quit_text = font.render("Quit", True, WHITE)

    WIN.blit(restart_text, (restart_button.x + (restart_button.width - restart_text.get_width()) // 2, 
                            restart_button.y + (restart_button.height - restart_text.get_height()) // 2))
    WIN.blit(quit_text, (quit_button.x + (quit_button.width - quit_text.get_width()) // 2, 
                         quit_button.y + (quit_button.height - quit_text.get_height()) // 2))

    pygame.display.flip()

    return restart_button, quit_button



def generate_food(snake):
    empty_cells = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT) if (x, y) not in snake]
    if empty_cells:
        return random.choice(empty_cells)
    return None  # Return None if there are no empty cells

def generate_obstacles(snake, food, num_obstacles):
    empty_cells = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT) if (x, y) not in snake and (x, y) != food]
    return random.sample(empty_cells, min(num_obstacles, len(empty_cells)))

def load_high_score():
    if os.path.exists("high_score.txt"):
        with open("high_score.txt", "r") as file:
            return int(file.read())
    return 0

# Save high score to file
def save_high_score(score):
    with open("high_score.txt", "w") as file:
        file.write(str(score))

def main():
    # Initialize variables
    clock = pygame.time.Clock()
    snake = [(10, 10)]
    direction = 'RIGHT'
    food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
    obstacles = generate_obstacles(snake, food, 10)  # Generate 10 obstacles
    path = []
    score = 0
    high_score = load_high_score()

    # Game loop
    run = True
    while run:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if restart_button.collidepoint(mouse_pos):
                    main()  # Restart the game
                    return  # Exit current game loop after starting a new game
                elif quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    return
                elif end_game_button.collidepoint(mouse_pos):
                    # Trigger game over screen
                    WIN.fill(BLACK)
                    restart_button, quit_button = game_over_screen()
                    pygame.display.flip()
                    
                    # Handle game over screen loop
                    while True:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                return
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                mouse_pos = pygame.mouse.get_pos()
                                if restart_button.collidepoint(mouse_pos):
                                    main()  # Restart the game
                                    return
                                elif quit_button.collidepoint(mouse_pos):
                                    pygame.quit()
                                    return

        # Draw and update game elements
        WIN.fill(BLACK)
        draw_grid()
        draw_snake(snake)
        draw_food(food)
        draw_obstacles(obstacles)
        draw_score(score, high_score)

        # Draw all buttons, including the End Game button
        restart_button, quit_button, end_game_button = draw_buttons()

        # Continue game logic
        if not path:
            path = a_star(snake[0], food, snake + obstacles)
            print(f"New path: {path}")

        if path:
            next_step = path.pop(0)
            delta_x, delta_y = next_step[0] - snake[0][0], next_step[1] - snake[0][1]
            print(f"Next step: {next_step}, Delta: ({delta_x}, {delta_y})")
            possible_directions = [key for key, value in DIRECTIONS.items() if value == (delta_x, delta_y)]
            if possible_directions:
                direction = possible_directions[0]
            else:
                print(f"Error: No matching direction for delta ({delta_x}, {delta_y})")
                path = []

        new_head = (snake[0][0] + DIRECTIONS[direction][0], snake[0][1] + DIRECTIONS[direction][1])
        snake.insert(0, new_head)

        if snake[0] == food:
            food = generate_food(snake + obstacles)
            score += 1
            if score > high_score:
                high_score = score
                save_high_score(high_score)
        else:
            snake.pop()

        if new_head in snake[1:] or not (0 <= snake[0][0] < GRID_WIDTH) or not (0 <= snake[0][1] < GRID_HEIGHT) or new_head in obstacles:
            WIN.fill(BLACK)
            restart_button, quit_button = game_over_screen()
            pygame.display.flip()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if restart_button.collidepoint(mouse_pos):
                            main()  # Restart the game
                            return
                        elif quit_button.collidepoint(mouse_pos):
                            pygame.quit()
                            return

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
