"""Renderização do lado cliente (pygame)."""

import math

import pygame as pg

from core import config as C
from core.entities import Asteroid, BlackHole, Bullet, FreezePickup, Ship, UFO
from core.entities import Asteroid, Bullet, FreezePickup, Ship, UFO, TripleShootPowerUp
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
            FreezePickup: self._draw_freeze_pickup,  # coletável de congelamento
            BlackHole: self._draw_black_hole,
            TripleShootPowerUp: self._draw_triple_shot_power_up,  # coletável de tiro triplo
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
        triple_shot_timer: float = 0.0,
    ) -> None:
        """Desenha o HUD com pontuação, vidas, wave e (se ativo) timer de freeze."""
        if state != SceneState.PLAY:
            return

        text = f"SCORE {score:06d}   LIVES {lives}   WAVE {wave}"
        label = self.font.render(text, True, self.config.WHITE)
        self.screen.blit(label, (10, 10))

        # exibe o contador de congelamento enquanto estiver ativo
        if freeze_timer > 0.0:
            freeze_text = f"FREEZE {freeze_timer:.1f}s"
            freeze_label = self.font.render(freeze_text, True, C.FREEZE_COLOR)
            self.screen.blit(freeze_label, (10, 36))
        
        # Contador de tiro triplo
        if triple_shot_timer > 0.0:
            triple_text = f"TRIPLE SHOT {triple_shot_timer:.1f}s"
            triple_label = self.font.render(triple_text, True, C.TRIPLE_SHOT_COLOR)
            self.screen.blit(triple_label, (10, 62))

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
            self.config.WIDTH // 2 - 170,
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

    def _draw_ufo(self, ufo: UFO) -> None:
        width = ufo.r * 2
        height = ufo.r

        body = pg.Rect(0, 0, width, height)
        body.center = (int(ufo.pos.x), int(ufo.pos.y))
        pg.draw.ellipse(self.screen, self.config.WHITE, body, width=1)

        cup = pg.Rect(0, 0, int(width * 0.5), int(height * 0.7))
        cup.center = (int(ufo.pos.x), int(ufo.pos.y - height * 0.3))
        pg.draw.ellipse(self.screen, self.config.WHITE, cup, width=1)

    def _draw_freeze_pickup(self, pickup: FreezePickup) -> None:
        """Desenha um cristal de gelo (floco de neve simplificado) na tela.

        O floco é formado por 6 linhas saindo do centro em ângulos de 60°,
        com duas hastes menores cruzadas em cada extremidade.
        """
        cx, cy = int(pickup.pos.x), int(pickup.pos.y)
        r = pickup.r
        cor = C.FREEZE_COLOR

        # 6 eixos do floco (0°, 60°, 120°, ... 300°)
        for i in range(6):
            ang = math.radians(i * 60)
            ex = cx + int(r * math.cos(ang))
            ey = cy + int(r * math.sin(ang))
            # linha principal do eixo
            pg.draw.line(self.screen, cor, (cx, cy), (ex, ey), 1)

            # hastes laterais no meio do eixo
            mid_x = cx + int((r * 0.5) * math.cos(ang))
            mid_y = cy + int((r * 0.5) * math.sin(ang))
            for delta in (-60, 60):
                side_ang = math.radians(i * 60 + delta)
                sx = mid_x + int((r * 0.3) * math.cos(side_ang))
                sy = mid_y + int((r * 0.3) * math.sin(side_ang))
                pg.draw.line(self.screen, cor, (mid_x, mid_y), (sx, sy), 1)

    def _draw_black_hole(self, bh: BlackHole) -> None:
        pulse = math.sin(bh.age * self.config.BLACK_HOLE_PULSE_FREQ) * self.config.BLACK_HOLE_PULSE_AMP + 1.0
        center = (int(bh.pos.x), int(bh.pos.y))

        # Outer gravitational aura rings
        outer_r = int(bh.r * self.config.BLACK_HOLE_AURA_OUTER * pulse)
        mid_r = int(bh.r * self.config.BLACK_HOLE_AURA_MID * pulse)
        pg.draw.circle(self.screen, self.config.PURPLE_DARK, center, outer_r, width=1)
        pg.draw.circle(self.screen, self.config.PURPLE, center, mid_r, width=1)

        # Solid black core
        pg.draw.circle(self.screen, self.config.BLACK, center, bh.r)

        # Bright event-horizon border
        pg.draw.circle(self.screen, self.config.PURPLE_LIGHT, center, bh.r, width=2)
    def _draw_triple_shot_power_up(self, power_up: TripleShootPowerUp) -> None:
        """Desenha um ícone de tiro triplo com setas estilizadas e brilho."""
        cx, cy = int(power_up.pos.x), int(power_up.pos.y)
        r = power_up.r
        cor_principal = (255, 215, 0)  # Dourado
        cor_brilho = (255, 255, 150)    # Amarelo claro
        

        angulos = [-30, 0, 30]
        
        for ang_deg in angulos:
            rad = math.radians(ang_deg - 90)
            
            ponta = (
                cx + int(r * math.cos(rad)),
                cy + int(r * math.sin(rad))
            )
            
            asa_esq = (
                cx + int(r * 0.5 * math.cos(rad + 2.5)),
                cy + int(r * 0.5 * math.sin(rad + 2.5))
            )
            asa_dir = (
                cx + int(r * 0.5 * math.cos(rad - 2.5)),
                cy + int(r * 0.5 * math.sin(rad - 2.5))
            )
            
            pg.draw.polygon(self.screen, cor_principal, [ponta, asa_esq, asa_dir])
            
            pg.draw.circle(self.screen, cor_brilho, ponta, 2)
