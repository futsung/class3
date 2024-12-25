import pygame
import os
from board import Board
from utils import ImageManager, HealthBar, StatusBar

class GameManager:
    def __init__(self):
        """
        初始化遊戲的相關參數與模組。
        """
        self.screen_width = 720
        self.screen_height = 800
        self.rows = 5
        self.cols = 6
        self.tile_size = 100
        self.fps = 60

        # 初始化 Pygame
        pygame.init()
        pygame.mixer.init()

        # 建立畫布
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("行人地獄")
        self.clock = pygame.time.Clock()

        # 加載圖片與音效
        self.image_paths = self._get_image_paths()
        self.images = ImageManager.load_images(
            self.image_paths, self.tile_size, self.screen_width, self.screen_height
        )
        self.match_sound = self._load_sound("music/caraccident.mp3")
        self._initialize_music("music/bgm.mp3")

        # 遊戲核心模組
        self.board = Board(self.rows, self.cols, self.tile_size)
        self.level = 1
        self.traffic_tickets = 0
        self.combo = 0

        # 敵人參數
        self.enemies = ["man", "old_woman", "kid_and_dog"]
        self.enemy_health = [150, 250, 500]
        self.enemy_sizes = [(150, 200), (250, 220), (150, 200)]
        self.current_enemy_index = 0
        self.max_health = self.enemy_health[self.current_enemy_index]
        self.health = self.max_health

        # 控制參數
        self.running = True
        self.dragging = False
        self.start_pos = None

    def _get_image_paths(self):
        """
        設置圖片資源路徑。
        """
        base_dir = os.path.dirname(__file__)
        return {
            "car": os.path.join(base_dir, "Image", "car.png"),
            "scooter": os.path.join(base_dir, "Image", "scooter.png"),
            "bus": os.path.join(base_dir, "Image", "bus.png"),
            "train": os.path.join(base_dir, "Image", "train.png"),
            "bike": os.path.join(base_dir, "Image", "bike.jpg"),
            "background": os.path.join(base_dir, "Image", "background.jpg"),
            "man": os.path.join(base_dir, "Image", "man.png"),
            "old_woman": os.path.join(base_dir, "Image", "old_woman.png"),
            "kid_and_dog": os.path.join(base_dir, "Image", "kid_and_dog.png"),
            "victory": os.path.join(base_dir, "Image", "victory.jpg"),
            "start_background": os.path.join(base_dir, "Image", "alivinghell.jpg")
        }

    def _initialize_music(self, music_path):
        """
        初始化背景音樂。
        """
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        else:
            print(f"Error: Music file not found at {music_path}")

    def _load_sound(self, sound_path):
        """
        加載音效檔案。
        """
        if os.path.exists(sound_path):
            return pygame.mixer.Sound(sound_path)
        else:
            print(f"Error: Sound file not found at {sound_path}")
            exit()

    def show_start_screen(self):
        """
        顯示起始畫面。
        """
        start_background = pygame.image.load(self.image_paths["start_background"])
        start_background = pygame.transform.scale(start_background, (self.screen_width, self.screen_height))
        UIManager.show_start_screen(self.screen, start_background)

    def show_summary(self):
        """
        顯示結算畫面。
        """
        UIManager.show_summary(self.screen, self.traffic_tickets, self.images)

    def main_loop(self):
        """
        遊戲主循環。
        """
        self.show_start_screen()

        while self.running:
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.images["background"], (0, 0))  # 背景圖

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.start_pos = pygame.mouse.get_pos()
                    self.dragging = True
                    self.board.handle_drag(self.start_pos)

                if event.type == pygame.MOUSEMOTION and self.dragging:
                    self.board.continue_drag(pygame.mouse.get_pos())

                if event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False
                    self.board.end_drag()
                    matches = self.board.check_matches()
                    if matches:
                        self.match_sound.play()
                        self.combo += 1
                        damage = len(matches) * 10
                        self.health -= damage
                        self.traffic_tickets += damage
                        if self.health <= 0:
                            self.level += 1
                            if self.level > len(self.enemies):
                                self.show_summary()
                                self.running = False
                            else:
                                self.current_enemy_index = self.level - 1
                                self.health = self.enemy_health[self.current_enemy_index]
                                self.max_health = self.health
                        self.board.apply_gravity()

            # 繪製敵人
            enemy_x = self.screen_width // 2 - self.enemy_sizes[self.current_enemy_index][0] // 2
            enemy_y = 31
            enemy_image = pygame.transform.scale(
                self.images[self.enemies[self.current_enemy_index]],
                self.enemy_sizes[self.current_enemy_index]
            )
            self.screen.blit(enemy_image, (enemy_x, enemy_y))
            HealthBar.draw(
                self.screen, self.health, self.max_health, enemy_x, enemy_y - 20,
                self.enemy_sizes[self.current_enemy_index][0], 10
            )

            # 繪製遊戲盤面與狀態欄
            self.board.draw(self.screen, self.images)
            StatusBar.draw(self.screen, self.traffic_tickets, self.combo, self.level)

            # 更新畫面
            pygame.display.flip()
            self.clock.tick(self.fps)

        pygame.quit()


class UIManager:
    @staticmethod
    def show_start_screen(screen, background_image):
        font_button = pygame.font.Font(None, 48)
        button_text = font_button.render("START", True, (0, 0, 0))
        button_rect = pygame.Rect(260, 400, 200, 80)

        screen.blit(background_image, (0, 0))
        pygame.draw.rect(screen, (255, 255, 255), button_rect)
        screen.blit(
            button_text,
            (button_rect.centerx - button_text.get_width() // 2, button_rect.centery - button_text.get_height() // 2)
        )
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                    waiting = False

    @staticmethod
    def show_summary(screen, traffic_tickets, images):
        screen.fill((0, 0, 0))
        screen.blit(images["victory"], (0, 0))

        font = pygame.font.Font(None, 72)
        text_number = font.render(f"{traffic_tickets}", True, (255, 255, 255))
        number_rect = text_number.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text_number, number_rect)
        pygame.display.flip()
        pygame.time.wait(5000)


if __name__ == "__main__":
    game = GameManager()
    game.main_loop()