import pygame
import sys

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
CURSOR_COLOR = (255, 255, 255)  # Darker cursor color

# Set window size
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Puzzle League")

font = pygame.font.SysFont(None, 24)

def initialize_board():
    """Initializes a simple 6x6 board with a predefined setup for demonstration."""
    return [
        [' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', ' ', ' ', ' '],
        [' ', ' ', ' ', 'G', ' ', ' '],
        [' ', 'G', 'G', 'P', ' ', ' '],
        [' ', 'P', 'G', 'P', ' ', ' '],
        [' ', 'P', 'P', 'G', 'P', 'G'],
    ]
def reset_game(board, cursor_pos):
    """Resets the game to the initial state."""
    new_board = initialize_board()  # Reinitialize the board
    cursor_pos[0], cursor_pos[1] = 0, 0  # Reset cursor to the starting position
    return new_board
def draw_board(board, cursor_pos):
    for i, row in enumerate(board):
        for j, block in enumerate(row):
            rect = (BOARD_POS[0] + j * BLOCK_SIZE, BOARD_POS[1] + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, BLOCK_COLORS[block], rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)  # Draw border

    # Draw the cursor
    cursor_rect = (BOARD_POS[0] + cursor_pos[1] * BLOCK_SIZE, BOARD_POS[1] + cursor_pos[0] * BLOCK_SIZE, BLOCK_SIZE * 2, BLOCK_SIZE)
    pygame.draw.rect(screen, CURSOR_COLOR, cursor_rect, 4)  # Thicker border for cursor

def find_matches(board):
    """Finds all matches of three or more blocks in a row or column."""
    matched = set()
    # Horizontal matches
    for row in range(HEIGHT):
        for col in range(WIDTH - 2):
            if board[row][col] == board[row][col + 1] == board[row][col + 2] != ' ':
                matched.update([(row, col), (row, col + 1), (row, col + 2)])

    # Vertical matches
    for col in range(WIDTH):
        for row in range(HEIGHT - 2):
            if board[row][col] == board[row + 1][col] == board[row + 2][col] != ' ':
                matched.update([(row, col), (row + 1, col), (row + 2, col)])

    return matched

def clear_matches(board, matched):
    """Clears the blocks that are part of a match."""
    for row, col in matched:
        board[row][col] = ' '

def collapse_board(board):
    """Collapses the board to fill in gaps from cleared blocks, letting blocks fall only where gaps exist."""
    for col in range(WIDTH):
        # Iterate from the bottom of the column up to the top
        for row in range(HEIGHT - 1, 0, -1):
            if board[row][col] == ' ':  # There's a gap
                # Find the first non-empty block above this gap
                for above in range(row - 1, -1, -1):
                    if board[above][col] != ' ':
                        # Move this block down into the gap
                        board[row][col] = board[above][col]
                        board[above][col] = ' '  # Clear the original location
                        break  # Only the first non-empty block above should fall into the gap


def process_game_logic(board):
    """Handles match finding, clearing, and collapsing, allowing for chain reactions."""
    while True:  # Start an indefinite loop to handle potential chains
        collapse_board(board)
        matches = find_matches(board)
        if matches:
            clear_matches(board, matched=matches)
            collapse_board(board)
            print("Chain reaction triggered!")  # Optional: print statement for debugging
        else:
            collapse_board(board)
            break  # Exit the loop if no matches are found


def main():
    board = initialize_board()
    cursor_pos = [0, 0]  # Starting position of the cursor [row, column]
    clock = pygame.time.Clock()
    move_count = 0  # Initialize move count
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:  # Correct usage of == for comparison
                if event.key == pygame.K_LEFT:
                    cursor_pos[1] = max(0, cursor_pos[1] - 1)  # Move cursor left within bounds
                elif event.key == pygame.K_RIGHT:
                    cursor_pos[1] = min(WIDTH - 2, cursor_pos[1] + 1)  # Move cursor right within bounds
                elif event.key == pygame.K_UP:
                    cursor_pos[0] = max(0, cursor_pos[0] - 1)  # Move cursor up within bounds
                elif event.key == pygame.K_DOWN:
                    cursor_pos[0] = min(HEIGHT - 1, cursor_pos[0] + 1)  # Move cursor down within bounds
                elif event.key == pygame.K_RETURN:
                    # Ensure that the cursor is in a position to swap (not at the edge of the board)
                    if cursor_pos[1] < WIDTH - 1:
                        # Swap the blocks horizontally adjacent
                        temp = board[cursor_pos[0]][cursor_pos[1]]
                        board[cursor_pos[0]][cursor_pos[1]] = board[cursor_pos[0]][cursor_pos[1] + 1]
                        board[cursor_pos[0]][cursor_pos[1] + 1] = temp
                        
                        print("Swapped blocks at ({}, {}) and ({}, {})".format(
                            cursor_pos[0], cursor_pos[1], cursor_pos[0], cursor_pos[1] + 1))

                        # Process the game logic after swapping
                        process_game_logic(board)
                        move_count += 1  # Increment move count on valid move
                    else:
                        print("Cursor at edge, no swap possible.")
                elif event.key == pygame.K_BACKSPACE:
                    board = reset_game(board, cursor_pos)  # Reset the game when Backspace is pressed
                    move_count = 0  # Reset move count


        screen.fill(BACKGROUND_COLOR)
        draw_board(board, cursor_pos)
        # Display move count on the right-hand side
        move_text = font.render("Moves: {}".format(move_count), True, TEXT_COLOR)
        screen.blit(move_text, MOVE_COUNT_POS)
        controls_text = [
            "Controls:",
            "Arrow keys: Move cursor",
            "Enter: Swap blocks",
            "Backspace: Reset game"
        ]

        # Display move count on the right-hand side
        move_text = font.render("Moves: {}".format(move_count), True, TEXT_COLOR)
        screen.blit(move_text, MOVE_COUNT_POS)

        # Display controls text below the move count
        control_y_pos = MOVE_COUNT_POS[1] + move_text.get_height() + 10  # Adjust vertical position
        for i, line in enumerate(controls_text):
            control_text = font.render(line, True, TEXT_COLOR)
            control_text_pos = (MOVE_COUNT_POS[0], control_y_pos + i * (control_text.get_height() + 5))
            screen.blit(control_text, control_text_pos)

        pygame.display.flip()
        clock.tick(30)  # Limits the frame rate to 30 FPS
        
if __name__ == "__main__":
    main()
