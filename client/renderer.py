"""Client-side rendering."""

import math

import pygame as pg

from core import config as C
from core.entities import (
    Asteroid,
    BlackHole,
    Bullet,
    FreezePickup,
    PowerUp,
    ShieldPickup,
    Ship,
    SpecialAsteroid,
    TripleShootPowerUp,
    UFO,
)
from core.scene import SceneState


class Renderer:
    def __init__(
        self,
        screen: pg.Surface,
        config: object = C,
        fonts: dict[str, pg.font.Font] | None = None,
    ) -> None:
        self.screen = screen
        self.config = config

        safe_fonts = fonts or {}
        self.font = safe_fonts.get(
            "font",
            pg.font.SysFont(getattr(self.config, "FONT_NAME", "consolas"), getattr(self.config, "FONT_SIZE_SMALL", 22)),
        )
        self.big = safe_fonts.get(
            "big",
            pg.font.SysFont(getattr(self.config, "FONT_NAME", "consolas"), getattr(self.config, "FONT_SIZE_LARGE", 64)),
        )

        self._draw_dispatch: dict[type, callable] = {
            Bullet: self._draw_bullet,
            SpecialAsteroid: self._draw_special_asteroid,
            Asteroid: self._draw_asteroid,
            PowerUp: self._draw_powerup,
            Ship: self._draw_ship,
            UFO: self._draw_ufo,
            FreezePickup: self._draw_freeze_pickup,
            ShieldPickup: self._draw_shield_pickup,
            BlackHole: self._draw_black_hole,
            TripleShootPowerUp: self._draw_triple_shot_power_up,
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
        triple_shot_timer: float = 0.0,
    ) -> None:
        if state != SceneState.PLAY:
            return

        header = f"SCORE {score:06d}  LIVES {lives}  WAVE {wave}"
        label = self.font.render(header, True, self.config.WHITE)
        self.screen.blit(label, (10, 10))

        effect_y = 38
        effect_gap = 24

        if freeze_timer > 0.0:
            freeze_label = self.font.render(
                f"FREEZE {freeze_timer:.1f}s",
                True,
                C.FREEZE_COLOR,
            )
            self.screen.blit(freeze_label, (10, effect_y))
            effect_y += effect_gap

        if shield_timer > 0.0:
            shield_label = self.font.render(
                f"SHIELD {shield_timer:.1f}s",
                True,
                C.SHIELD_COLOR,
            )
            self.screen.blit(shield_label, (10, effect_y))
            effect_y += effect_gap

        if triple_shot_timer > 0.0:
            triple_label = self.font.render(
                f"TRIPLE SHOT {triple_shot_timer:.1f}s",
                True,
                C.TRIPLE_SHOT_COLOR,
            )
            self.screen.blit(triple_label, (10, effect_y))

    def draw_menu(self) -> None:
        title = self.big.render("ASTEROIDS", True, self.config.WHITE)
        prompt = self.font.render("Press any key", True, self.config.WHITE)

        self.screen.blit(
            title,
            (
                self.config.WIDTH // 2 - title.get_width() // 2,
                200,
            ),
        )
        self.screen.blit(
            prompt,
            (
                self.config.WIDTH // 2 - prompt.get_width() // 2,
                350,
            ),
        )

    def draw_game_over(self) -> None:
        title = self.big.render("GAME OVER", True, self.config.WHITE)
        prompt = self.font.render("Press any key", True, self.config.WHITE)

        self.screen.blit(
            title,
            (
                self.config.WIDTH // 2 - title.get_width() // 2,
                260,
            ),
        )
        self.screen.blit(
            prompt,
            (
                self.config.WIDTH // 2 - prompt.get_width() // 2,
                340,
            ),
        )

    def _draw_bullet(self, bullet: Bullet) -> None:
        center = (int(bullet.pos.x), int(bullet.pos.y))
        pg.draw.circle(self.screen, self.config.WHITE, center, bullet.r, width=1)

    def _draw_asteroid(self, asteroid: Asteroid) -> None:
        points = [
            (int(asteroid.pos.x + point.x), int(asteroid.pos.y + point.y))
            for point in asteroid.poly
        ]
        pg.draw.polygon(self.screen, self.config.WHITE, points, width=1)

    def _draw_special_asteroid(self, asteroid: SpecialAsteroid) -> None:
        points = [
            (int(asteroid.pos.x + point.x), int(asteroid.pos.y + point.y))
            for point in asteroid.poly
        ]
        pg.draw.polygon(self.screen, self.config.GOLD, points, width=1)
        pg.draw.circle(
            self.screen,
            self.config.GOLD,
            (int(asteroid.pos.x), int(asteroid.pos.y)),
            2,
        )

    def _draw_powerup(self, pup: PowerUp) -> None:
        if pup.ttl <= self.config.POWERUP_BLINK_THRESHOLD:
            blink_phase = int(pup.phase * self.config.POWERUP_BLINK_HZ * 2.0) % 2
            if blink_phase != 0:
                return

        cx = int(pup.pos.x)
        cy = int(pup.pos.y)
        r = pup.r

        points = [
            (cx, cy - r),
            (cx + r, cy),
            (cx, cy + r),
            (cx - r, cy),
        ]
        pg.draw.polygon(self.screen, self.config.GOLD, points, width=1)

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
            pg.draw.circle(self.screen, self.config.WHITE, center, ship.r + 6, width=1)

        if ship.shield_timer > 0.0 and int(ship.shield_timer * 10) % 2 == 0:
            center = (int(ship.pos.x), int(ship.pos.y))
            pg.draw.circle(self.screen, C.SHIELD_COLOR, center, ship.r + 10, width=2)

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
        center = (int(pickup.pos.x), int(pickup.pos.y))
        pg.draw.circle(self.screen, C.SHIELD_COLOR, center, pickup.r, width=2)
        pg.draw.circle(
            self.screen,
            C.SHIELD_COLOR,
            center,
            max(4, pickup.r // 2),
            width=1,
        )

    def _draw_freeze_pickup(self, pickup: FreezePickup) -> None:
        cx = int(pickup.pos.x)
        cy = int(pickup.pos.y)
        r = pickup.r
        color = C.FREEZE_COLOR

        for i in range(6):
            ang = math.radians(i * 60)
            ex = cx + int(r * math.cos(ang))
            ey = cy + int(r * math.sin(ang))
            pg.draw.line(self.screen, color, (cx, cy), (ex, ey), 1)

            mid_x = cx + int((r * 0.5) * math.cos(ang))
            mid_y = cy + int((r * 0.5) * math.sin(ang))

            for delta in (-60, 60):
                side_ang = math.radians(i * 60 + delta)
                sx = mid_x + int((r * 0.3) * math.cos(side_ang))
                sy = mid_y + int((r * 0.3) * math.sin(side_ang))
                pg.draw.line(self.screen, color, (mid_x, mid_y), (sx, sy), 1)

    def _draw_black_hole(self, bh: BlackHole) -> None:
        pulse = (
            math.sin(bh.age * self.config.BLACK_HOLE_PULSE_FREQ)
            * self.config.BLACK_HOLE_PULSE_AMP
            + 1.0
        )
        center = (int(bh.pos.x), int(bh.pos.y))

        outer_r = int(bh.r * self.config.BLACK_HOLE_AURA_OUTER * pulse)
        mid_r = int(bh.r * self.config.BLACK_HOLE_AURA_MID * pulse)

        pg.draw.circle(self.screen, self.config.PURPLE_DARK, center, outer_r, width=1)
        pg.draw.circle(self.screen, self.config.PURPLE, center, mid_r, width=1)
        pg.draw.circle(self.screen, self.config.BLACK, center, bh.r)
        pg.draw.circle(self.screen, self.config.PURPLE_LIGHT, center, bh.r, width=2)

    def _draw_triple_shot_power_up(self, power_up: TripleShootPowerUp) -> None:
        cx = int(power_up.pos.x)
        cy = int(power_up.pos.y)
        r = power_up.r

        main_color = C.TRIPLE_SHOT_COLOR
        glow_color = self.config.WHITE

        angles = [-30, 0, 30]
        for ang_deg in angles:
            rad = math.radians(ang_deg - 90)

            tip = (
                cx + int(r * math.cos(rad)),
                cy + int(r * math.sin(rad)),
            )
            wing_left = (
                cx + int(r * 0.5 * math.cos(rad + 2.5)),
                cy + int(r * 0.5 * math.sin(rad + 2.5)),
            )
            wing_right = (
                cx + int(r * 0.5 * math.cos(rad - 2.5)),
                cy + int(r * 0.5 * math.sin(rad - 2.5)),
            )

            pg.draw.polygon(self.screen, main_color, [tip, wing_left, wing_right])
            pg.draw.circle(self.screen, glow_color, tip, 2)