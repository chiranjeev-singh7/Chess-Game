import pygame
import chess
from enum import Enum

class GameMode(Enum):
    HUMAN_VS_HUMAN = 1
    HUMAN_VS_AI = 2


# Constants
BOARD_WIDTH = 640
SIDE_PANEL_WIDTH = 160
WIDTH = BOARD_WIDTH + SIDE_PANEL_WIDTH
HEIGHT = 640
ROWS, COLS = 8, 8
SQUARE_SIZE = BOARD_WIDTH // COLS


AI_COLOR = chess.BLACK  # or chess.WHITE depending on your preference
MAX_DEPTH = 3  # Keep it 2–3 to start; higher is slower


# Colors
WHITE = (240, 217, 181)
BROWN = (181, 136, 99)
HIGHLIGHT = (100, 200, 100)
CHECK_HIGHLIGHT = (255, 0, 0)  # Red border for king in check


BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
BUTTON_PADDING = 10

UNDO_BUTTON_RECT = pygame.Rect(BOARD_WIDTH + 20, 40, BUTTON_WIDTH, BUTTON_HEIGHT)
RESET_BUTTON_RECT = pygame.Rect(BOARD_WIDTH + 20, 100, BUTTON_WIDTH, BUTTON_HEIGHT)
MENU_BUTTON_RECT = pygame.Rect(BOARD_WIDTH + 20, 160, BUTTON_WIDTH, BUTTON_HEIGHT)


# Init Pygame
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Chess")

