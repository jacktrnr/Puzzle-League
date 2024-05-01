import pygame
import sys
from collections import deque

# Constants
BLOCK_SIZE = 60  # Size of the block
BOARD_POS = (100, 100)  # Top-left position of the board on the window
WIDTH = 6  # Width of the board
HEIGHT = 6  # Height of the board
MOVE_COUNT_POS = (500, 100)  # Position of the move count text
# Colors
BACKGROUND_COLOR = (60, 60, 60)
BLOCK_COLORS = {
    'R': (255, 0, 0),
    'G': (0, 255, 0),
    'B': (0, 0, 255),
    'P': (255, 0, 255),
    ' ': (0, 0, 0)  # Empty space color
}
TEXT_COLOR = (255, 255, 255)
CURSOR_COLOR = (255, 255, 255)

# Set window size
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Puzzle League")
font = pygame.font.SysFont(None, 24)

def initialize_board():
    return [
        [' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', 'G', ' ', ' '],
        [' ', 'G', 'G', 'P', ' ', ' '],
        [' ', 'P', 'G', 'P', ' ', ' '],
        [' ', 'P', 'P', 'G', 'P', 'G'],
    ]

def reset_game(board, cursor_pos):
    new_board = initialize_board()
    cursor_pos[0], cursor_pos[1] = 5, 0
    return new_board

def draw_board(board, cursor_pos):
    for i, row in enumerate(board):
        for j, block in enumerate(row):
            rect = (BOARD_POS[0] + j * BLOCK_SIZE, BOARD_POS[1] + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, BLOCK_COLORS[block], rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)
    cursor_rect = (BOARD_POS[0] + cursor_pos[1] * BLOCK_SIZE, BOARD_POS[1] + cursor_pos[0] * BLOCK_SIZE, BLOCK_SIZE * 2, BLOCK_SIZE)
    pygame.draw.rect(screen, CURSOR_COLOR, cursor_rect, 4)

def find_matches(board):
    matched = set()
    for row in range(HEIGHT):
        for col in range(WIDTH - 2):
            if board[row][col] == board[row][col + 1] == board[row][col + 2] != ' ':
                matched.update([(row, col), (row, col + 1), (row, col + 2)])
    for col in range(WIDTH):
        for row in range(HEIGHT - 2):
            if board[row][col] == board[row + 1][col] == board[row + 2][col] != ' ':
                matched.update([(row, col), (row + 1, col), (row + 2, col)])
    return matched

def clear_matches(board, matched):
    for row, col in matched:
        board[row][col] = ' '

def collapse_board(board):
    for col in range(WIDTH):
        for row in range(HEIGHT - 1, 0, -1):
            if board[row][col] == ' ':
                for above in range(row - 1, -1, -1):
                    if board[above][col] != ' ':
                        board[row][col] = board[above][col]
                        board[above][col] = ' '
                        break

def process_game_logic(board):
    while True:
        collapse_board(board)
        matches = find_matches(board)
        if matches:
            clear_matches(board, matched=matches)
            collapse_board(board)
        else:
            break

def bfs_solve(board):
    queue = deque([(board, [])])
    seen = set()
    while queue:
        current_board, moves = queue.popleft()
        if not any(item for row in current_board for item in row if item != ' '):
            return moves  # Return the first solution found
        for i in range(HEIGHT):
            for j in range(WIDTH - 1):
                new_board = [row[:] for row in current_board]
                new_board[i][j], new_board[i][j+1] = new_board[i][j+1], new_board[i][j]
                process_game_logic(new_board)
                board_id = tuple(tuple(row) for row in new_board)
                if board_id not in seen:
                    seen.add(board_id)
                    queue.append((new_board, moves + [(i, j, i, j+1)]))

def main():
    board = initialize_board()
    cursor_pos = [5, 0]
    clock = pygame.time.Clock()
    move_count = 0
    moves_to_solve = bfs_solve([row[:] for row in board])  # Calculate minimum moves at game start

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    cursor_pos[1] = max(0, cursor_pos[1] - 1)
                elif event.key == pygame.K_RIGHT:
                    cursor_pos[1] = min(WIDTH - 2, cursor_pos[1] + 1)
                elif event.key == pygame.K_UP:
                    cursor_pos[0] = max(0, cursor_pos[0] - 1)
                elif event.key == pygame.K_DOWN:
                    cursor_pos[0] = min(HEIGHT - 1, cursor_pos[0] + 1)
                elif event.key == pygame.K_RETURN:
                    if cursor_pos[1] < WIDTH - 1:
                        temp = board[cursor_pos[0]][cursor_pos[1]]
                        board[cursor_pos[0]][cursor_pos[1]] = board[cursor_pos[0]][cursor_pos[1] + 1]
                        board[cursor_pos[0]][cursor_pos[1] + 1] = temp
                        process_game_logic(board)
                        move_count += 1
                elif event.key == pygame.K_BACKSPACE:
                    board = reset_game(board, cursor_pos)
                    move_count = 0  # Do not recalculate moves_to_solve

        screen.fill(BACKGROUND_COLOR)
        draw_board(board, cursor_pos)
        move_text = font.render("Moves: {}".format(move_count), True, TEXT_COLOR)
        screen.blit(move_text, MOVE_COUNT_POS)
        if moves_to_solve is not None:
            solution_text = font.render("Min Moves to Solve: {}".format(len(moves_to_solve)), True, TEXT_COLOR)
            screen.blit(solution_text, (MOVE_COUNT_POS[0], MOVE_COUNT_POS[1] + 30))

        # Display control instructions
        controls_text = [
            "Controls:",
            "Arrow keys: Move cursor",
            "Enter: Swap blocks",
            "Backspace: Reset game"
        ]
        control_y_pos = MOVE_COUNT_POS[1] + 60  # Adjust vertical position for control instructions
        for i, line in enumerate(controls_text):
            control_text = font.render(line, True, TEXT_COLOR)
            control_text_pos = (MOVE_COUNT_POS[0], control_y_pos + i * (control_text.get_height() + 5))
            screen.blit(control_text, control_text_pos)

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
