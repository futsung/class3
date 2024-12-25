import random
from models import Runestone
from stone_types import StoneType
import pygame
from typing import List, Tuple, Optional


class Board:
    def __init__(self, rows: int, cols: int, tile_size: int):
        """
        初始化遊戲盤面參數。
        """
        self.rows: int = rows
        self.cols: int = cols
        self.tile_size: int = tile_size
        self.tiles: List[List[Optional[Runestone]]] = TileManager.generate_board(rows, cols)
        self.drag_path: List[Tuple[int, int]] = []

    def draw(self, screen: pygame.Surface, images: dict) -> None:
        """
        繪製遊戲盤面，包括符石與黑色格線。
        """
        TileManager.draw_tiles(self.tiles, screen, images, self.tile_size)

    def handle_drag(self, start_pos: Tuple[int, int]) -> None:
        """
        處理拖曳的起始點。
        """
        TileManager.handle_drag(self.tiles, start_pos, self.drag_path, self.rows, self.cols, self.tile_size)

    def continue_drag(self, current_pos: Tuple[int, int]) -> None:
        """
        處理拖曳過程。
        """
        TileManager.continue_drag(self.tiles, current_pos, self.drag_path, self.rows, self.cols, self.tile_size)

    def end_drag(self) -> None:
        """
        清空拖曳路徑。
        """
        self.drag_path = []

    def check_matches(self) -> set:
        """
        檢查盤面上的三消匹配，並移除匹配的格子。
        """
        return TileManager.check_matches(self.tiles)

    def apply_gravity(self) -> None:
        """
        讓符石下落並補充新的符石。
        """
        TileManager.apply_gravity(self.tiles, self.rows, self.cols)


class TileManager:
    @staticmethod
    def generate_board(rows: int, cols: int) -> List[List[Optional[Runestone]]]:
        """
        生成一個隨機的遊戲盤面，保證沒有初始消除的情況。
        """
        while True:
            tiles: List[List[Optional[Runestone]]] = [
                [Runestone(random.choice(list(StoneType))) for _ in range(cols)] for _ in range(rows)
            ]
            if not TileManager.has_initial_matches(tiles):
                return tiles

    @staticmethod
    def has_initial_matches(tiles: List[List[Optional[Runestone]]]) -> bool:
        """
        檢查是否存在初始的三消匹配。
        """
        for row in range(len(tiles)):
            for col in range(len(tiles[0]) - 2):
                if tiles[row][col] and tiles[row][col + 1] and tiles[row][col + 2]:
                    if tiles[row][col].type == tiles[row][col + 1].type == tiles[row][col + 2].type:
                        return True
        for col in range(len(tiles[0])):
            for row in range(len(tiles) - 2):
                if tiles[row][col] and tiles[row + 1][col] and tiles[row + 2][col]:
                    if tiles[row][col].type == tiles[row + 1][col].type == tiles[row + 2][col].type:
                        return True
        return False

    @staticmethod
    def draw_tiles(
        tiles: List[List[Optional[Runestone]]],
        screen: pygame.Surface,
        images: dict,
        tile_size: int
    ) -> None:
        """
        繪製符石與棋盤格線。
        """
        for row in range(len(tiles)):
            for col in range(len(tiles[0])):
                tile = tiles[row][col]
                x, y = col * tile_size + 50, row * tile_size + 300
                if tile:
                    screen.blit(images[tile.type.value], (x, y))
                pygame.draw.rect(screen, (0, 0, 0), (x, y, tile_size, tile_size), 2)

    @staticmethod
    def handle_drag(
        tiles: List[List[Optional[Runestone]]],
        start_pos: Tuple[int, int],
        drag_path: List[Tuple[int, int]],
        rows: int,
        cols: int,
        tile_size: int
    ) -> None:
        """
        處理拖曳開始點。
        """
        start_x, start_y = start_pos
        start_col, start_row = (start_x - 50) // tile_size, (start_y - 300) // tile_size

        if 0 <= start_row < rows and 0 <= start_col < cols:
            drag_path.append((start_row, start_col))

    @staticmethod
    def continue_drag(
        tiles: List[List[Optional[Runestone]]],
        current_pos: Tuple[int, int],
        drag_path: List[Tuple[int, int]],
        rows: int,
        cols: int,
        tile_size: int
    ) -> None:
        """
        處理拖曳中的移動，交換兩個格子的內容。
        """
        current_x, current_y = current_pos
        current_col, current_row = (current_x - 50) // tile_size, (current_y - 300) // tile_size

        if 0 <= current_row < rows and 0 <= current_col < cols:
            if drag_path and drag_path[-1] != (current_row, current_col):
                last_row, last_col = drag_path[-1]
                tiles[last_row][last_col], tiles[current_row][current_col] = (
                    tiles[current_row][current_col],
                    tiles[last_row][last_col],
                )
                drag_path.append((current_row, current_col))

 
    @staticmethod
    def check_matches(tiles):
        """
        檢查盤面上的三消匹配，並移除匹配的格子。
        """
        matched = set()
        for row in range(len(tiles)):
            for col in range(len(tiles[0]) - 2):
                if (
                    tiles[row][col] and
                    tiles[row][col + 1] and
                    tiles[row][col + 2] and
                    tiles[row][col].type == tiles[row][col + 1].type == tiles[row][col + 2].type
                ):
                    matched.update({(row, col), (row, col + 1), (row, col + 2)})
        for col in range(len(tiles[0])):
            for row in range(len(tiles) - 2):
                if (
                    tiles[row][col] and
                    tiles[row + 1][col] and
                    tiles[row + 2][col] and
                    tiles[row][col].type == tiles[row + 1][col].type == tiles[row + 2][col].type
                ):
                    matched.update({(row, col), (row + 1, col), (row + 2, col)})

        for row, col in matched:
            tiles[row][col] = None

        return matched


    @staticmethod
    def apply_gravity(tiles: List[List[Optional[Runestone]]], rows: int, cols: int) -> None:
        """
        讓符石下落並生成新的符石填補空格。
        """
        for col in range(cols):
            for row in range(rows - 1, -1, -1):
                if not tiles[row][col]:
                    for upper_row in range(row - 1, -1, -1):
                        if tiles[upper_row][col]:
                            tiles[row][col], tiles[upper_row][col] = tiles[upper_row][col], None
                            break
                    if not tiles[row][col]:
                        tiles[row][col] = Runestone(random.choice(list(StoneType)))