def show_menu(win):
    win.fill((30, 30, 30))
    font = pygame.font.SysFont("Arial", 36, True)
    small_font = pygame.font.SysFont("Arial", 24)

    title = font.render("Python Chess", True, (255, 255, 255))
    title_rect = title.get_rect(center=(WIDTH // 2, 80))
    win.blit(title, title_rect)

    btn_hvh = pygame.Rect(WIDTH // 2 - 100, 150, 200, 50)
    btn_hvai = pygame.Rect(WIDTH // 2 - 100, 220, 200, 50)

    pygame.draw.rect(win, (200, 200, 200), btn_hvh)
    pygame.draw.rect(win, (200, 200, 200), btn_hvai)

    txt1 = small_font.render("Human vs Human", True, (0, 0, 0))
    txt2 = small_font.render("Human vs AI", True, (0, 0, 0))
    win.blit(txt1, txt1.get_rect(center=btn_hvh.center))
    win.blit(txt2, txt2.get_rect(center=btn_hvai.center))

    instructions = small_font.render("Press 'U' to undo, 'R' to restart", True, (180, 180, 180))
    win.blit(instructions, instructions.get_rect(center=(WIDTH // 2, 320)))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_hvh.collidepoint(event.pos):
                    return GameMode.HUMAN_VS_HUMAN
                elif btn_hvai.collidepoint(event.pos):
                    return GameMode.HUMAN_VS_AI


# Load images
PIECE_IMAGES = {}
PIECES = ['P', 'N', 'B', 'R', 'Q', 'K']
for color in ['w', 'b']:
    for piece in PIECES:
        img = pygame.image.load(f"images/{color}{piece}.png")
        PIECE_IMAGES[f"{color}{piece}"] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))

# Draw chess board
def draw_board(win, board, selected_square=None):
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(win, color, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    # Highlight selected square and legal moves
    if selected_square is not None:
        col = chess.square_file(selected_square)
        row = 7 - chess.square_rank(selected_square)
        pygame.draw.rect(win, HIGHLIGHT, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)

        for move_square in get_legal_moves_for_square(board, selected_square):
            mc = chess.square_file(move_square)
            mr = 7 - chess.square_rank(move_square)
            center = (mc*SQUARE_SIZE + SQUARE_SIZE//2, mr*SQUARE_SIZE + SQUARE_SIZE//2)
            target_piece = board.piece_at(move_square)

            if target_piece:
                # Capture move: red border square
                rect = pygame.Rect(mc*SQUARE_SIZE, mr*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(win, (255, 0, 0), rect, width=4)
            else:
                # Normal move: hollow green circle
                pygame.draw.circle(win, (0, 180, 0), center, 12, width=3)


    # Highlight king in check
    if board.is_check():
        king_square = board.king(board.turn)  # Returns square of the king in check
        col = chess.square_file(king_square)
        row = 7 - chess.square_rank(king_square)
        pygame.draw.rect(win, CHECK_HIGHLIGHT, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 5)


    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - (square // 8)
            col = square % 8
            color = 'w' if piece.color == chess.WHITE else 'b'
            piece_str = f"{color}{piece.symbol().upper()}"
            WIN.blit(PIECE_IMAGES[piece_str], (col*SQUARE_SIZE, row*SQUARE_SIZE))

    draw_buttons(win)
    pygame.display.update()

def show_promotion_menu(win, color, square):
    font = pygame.font.SysFont("Arial", 24, True)
    choices = ['q', 'r', 'b', 'n']
    piece_names = {'q': 'Queen', 'r': 'Rook', 'b': 'Bishop', 'n': 'Knight'}

    # Determine menu position near promotion square
    file = chess.square_file(square)
    rank = 7 - chess.square_rank(square)
    menu_x = file * SQUARE_SIZE
    menu_y = rank * SQUARE_SIZE
    if menu_y > HEIGHT - 4 * SQUARE_SIZE:
        menu_y -= 4 * SQUARE_SIZE  # Adjust upward if near bottom

    buttons = []
    for i, c in enumerate(choices):
        rect = pygame.Rect(menu_x, menu_y + i * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        buttons.append((rect, c))
        pygame.draw.rect(win, (240, 240, 240), rect)
        pygame.draw.rect(win, (0, 0, 0), rect, 2)
        piece_str = f"{'w' if color == chess.WHITE else 'b'}{c.upper()}"
        win.blit(PIECE_IMAGES[piece_str], rect)

    pygame.display.update()

    # Wait for user to click one
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for rect, code in buttons:
                    if rect.collidepoint(event.pos):
                        return {
                            'q': chess.QUEEN,
                            'r': chess.ROOK,
                            'b': chess.BISHOP,
                            'n': chess.KNIGHT
                        }[code]



def draw_buttons(win):
    font = pygame.font.SysFont("Arial", 22)

    # Undo
    pygame.draw.rect(win, (200, 200, 200), UNDO_BUTTON_RECT)
    undo_text = font.render("Undo", True, (0, 0, 0))
    win.blit(undo_text, undo_text.get_rect(center=UNDO_BUTTON_RECT.center))

    # Restart
    pygame.draw.rect(win, (200, 200, 200), RESET_BUTTON_RECT)
    reset_text = font.render("Restart", True, (0, 0, 0))
    win.blit(reset_text, reset_text.get_rect(center=RESET_BUTTON_RECT.center))

    # Back to Menu
    pygame.draw.rect(win, (200, 200, 200), MENU_BUTTON_RECT)
    menu_text = font.render("Main Menu", True, (0, 0, 0))
    win.blit(menu_text, menu_text.get_rect(center=MENU_BUTTON_RECT.center))


piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0  # King value is handled via checkmate
}

def evaluate_board(board):
    if board.is_checkmate():
        return -9999 if board.turn == AI_COLOR else 9999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    eval = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            eval += value if piece.color == AI_COLOR else -value
    return eval


def minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None
    if maximizing:
        max_eval = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move



def get_square_under_mouse(pos):
    x, y = pos
    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE
    square = chess.square(col, 7 - row)  # Convert GUI row to chess rank
    return square

def get_legal_moves_for_square(board, square):
    return [move.to_square for move in board.legal_moves if move.from_square == square]


def display_message(win, message):
    font = pygame.font.SysFont("Arial", 32, True)
    text = font.render(message, True, (200, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    win.blit(text, text_rect)
    pygame.display.update()

def get_game_status(board):
    if board.is_checkmate():
        return "Checkmate! " + ("White" if board.turn == chess.BLACK else "Black") + " wins."
    elif board.is_stalemate():
        return "Stalemate!"
    elif board.is_insufficient_material():
        return "Draw by insufficient material."
    elif board.can_claim_fifty_moves():
        return "Draw by 50-move rule."
    elif board.can_claim_threefold_repetition():
        return "Draw by repetition."
    return None




def main():
    game_mode = show_menu(WIN)

    board = chess.Board()
    selected = None
    running = True
    game_over = False
    status_message = ""

    while running:
        draw_board(WIN, board, selected)
        if game_over:
            display_message(WIN, status_message)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Undo / Restart buttons
                if UNDO_BUTTON_RECT.collidepoint(mouse_pos):
                    if board.move_stack:
                        board.pop()
                        game_over = False
                        status_message = ""
                        selected = None

                elif RESET_BUTTON_RECT.collidepoint(mouse_pos):
                    board.reset()
                    selected = None
                    game_over = False
                    status_message = ""

                elif MENU_BUTTON_RECT.collidepoint(mouse_pos):
                    # Go back to main menu
                    game_mode = show_menu(WIN)
                    board.reset()
                    selected = None
                    game_over = False
                    status_message = ""

                elif not game_over:
                    square = get_square_under_mouse(mouse_pos)
                    if selected is None:
                        if board.piece_at(square) and board.piece_at(square).color == board.turn:
                            selected = square
                    else:
                        move = chess.Move(selected, square)
                        piece = board.piece_at(selected)
                        is_pawn_promo = (
                            piece and 
                            piece.piece_type == chess.PAWN and 
                            (chess.square_rank(square) == 0 or chess.square_rank(square) == 7)
                        )

                        if is_pawn_promo:
                            if chess.Move(selected, square, promotion=chess.QUEEN) in board.legal_moves:
                                promotion_piece = show_promotion_menu(WIN, piece.color, square)
                                move = chess.Move(selected, square, promotion=promotion_piece)

                        if move in board.legal_moves:
                            board.push(move)


                            selected = None
                            status_message = get_game_status(board)
                            if status_message:
                                game_over = True

                            # Let AI play after human
                            if game_mode == GameMode.HUMAN_VS_AI and board.turn == AI_COLOR and not board.is_game_over():
                                _, ai_move = minimax(board, MAX_DEPTH, -float('inf'), float('inf'), True)
                                if ai_move:
                                    # Handle AI pawn promotion
                                    if ai_move.promotion is None and board.piece_at(ai_move.from_square).piece_type == chess.PAWN:
                                        if chess.square_rank(ai_move.to_square) in [0, 7]:
                                            ai_move = chess.Move(ai_move.from_square, ai_move.to_square, promotion=chess.QUEEN)

                                    board.push(ai_move)

                                    selected = None
                                    status_message = get_game_status(board)
                                    if status_message:
                                        game_over = True
                        else:
                            selected = None

    pygame.quit()


if __name__ == "__main__":
    main()
