#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jogo: Batalha Naval (console)
Autor: Ericles Magno 
Rodar: python batalha_naval.py
"""

import random
import string

# Configurações
BOARD_SIZE = 10
ROW_LETTERS = list(string.ascii_uppercase[:BOARD_SIZE])  # ['A','B',...]
SHIP_SPECS = {
    "Porta-aviões": 5,
    "Couraçado": 4,
    "Cruzador": 3,
    "Submarino": 3,
    "Destroyer": 2
}

# Representações:
# 0 = água / não revelado
# 'S' = navio (apenas mostrado no tabuleiro do dono)
# 'X' = acerto
# 'O' = erro (agua acertada)

def create_empty_board():
    return [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

def print_boards(player_board, tracking_board):
    
    header = "   " + " ".join(f"{i:2}" for i in range(1, BOARD_SIZE+1))
    print("Seu tabuleiro:".ljust(34) + "Tabuleiro (rastreamento):")
    print(header.ljust(34) + header)
    for r in range(BOARD_SIZE):
        row_label = ROW_LETTERS[r]
        left = f"{row_label} " + " ".join(display_player_cell(player_board[r][c]) for c in range(BOARD_SIZE))
        right = f"{row_label} " + " ".join(display_tracking_cell(tracking_board[r][c]) for c in range(BOARD_SIZE))
        print(left.ljust(34) + right)
    print()

def display_player_cell(cell):
    if cell == 0:
        return ". "
    elif cell == 'S':
        return "S "
    elif cell == 'X':
        return "X "
    elif cell == 'O':
        return "O "
    else:
        return "? "

def display_tracking_cell(cell):
    if cell == 0:
        return ". "
    elif cell == 'X':
        return "X "
    elif cell == 'O':
        return "O "
    else:
        return ". "

def coords_from_input(inp):
    
    inp = inp.strip().upper()
    if len(inp) < 2:
        return None
    row_char = inp[0]
    col_part = inp[1:]
    if row_char not in ROW_LETTERS:
        return None
    try:
        col = int(col_part)
    except ValueError:
        return None
    if not (1 <= col <= BOARD_SIZE):
        return None
    row = ROW_LETTERS.index(row_char)
    col_idx = col - 1
    return (row, col_idx)

def can_place(board, row, col, size, orientation):
    dr, dc = (0, 1) if orientation == 'H' else (1, 0)
    for i in range(size):
        r = row + dr*i
        c = col + dc*i
        if r < 0 or r >= BOARD_SIZE or c < 0 or c >= BOARD_SIZE:
            return False
        if board[r][c] != 0:
            return False
    return True

def place_ship(board, row, col, size, orientation):
    dr, dc = (0, 1) if orientation == 'H' else (1, 0)
    coords = []
    for i in range(size):
        r = row + dr*i
        c = col + dc*i
        board[r][c] = 'S'
        coords.append((r,c))
    return coords

def random_place_all_ships(board, ship_specs):
    ship_positions = {}
    for name, size in ship_specs.items():
        placed = False
        attempts = 0
        while not placed and attempts < 1000:
            orientation = random.choice(['H','V'])
            if orientation == 'H':
                row = random.randrange(0, BOARD_SIZE)
                col = random.randrange(0, BOARD_SIZE - size + 1)
            else:
                row = random.randrange(0, BOARD_SIZE - size + 1)
                col = random.randrange(0, BOARD_SIZE)
            if can_place(board, row, col, size, orientation):
                coords = place_ship(board, row, col, size, orientation)
                ship_positions[name] = coords
                placed = True
            attempts += 1
        if not placed:
            raise RuntimeError("Não foi possível posicionar todos os navios (tente reiniciar).")
    return ship_positions

def manual_place_ships(board, ship_specs):
    ship_positions = {}
    print("Colocação manual: informe posição e orientação (H ou V). Exemplo: A1 H")
    print_boards(board, create_empty_board())
    for name, size in ship_specs.items():
        while True:
            entrada = input(f"Posicionamento para {name} ({size} células). Formato 'A1 H' ou 'random': ").strip()
            if entrada.lower() == 'random':
                
                orientation = random.choice(['H','V'])
                if orientation == 'H':
                    row = random.randrange(0, BOARD_SIZE)
                    col = random.randrange(0, BOARD_SIZE - size + 1)
                else:
                    row = random.randrange(0, BOARD_SIZE - size + 1)
                    col = random.randrange(0, BOARD_SIZE)
                if can_place(board, row, col, size, orientation):
                    coords = place_ship(board, row, col, size, orientation)
                    ship_positions[name] = coords
                    print(f"{name} posicionado aleatoriamente.")
                    print_boards(board, create_empty_board())
                    break
                else:
                    continue
            parts = entrada.upper().split()
            if len(parts) == 0:
                continue
            coord = parts[0]
            orientation = 'H'
            if len(parts) > 1:
                orientation = parts[1][0]
            if orientation not in ('H','V'):
                print("Orientação deve ser H ou V.")
                continue
            parsed = coords_from_input(coord)
            if not parsed:
                print("Coordenada inválida. Use ex: A1, J10.")
                continue
            row, col = parsed
            if not can_place(board, row, col, size, orientation):
                print("Não é possível colocar aí (ultrapassa ou sobrepõe). Tente outro local.")
                continue
            coords = place_ship(board, row, col, size, orientation)
            ship_positions[name] = coords
            print_boards(board, create_empty_board())
            break
    return ship_positions

def check_shot(board, ship_positions, row, col):
    cell = board[row][col]
    if cell == 'S':
        board[row][col] = 'X'
        
        sunk_ship = None
        for name, coords in ship_positions.items():
            if (row,col) in coords:
              
                if all(board[r][c] == 'X' for (r,c) in coords):
                    sunk_ship = name
                break
        return True, sunk_ship
    elif cell == 0:
        board[row][col] = 'O'
        return False, None
    else:
        
        return None, None

def all_ships_sunk(board, ship_positions):
    for coords in ship_positions.values():
        for (r,c) in coords:
            if board[r][c] != 'X':
                return False
    return True

def computer_choose_shot(tracking_board):
    
    choices = [(r,c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if tracking_board[r][c] == 0]
    return random.choice(choices) if choices else None

def input_player_shot(tracking_board):
    while True:
        s = input("Digite posição para atirar (ex: B7): ").strip()
        parsed = coords_from_input(s)
        if not parsed:
            print("Entrada inválida. Tente novamente.")
            continue
        r,c = parsed
        if tracking_board[r][c] != 0:
            print("Você já atirou nessa posição. Escolha outra.")
            continue
        return r,c

def main():
    print("=== BATALHA NAVAL ===")
   
    player_board = create_empty_board()
    computer_board = create_empty_board()
    player_tracking = create_empty_board()  
    computer_tracking = create_empty_board()  

    
    escolha = input("Deseja posicionar seus navios manualmente? (s/N): ").strip().lower()
    if escolha == 's':
        player_ships = manual_place_ships(player_board, SHIP_SPECS)
    else:
        player_ships = random_place_all_ships(player_board, SHIP_SPECS)

    computer_ships = random_place_all_ships(computer_board, SHIP_SPECS)
    print("Navios posicionados. Começando o jogo!\n")

    
    player_turn = True
    while True:
        print_boards(player_board, player_tracking)

        if player_turn:
            print("--- Seu turno ---")
            r,c = input_player_shot(player_tracking)
            result, sunk = check_shot(computer_board, computer_ships, r, c)
            if result is None:
                print("Essa posição já foi atingida. Perdeu o turno (não deveria acontecer).")
            elif result:
                player_tracking[r][c] = 'X'
                print(f"ACERTOU! ({ROW_LETTERS[r]}{c+1})")
                if sunk:
                    print(f"Você afundou o navio inimigo: {sunk}!")
                if all_ships_sunk(computer_board, computer_ships):
                    print("Parabéns — você venceu! Todos os navios inimigos foram afundados.")
                    break
                
            else:
                player_tracking[r][c] = 'O'
                print(f"ÁGUA. ({ROW_LETTERS[r]}{c+1})")
                player_turn = False
        else:
            print("--- Turno do computador ---")
            shot = computer_choose_shot(computer_tracking)
            if shot is None:
                print("Sem posições restantes. Empate estranho.")
                break
            r,c = shot
            print(f"Computador atira em {ROW_LETTERS[r]}{c+1}...")
            result, sunk = check_shot(player_board, player_ships, r, c)
            if result is None:
                
                computer_tracking[r][c] = 'O'
                print("Computador atirou onde já tinha atirado. Pulando.")
                player_turn = True
                continue
            elif result:
                computer_tracking[r][c] = 'X'
                print("Computador ACERTOU!")
                if sunk:
                    print(f"O computador afundou seu navio: {sunk}!")
                if all_ships_sunk(player_board, player_ships):
                    print("O computador venceu. Seus navios foram todos afundados.")
                    break
                
                player_turn = True
            else:
                computer_tracking[r][c] = 'O'
                print("Computador errou (água).")
                player_turn = True

    print("Fim de jogo. Obrigado por jogar!")

if __name__ == "__main__":
    main()
