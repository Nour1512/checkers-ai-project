import sys
import time
import random
from copy import deepcopy
from collections import namedtuple

try:
    import pygame
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False

EMPTY = 0
MAN = 1
KING = 2

WHITE = 1  
BLACK = -1 

Move = namedtuple("Move", ["sequence"])

class Board:
    def __init__(self, board=None, current_player=WHITE):
        if board is None:
            self.board = self._init_board()
        else:
            self.board = board
        self.current_player = current_player
        self.move_count = 0

    def _init_board(self):
        b = [[None]*8 for _ in range(8)]
        for r in range(8):
            for c in range(8):
                if (r + c) % 2 == 0:
                    b[r][c] = None 
                else:
                    if r < 3:
                        b[r][c] = (BLACK, MAN)
                    elif r > 4:
                        b[r][c] = (WHITE, MAN)
                    else:
                        b[r][c] = (EMPTY, EMPTY)
        return b

    def clone(self):
        return Board(board=deepcopy(self.board), current_player=self.current_player)

    def inside(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def get_piece(self, r, c):
        if not self.inside(r, c):
            return None
        val = self.board[r][c]
        if val is None:
            return None
        if val == (EMPTY, EMPTY):
            return (EMPTY, EMPTY)
        return val 

    def set_piece(self, r, c, piece):
        self.board[r][c] = piece

    def is_playable_square(self, r, c):
        return self.inside(r, c) and self.board[r][c] is not None

    def print_board(self):
        print("    0 1 2 3 4 5 6 7")
        print("   ----------------")
        for r in range(8):
            row_s = f"{r} | "
            for c in range(8):
                cell = self.board[r][c]
                if cell is None:
                    row_s += ". "
                elif cell == (EMPTY, EMPTY):
                    row_s += "_ "
                else:
                    player, t = cell
                    if player == WHITE:
                        ch = 'w' if t == MAN else 'W'
                    else:
                        ch = 'b' if t == MAN else 'B'
                    row_s += ch + " "
            print(row_s)
        print(f"Current player: {'WHITE' if self.current_player==WHITE else 'BLACK'}")
        print()

    def generate_legal_moves(self):

        player = self.current_player
        capture_moves = []
        non_capture_moves = []

        for r in range(8):
            for c in range(8):
                piece = self.get_piece(r, c)
                if piece is None or piece == (EMPTY, EMPTY):
                    continue
                pplayer, ptype = piece
                if pplayer != player:
                    continue
                caps = self._generate_captures_from(r, c, ptype)
                if caps:
                    capture_moves.extend([Move(seq) for seq in caps])
                else:
                    steps = self._generate_steps_from(r, c, ptype)
                    non_capture_moves.extend([Move(seq) for seq in steps])

        if capture_moves:
            return capture_moves
        return non_capture_moves

    def _generate_steps_from(self, r, c, ptype):
        player = self.current_player
        dirs = []
        if ptype == MAN:
            dr = -1 if player == WHITE else 1
            dirs = [(dr, -1), (dr, 1)]
        else:  # KING
            dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        moves = []
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            if self.inside(nr, nc) and self.get_piece(nr, nc) == (EMPTY, EMPTY):
                moves.append([(r, c), (nr, nc)])
        return moves

    def _generate_captures_from(self, r, c, ptype):
        player = self.current_player
        results = []

        def dfs(path_board, cur_r, cur_c, path):
            found_any = False
            cur_piece = path_board.get_piece(cur_r, cur_c)
            if cur_piece is None or cur_piece == (EMPTY, EMPTY):
                return
            _, cur_ptype = cur_piece
            if cur_ptype == MAN:
                dirs = [(-1, -1), (-1, 1)] if player == WHITE else [(1, -1), (1, 1)]
            else:
                dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in dirs:
                mid_r, mid_c = cur_r + dr, cur_c + dc
                end_r, end_c = cur_r + 2*dr, cur_c + 2*dc
                if not (path_board.inside(end_r, end_c) and path_board.inside(mid_r, mid_c)):
                    continue
                mid_piece = path_board.get_piece(mid_r, mid_c)
                end_piece = path_board.get_piece(end_r, end_c)
                if mid_piece is None or end_piece is None:
                    continue
                if mid_piece != (EMPTY, EMPTY) and mid_piece[0] == -player and end_piece == (EMPTY, EMPTY):

                    new_board = path_board.clone()
                    new_board.set_piece(mid_r, mid_c, (EMPTY, EMPTY))
                    new_board.set_piece(end_r, end_c, new_board.get_piece(cur_r, cur_c))
                    new_board.set_piece(cur_r, cur_c, (EMPTY, EMPTY))
                    found_any = True
                    dfs(new_board, end_r, end_c, path + [(end_r, end_c)])
            if not found_any:
                if len(path) > 1:
                    results.append(path)

        dfs(self, r, c, [(r, c)])
        return results

    def apply_move(self, move):
        seq = move.sequence
        if not seq or len(seq) < 2:
            return
        start = seq[0]
        piece = self.get_piece(*start)
        if piece is None or piece == (EMPTY, EMPTY):
            raise ValueError("Invalid move start.")
        player, ptype = piece


        r0, c0 = start
        self.set_piece(r0, c0, (EMPTY, EMPTY))
        for (r1, c1) in seq[1:]:
            if abs(r1 - r0) == 2:
                mid_r = (r0 + r1) // 2
                mid_c = (c0 + c1) // 2
                self.set_piece(mid_r, mid_c, (EMPTY, EMPTY))
            r0, c0 = r1, c1
        final_r, final_c = r0, c0
        if ptype == MAN:
            if (player == WHITE and final_r == 0) or (player == BLACK and final_r == 7):
                ptype = KING
        self.set_piece(final_r, final_c, (player, ptype))
        self.current_player = -self.current_player
        self.move_count += 1

    def is_terminal(self, max_moves=200):

        moves = self.generate_legal_moves()
        if not moves:
            winner = -self.current_player
            return True, winner
        if self.move_count >= max_moves:
            return True, 0
        return False, None

    def count_pieces(self):
        counts = {WHITE:0, BLACK:0, 'white_kings':0, 'black_kings':0}
        for r in range(8):
            for c in range(8):
                p = self.get_piece(r, c)
                if p is None or p == (EMPTY, EMPTY):
                    continue
                player, t = p
                if player == WHITE:
                    counts[WHITE] += 1
                    if t == KING:
                        counts['white_kings'] += 1
                else:
                    counts[BLACK] += 1
                    if t == KING:
                        counts['black_kings'] += 1
        return counts

def evaluate_board(board: Board, perspective=WHITE):
    counts = board.count_pieces()
    white_score = counts[WHITE] + 1.6 * counts['white_kings']
    black_score = counts[BLACK] + 1.6 * counts['black_kings']

    cur_player = board.current_player
    moves_current = len(board.generate_legal_moves())

    flipped = board.clone()
    flipped.current_player = -flipped.current_player
    moves_opponent = len(flipped.generate_legal_moves())

    mobility_score = (moves_current - moves_opponent) * 0.05

    base = (white_score - black_score)

    if perspective == WHITE:
        score = base + mobility_score * (1 if board.current_player == WHITE else -1)
    else:
        score = -base + mobility_score * (1 if board.current_player == BLACK else -1)
    return score


class SearchStats:
    def __init__(self):
        self.nodes = 0
        self.max_depth_reached = 0
        self.start_time = None
        self.time = 0.0

class MinimaxAgent:
    def __init__(self, depth=6, use_alphabeta=True):
        self.depth = depth
        self.use_alphabeta = use_alphabeta

    def select_move(self, board: Board):
        stats = SearchStats()
        stats.start_time = time.time()
        if self.use_alphabeta:
            val, move = self.alphabeta_root(board, self.depth, stats)
        else:
            val, move = self.minimax_root(board, self.depth, stats)
        stats.time = time.time() - stats.start_time
        return move, stats

    def minimax_root(self, board, depth, stats):
        best_val = float('-inf') if board.current_player == WHITE else float('inf')
        best_move = None
        stats.nodes += 1
        moves = board.generate_legal_moves()
        if not moves:
            return (float('-inf') if board.current_player == WHITE else float('inf')), None
        for m in moves:
            nb = board.clone()
            nb.apply_move(m)
            val = self._minimax(nb, depth-1, stats, maximizing=(nb.current_player==WHITE))
            if board.current_player == WHITE:
                if val > best_val:
                    best_val = val
                    best_move = m
            else:
                if val < best_val:
                    best_val = val
                    best_move = m
        return best_val, best_move

    def alphabeta_root(self, board, depth, stats):
        alpha = float('-inf')
        beta = float('inf')
        best_val = float('-inf') if board.current_player == WHITE else float('inf')
        best_move = None
        moves = board.generate_legal_moves()
        if not moves:
            return (float('-inf') if board.current_player == WHITE else float('inf')), None
        scored_moves = []
        for m in moves:
            nb = board.clone()
            nb.apply_move(m)
            scored_moves.append((evaluate_board(nb, perspective=board.current_player), m))
        reverse = True if board.current_player == WHITE else False
        scored_moves.sort(key=lambda x: x[0], reverse=reverse)
        for _, m in scored_moves:
            nb = board.clone()
            nb.apply_move(m)
            val = self._alphabeta(nb, depth-1, alpha, beta, stats, maximizing=(nb.current_player==WHITE))
            if board.current_player == WHITE:
                if val > best_val:
                    best_val = val
                    best_move = m
                alpha = max(alpha, best_val)
            else:
                if val < best_val:
                    best_val = val
                    best_move = m
                beta = min(beta, best_val)
        return best_val, best_move

    def _minimax(self, board, depth, stats, maximizing=True):
        stats.nodes += 1
        stats.max_depth_reached = max(stats.max_depth_reached, self.depth - depth)
        term, winner = board.is_terminal()
        if term:
            if winner == 0:
                return 0
            return 1000 * winner
        if depth == 0:
            return evaluate_board(board, perspective=WHITE)

        moves = board.generate_legal_moves()
        if not moves:
            return -1000 if maximizing else 1000

        if maximizing:
            v = float('-inf')
            for m in moves:
                nb = board.clone()
                nb.apply_move(m)
                v = max(v, self._minimax(nb, depth-1, stats, maximizing=(nb.current_player==WHITE)))
            return v
        else:
            v = float('inf')
            for m in moves:
                nb = board.clone()
                nb.apply_move(m)
                v = min(v, self._minimax(nb, depth-1, stats, maximizing=(nb.current_player==WHITE)))
            return v

    def _alphabeta(self, board, depth, alpha, beta, stats, maximizing=True):
        stats.nodes += 1
        stats.max_depth_reached = max(stats.max_depth_reached, self.depth - depth)
        term, winner = board.is_terminal()
        if term:
            if winner == 0:
                return 0
            return 1000 * winner
        if depth == 0:
            return evaluate_board(board, perspective=WHITE)

        moves = board.generate_legal_moves()
        if not moves:
            return -1000 if maximizing else 1000

        scored = []
        for m in moves:
            nb = board.clone()
            nb.apply_move(m)
            scored.append((evaluate_board(nb, perspective=WHITE), m))
        scored.sort(key=lambda x: x[0], reverse=maximizing)

        if maximizing:
            v = float('-inf')
            for _, m in scored:
                nb = board.clone()
                nb.apply_move(m)
                v = max(v, self._alphabeta(nb, depth-1, alpha, beta, stats, maximizing=(nb.current_player==WHITE)))
                alpha = max(alpha, v)
                if alpha >= beta:
                    break
            return v
        else:
            v = float('inf')
            for _, m in scored:
                nb = board.clone()
                nb.apply_move(m)
                v = min(v, self._alphabeta(nb, depth-1, alpha, beta, stats, maximizing=(nb.current_player==WHITE)))
                beta = min(beta, v)
                if beta <= alpha:
                    break
            return v

def human_move_input(board: Board):

    board.print_board()
    legal = board.generate_legal_moves()
    print("Legal moves (index : sequence):")
    for i, m in enumerate(legal):
        print(f"{i}: {m.sequence}")
    while True:
        choice = input("Enter move index (or sequence like 'r0 c0 r1 c1 ...'): ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 0 <= idx < len(legal):
                return legal[idx]
            else:
                print("Index out of range.")
        else:
            parts = choice.split()
            try:
                coords = [int(x) for x in parts]
                if len(coords) % 2 != 0 or len(coords) < 4:
                    print("Invalid coordinate count.")
                    continue
                seq = []
                for i in range(0, len(coords), 2):
                    seq.append((coords[i], coords[i+1]))
                for m in legal:
                    if m.sequence == seq:
                        return m
                print("Entered sequence is not a legal move.")
            except ValueError:
                print("Invalid input. Try again.")

if PYGAME_AVAILABLE:
    class PygameUI:
        SQUARE = 80
        WIDTH = HEIGHT = SQUARE * 8
        RADIUS = SQUARE // 2 - 8

        def __init__(self, board: Board):
            pygame.init()
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
            pygame.display.set_caption("Checkers - Click to play (Human vs AI)")
            self.clock = pygame.time.Clock()
            self.board = board
            self.selected = None
            self.legal_moves_cache = board.generate_legal_moves()
            self.move_callback = None

        def draw(self):
            colors = [(235, 235, 208), (119, 148, 85)]
            for r in range(8):
                for c in range(8):
                    color = colors[(r+c)%2]
                    pygame.draw.rect(self.screen, color, pygame.Rect(c*self.SQUARE, r*self.SQUARE, self.SQUARE, self.SQUARE))

            for r in range(8):
                for c in range(8):
                    cell = self.board.get_piece(r, c)
                    if cell is None or cell == (EMPTY, EMPTY):
                        continue
                    player, t = cell
                    center = (c*self.SQUARE + self.SQUARE//2, r*self.SQUARE + self.SQUARE//2)
                    if player == WHITE:
                        col = (255, 255, 255)
                        border = (0,0,0)
                    else:
                        col = (0,0,0)
                        border = (200,200,200)
                    pygame.draw.circle(self.screen, col, center, self.RADIUS)
                    pygame.draw.circle(self.screen, border, center, self.RADIUS, 3)
                    if t == KING:
                        pygame.draw.circle(self.screen, (200, 180, 0), center, 10)

            if self.selected:
                for m in self.legal_moves_cache:
                    if m.sequence[0] == self.selected:
                        for pos in m.sequence[1:]:
                            r, c = pos
                            center = (c*self.SQUARE + self.SQUARE//2, r*self.SQUARE + self.SQUARE//2)
                            pygame.draw.circle(self.screen, (0, 255, 0), center, 10)

            pygame.display.flip()

        def pixel_to_cell(self, pos):
            x, y = pos
            c = x // self.SQUARE
            r = y // self.SQUARE
            return r, c

        def run_once(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    r, c = self.pixel_to_cell(pos)
                    if not self.board.is_playable_square(r, c):
                        continue
                    piece = self.board.get_piece(r, c)
                    if piece != (EMPTY, EMPTY) and piece is not None and piece[0] == self.board.current_player:
                        self.selected = (r, c)
                    else:
                        if self.selected:
                            for m in self.legal_moves_cache:
                                if m.sequence[0] == self.selected and m.sequence[-1] == (r, c):
                                    self.selected = None
                                    return m
            self.draw()
            self.clock.tick(60)
            return None

        def update_board(self, board):
            self.board = board
            self.legal_moves_cache = board.generate_legal_moves()
            self.selected = None

def play_game(mode="human_vs_ai", ai_depth=6, use_alphabeta=True):

    board = Board()
    agent = MinimaxAgent(depth=ai_depth, use_alphabeta=use_alphabeta)
    agent2 = MinimaxAgent(depth=ai_depth, use_alphabeta=use_alphabeta)  # for black if ai_vs_ai
    if PYGAME_AVAILABLE and mode == "human_vs_ai":
        ui = PygameUI(board)
    else:
        ui = None

    print("Starting game. Mode:", mode)
    if ui:
        print("Pygame GUI mode enabled.")

    MAX_MOVES = 300
    while True:
        term, winner = board.is_terminal(max_moves=MAX_MOVES)
        if term:
            if winner == 0:
                print("Game ended in a draw.")
            elif winner == WHITE:
                print("WHITE wins!")
            else:
                print("BLACK wins!")
            board.print_board()
            break
        if ui:
            ui.update_board(board)
        if mode == "human_vs_ai":
            if board.current_player == WHITE:
                if ui:
                    move = None
                    while move is None:
                        move = ui.run_once()
                    board.apply_move(move)
                    print("Human (WHITE) played", move.sequence)
                else:
                    move = human_move_input(board)
                    board.apply_move(move)
            else:
                print("AI thinking...")
                move, stats = agent.select_move(board)
                if move is None:
                    print("AI has no move.")
                    continue
                board.apply_move(move)
                print(f"AI (BLACK) played {move.sequence} | nodes={stats.nodes} time={stats.time:.3f}s depth={stats.max_depth_reached}")
        elif mode == "ai_vs_ai":
            cur_agent = agent if board.current_player == WHITE else agent2
            move, stats = cur_agent.select_move(board)
            if move is None:
                print("No move for", "WHITE" if board.current_player==WHITE else "BLACK")
                continue
            board.apply_move(move)
            print(f"{'WHITE' if board.current_player==-1 else 'BLACK'} played {move.sequence} | nodes={stats.nodes} time={stats.time:.3f}s")
        elif mode == "human_vs_human":
            move = human_move_input(board)
            board.apply_move(move)
        else:
            raise ValueError("Unknown mode")

if __name__ == "__main__":
    print("Checkers AI - Options:")
    print("1) Human vs AI (Human = WHITE)")
    print("2) AI vs AI")
    print("3) Human vs Human (console)")
    choice = input("Choose mode (1/2/3): ").strip()
    if choice == '1':
        use_gui = False
        if PYGAME_AVAILABLE:
            g = input("Use Pygame GUI? (y/n) [y]: ").strip().lower()
            use_gui = (g != 'n')
        depth = input("AI search depth (default 6): ").strip()
        depth = int(depth) if depth.isdigit() else 6
        if use_gui:
            # run with GUI
            play_game(mode="human_vs_ai", ai_depth=depth, use_alphabeta=True)
        else:
            play_game(mode="human_vs_ai", ai_depth=depth, use_alphabeta=True)
    elif choice == '2':
        d = input("AI depth for both agents (default 6): ").strip()
        d = int(d) if d.isdigit() else 6
        play_game(mode="ai_vs_ai", ai_depth=d, use_alphabeta=True)
    elif choice == '3':
        play_game(mode="human_vs_human")
    else:
        print("Invalid choice. Exiting.")
