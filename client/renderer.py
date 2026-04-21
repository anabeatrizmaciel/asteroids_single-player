"""Renderização do lado cliente (pygame)."""

import math

import pygame as pg

from core import config as C
from core.entities import Asteroid, Bullet, FreezePickup, ShieldPickup, Ship, UFO
from core.scene import SceneState


class Renderer:
    """Draws scenes and entities without coupling game rules to Game."""

    def __init__(
        self,
        screen: pg.Surface,
        config: object = C,
        fonts: dict[str, pg.font.Font] | None = None,
    ) -> None:
        self.screen = screen
        self.config = config
        safe_fonts = fonts or {}
        self.font = safe_fonts["font"]
        self.big = safe_fonts["big"]

        self._draw_dispatch: dict[type, callable] = {
            Bullet: self._draw_bullet,
            Asteroid: self._draw_asteroid,
            Ship: self._draw_ship,
            UFO: self._draw_ufo,
            FreezePickup: self._draw_freeze_pickup,
            ShieldPickup: self._draw_shield_pickup,
        }

    def clear(self) -> None:
        self.screen.fill(self.config.BLACK)

    def draw_world(self, world: object) -> None:
        sprites = getattr(world, "all_sprites", [])
        for sprite in sprites:
            drawer = self._draw_dispatch.get(type(sprite))
            if drawer is not None:
                drawer(sprite)

    def draw_hud(
        self,
        score: int,
        lives: int,
        wave: int,
        state: SceneState,
        freeze_timer: float = 0.0,
        shield_timer: float = 0.0,
    ) -> None:
        """Desenha o HUD com pontuação, vidas, wave e timers de efeitos."""
        if state != SceneState.PLAY:
            return

        text = f"SCORE {score:06d} LIVES {lives} WAVE {wave}"
        label = self.font.render(text, True, self.config.WHITE)
        self.screen.blit(label, (10, 10))

        if freeze_timer > 0.0:
            freeze_text = f"FREEZE {freeze_timer:.1f}s"
            freeze_label = self.font.render(freeze_text, True, C.FREEZE_COLOR)
            self.screen.blit(freeze_label, (10, 36))

        if shield_timer > 0.0:
            shield_text = f"SHIELD {shield_timer:.1f}s"
            shield_label = self.font.render(shield_text, True, C.SHIELD_COLOR)
            self.screen.blit(shield_label, (10, 62))

    def draw_menu(self) -> None:
        self._draw_text(
            self.big,
            "ASTEROIDS",
            self.config.WIDTH // 2 - 170,
            200,
        )
        self._draw_text(
            self.font,
            "Press any key",
            self.config.WIDTH // 2 - 100,
            350,
        )

    def draw_game_over(self) -> None:
        self._draw_text(
            self.big,
            "GAME OVER",
            self.config.WIDTH // 2 - 170,
            260,
        )
        self._draw_text(
            self.font,
            "Press any key",
            self.config.WIDTH // 2 - 170,
            340,
        )

    def _draw_text(
        self,
        font: pg.font.Font,
        text: str,
        x: int,
        y: int,
    ) -> None:
        label = font.render(text, True, self.config.WHITE)
        self.screen.blit(label, (x, y))

    def _draw_bullet(self, bullet: Bullet) -> None:
        center = (int(bullet.pos.x), int(bullet.pos.y))
        pg.draw.circle(
            self.screen,
            self.config.WHITE,
            center,
            bullet.r,
            width=1,
        )

    def _draw_asteroid(self, asteroid: Asteroid) -> None:
        points = []
        for point in asteroid.poly:
            px = int(asteroid.pos.x + point.x)
            py = int(asteroid.pos.y + point.y)
            points.append((px, py))
        pg.draw.polygon(self.screen, self.config.WHITE, points, width=1)

    def _draw_ship(self, ship: Ship) -> None:
        p1, p2, p3 = ship.ship_points()
        points = [
            (int(p1.x), int(p1.y)),
            (int(p2.x), int(p2.y)),
            (int(p3.x), int(p3.y)),
        ]
        pg.draw.polygon(self.screen, self.config.WHITE, points, width=1)

        if ship.invuln > 0.0 and int(ship.invuln * 10) % 2 == 0:
            center = (int(ship.pos.x), int(ship.pos.y))
            pg.draw.circle(
                self.screen,
                self.config.WHITE,
                center,
                ship.r + 6,
                width=1,
            )

        if ship.shield_timer > 0.0 and int(ship.shield_timer * 10) % 2 == 0:
            center = (int(ship.pos.x), int(ship.pos.y))
            pg.draw.circle(
                self.screen,
                C.SHIELD_COLOR,
                center,
                ship.r + 10,
                width=2,
            )

    def _draw_ufo(self, ufo: UFO) -> None:
        width = ufo.r * 2
        height = ufo.r

        body = pg.Rect(0, 0, width, height)
        body.center = (int(ufo.pos.x), int(ufo.pos.y))
        pg.draw.ellipse(self.screen, self.config.WHITE, body, width=1)

        cup = pg.Rect(0, 0, int(width * 0.5), int(height * 0.7))
        cup.center = (int(ufo.pos.x), int(ufo.pos.y - height * 0.3))
        pg.draw.ellipse(self.screen, self.config.WHITE, cup, width=1)

    def _draw_shield_pickup(self, pickup: ShieldPickup) -> None:
        """Desenha um coletável de escudo como anéis concêntricos."""
        center = (int(pickup.pos.x), int(pickup.pos.y))
        pg.draw.circle(self.screen, C.SHIELD_COLOR, center, pickup.r, width=2)
        pg.draw.circle(self.screen, C.SHIELD_COLOR, center, max(4, pickup.r // 2), width=1)

    def _draw_freeze_pickup(self, pickup: FreezePickup) -> None:
        """Desenha um cristal de gelo (floco de neve simplificado) na tela."""
        cx, cy = int(pickup.pos.x), int(pickup.pos.y)
        r = pickup.r
        cor = C.FREEZE_COLOR

        for i in range(6):
            ang = math.radians(i * 60)
            ex = cx + int(r * math.cos(ang))
            ey = cy + int(r * math.sin(ang))

            pg.draw.line(self.screen, cor, (cx, cy), (ex, ey), 1)

            mid_x = cx + int((r * 0.5) * math.cos(ang))
            mid_y = cy + int((r * 0.5) * math.sin(ang))

            for delta in (-60, 60):
                side_ang = math.radians(i * 60 + delta)
                sx = mid_x + int((r * 0.3) * math.cos(side_ang))
                sy = mid_y + int((r * 0.3) * math.sin(side_ang))
                pg.draw.line(self.screen, cor, (mid_x, mid_y), (sx, sy), 1)