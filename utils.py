import pygame
from typing import Dict


class ImageManager:
    @staticmethod
    def load_images(image_path: Dict[str, str], tile_size: int, screen_width: int, screen_height: int) -> Dict[str, pygame.Surface]:
        """
        加載並縮放所有遊戲所需的圖片。
        :param image_path: 字典，包含圖片名稱與對應路徑
        :param tile_size: 符石的圖片大小
        :param screen_width: 螢幕寬度，用於背景圖片的縮放
        :param screen_height: 螢幕高度，用於背景圖片的縮放
        :return: 字典，包含已縮放的圖片資源
        """
        images: Dict[str, pygame.Surface] = {}
        for key, path in image_path.items():
            if key in ["background", "victory"]:
                images[key] = pygame.transform.scale(
                    pygame.image.load(path), (screen_width, screen_height if key == "victory" else 300)
                )
            elif key == "start_background":
                images[key] = pygame.transform.scale(
                    pygame.image.load(path), (screen_width, screen_height)
                )
            else:
                images[key] = pygame.transform.scale(
                    pygame.image.load(path), (tile_size, tile_size)
                )
        return images


class HealthBar:
    @staticmethod
    def draw(screen: pygame.Surface, health: int, max_health: int, x: int, y: int, width: int, height: int) -> None:
        """
        繪製敵人的健康條（血條）。
        :param screen: Pygame 畫布
        :param health: 當前健康值
        :param max_health: 最大健康值
        :param x: 血條的 X 座標
        :param y: 血條的 Y 座標
        :param width: 血條的寬度
        :param height: 血條的高度
        """
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height))
        pygame.draw.rect(screen, (255, 0, 0), (x, y, width * (health / max_health), height))
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"{health}/{max_health}", True, (0, 0, 0))
        text_rect = health_text.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(health_text, text_rect)


class StatusBar:
    @staticmethod
    def draw(screen: pygame.Surface, traffic_tickets: int, combo: int, level: int) -> None:
        """
        繪製遊戲狀態欄，包括罰單數、連擊數和當前關卡。
        :param screen: Pygame 畫布
        :param traffic_tickets: 累計交通罰單數
        :param combo: 當前的連擊數
        :param level: 當前關卡
        """
        font = pygame.font.Font(None, 36)
        texts = [
            f"Traffic Tickets: {traffic_tickets}",
            f"Combo: {combo}",
            f"Level: {level}"
        ]
        for i, text in enumerate(texts):
            screen.blit(font.render(text, True, (255, 255, 255)), (20, 20 + i * 60))
