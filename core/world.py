"""Game systems (World, waves, score)."""

import math
from random import uniform
from typing import Dict

import pygame as pg

from core import config as C
from core.collisions import CollisionManager
from core.commands import PlayerCommand
from core.entities import (
    Asteroid,
    BlackHole,
    FreezePickup,
    PowerUp,
    ShieldPickup,
    Ship,
    SpecialAsteroid,
    TripleShootPowerUp,
    UFO,
)
from core.utils import Vec, rand_edge_pos

PlayerId = int


class World:
    """World state and game rules."""

    def __init__(self) -> None:
        self.ships: Dict[PlayerId, Ship] = {}

        self.bullets = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.ufos = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.freezes = pg.sprite.Group()
        self.shields = pg.sprite.Group()
        self.black_holes = pg.sprite.Group()
        self.triple_shot = pg.sprite.Group()

        self.all_sprites = pg.sprite.Group()

        self.scores: Dict[PlayerId, int] = {}
        self.lives: Dict[PlayerId, int] = {}

        self.wave = 0
        self.wave_cool = float(C.WAVE_DELAY)
        self.ufo_timer = float(C.UFO_SPAWN_EVERY)
        self.freeze_timer = 0.0
        self.bh_timer = float(C.BLACK_HOLE_SPAWN_EVERY)

        self.events: list[str] = []
        self._collision_mgr = CollisionManager()
        self.game_over = False

        self.spawn_player(C.LOCAL_PLAYER_ID)

    def begin_frame(self) -> None:
        self.events.clear()

    def reset(self) -> None:
        self.__init__()

    def spawn_player(self, player_id: PlayerId) -> None:
        pos = Vec(C.WIDTH / 2, C.HEIGHT / 2)
        ship = Ship(player_id, pos)
        ship.invuln = float(C.SAFE_SPAWN_TIME)

        self.ships[player_id] = ship
        self.scores[player_id] = 0
        self.lives[player_id] = C.START_LIVES
        self.all_sprites.add(ship)

    def get_ship(self, player_id: PlayerId) -> Ship | None:
        return self.ships.get(player_id)

    def start_wave(self) -> None:
        self.wave += 1
        count = C.WAVE_BASE_COUNT + self.wave
        ship_positions = [ship.pos for ship in self.ships.values()]

        for _ in range(count):
            pos = rand_edge_pos()
            while any((pos - sp).length() < C.AST_MIN_SPAWN_DIST for sp in ship_positions):
                pos = rand_edge_pos()

            ang = uniform(0, math.tau)
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX)
            vel = Vec(math.cos(ang), math.sin(ang)) * speed
            special = uniform(0, 1) < C.SPECIAL_AST_CHANCE

            self.spawn_asteroid(pos, vel, "L", special=special)

    def spawn_asteroid(self, pos: Vec, vel: Vec, size: str, special: bool = False) -> None:
        asteroid = SpecialAsteroid(pos, vel, size) if special else Asteroid(pos, vel, size)
        self.asteroids.add(asteroid)
        self.all_sprites.add(asteroid)

    def spawn_freeze_pickup(self, pos: Vec) -> None:
        pickup = FreezePickup(pos)
        self.freezes.add(pickup)
        self.all_sprites.add(pickup)

    def spawn_triple_shot_power_up(self, pos: Vec) -> None:
        power_up = TripleShootPowerUp(pos)
        self.triple_shot.add(power_up)
        self.all_sprites.add(power_up)

    def spawn_shield_pickup(self, pos: Vec) -> None:
        pickup = ShieldPickup(pos)
        self.shields.add(pickup)
        self.all_sprites.add(pickup)

    def spawn_powerup(self, pos: Vec, kind: str) -> None:
        pup = PowerUp(pos, kind)
        self.powerups.add(pup)
        self.all_sprites.add(pup)

    def spawn_ufo(self) -> None:
        small = uniform(0, 1) < 0.5
        pos = rand_edge_pos()
        target = self._get_nearest_ship_pos(pos)
        ufo = UFO(pos, small, target_pos=target)
        ufo.target_pos = target

        self.ufos.add(ufo)
        self.all_sprites.add(ufo)

    def update(
        self,
        dt: float,
        commands_by_player_id: Dict[PlayerId, PlayerCommand],
    ) -> None:
        self.begin_frame()

        if self.game_over:
            return

        self._apply_commands(dt, commands_by_player_id)
        self._apply_black_hole_gravity(dt)

        asteroid_dt = 0.0 if self.freeze_timer > 0.0 else dt
        for sprite in list(self.all_sprites):
            if sprite in self.asteroids:
                sprite.update(asteroid_dt)
            else:
                sprite.update(dt)

        self._update_ufos()
        self._update_timers(dt)
        self._update_bh_timer(dt)
        self._handle_collisions()
        self._maybe_start_next_wave(dt)

        for ship in self.ships.values():
            ship._update_triple_shot_timer(dt)

    def _apply_commands(
        self,
        dt: float,
        commands_by_player_id: Dict[PlayerId, PlayerCommand],
    ) -> None:
        for player_id, cmd in commands_by_player_id.items():
            ship = self.get_ship(player_id)
            if ship is None:
                continue

            if getattr(cmd, "hyperspace", False):
                if self.scores.get(player_id, 0) >= C.HYPERSPACE_COST:
                    self.scores[player_id] -= C.HYPERSPACE_COST
                    ship.hyperspace()

            spawned = ship.apply_command(cmd, dt, self.bullets)

            if spawned is None:
                continue

            if isinstance(spawned, list):
                for bullet in spawned:
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)
            else:
                self.bullets.add(spawned)
                self.all_sprites.add(spawned)

            self.events.append("player_shoot")

    def _apply_black_hole_gravity(self, dt: float) -> None:
        for bh in self.black_holes:
            for ship in self.ships.values():
                delta = bh.pos - ship.pos
                dist = max(delta.length(), C.BLACK_HOLE_GRAVITY_MIN_DIST)
                force = C.BLACK_HOLE_GRAVITY / (dist * dist)
                ship.vel += delta.normalize() * force * dt

    def _update_ufos(self) -> None:
        fallback = self._get_nearest_ship_pos(Vec(C.WIDTH / 2, C.HEIGHT / 2))
        for ufo in list(self.ufos):
            ufo.target_pos = self._get_nearest_ship_pos(ufo.pos) or fallback
            bullet = ufo.try_fire()
            if bullet is not None:
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)
                self.events.append("ufo_shoot")

    def _get_nearest_ship_pos(self, from_pos: Vec) -> Vec | None:
        nearest = None
        min_dist = float("inf")

        for ship in self.ships.values():
            dist = (ship.pos - from_pos).length()
            if dist < min_dist:
                min_dist = dist
                nearest = ship

        return nearest.pos if nearest else None

    def _update_timers(self, dt: float) -> None:
        if self.freeze_timer > 0.0:
            self.freeze_timer -= dt
            if self.freeze_timer < 0.0:
                self.freeze_timer = 0.0

        self.ufo_timer -= dt
        if self.ufo_timer <= 0.0:
            self.spawn_ufo()
            self.ufo_timer = float(C.UFO_SPAWN_EVERY)

    def _update_bh_timer(self, dt: float) -> None:
        self.bh_timer -= dt
        if self.bh_timer <= 0.0:
            self._spawn_black_hole()
            self.bh_timer = float(C.BLACK_HOLE_SPAWN_EVERY)

    def _spawn_black_hole(self) -> None:
        margin = C.BLACK_HOLE_RADIUS * 3
        ship_positions = [ship.pos for ship in self.ships.values()]

        pos = Vec(
            uniform(margin, C.WIDTH - margin),
            uniform(margin, C.HEIGHT - margin),
        )
        while any((pos - sp).length() < C.BLACK_HOLE_MIN_SPAWN_DIST for sp in ship_positions):
            pos = Vec(
                uniform(margin, C.WIDTH - margin),
                uniform(margin, C.HEIGHT - margin),
            )

        bh = BlackHole(pos)
        self.black_holes.add(bh)
        self.all_sprites.add(bh)

    def _maybe_start_next_wave(self, dt: float) -> None:
        if self.asteroids:
            return

        self.wave_cool -= dt
        if self.wave_cool <= 0.0:
            self.start_wave()
            self.wave_cool = float(C.WAVE_DELAY)

    def _handle_collisions(self) -> None:
        result = self._collision_mgr.resolve(
            self.ships,
            self.bullets,
            self.asteroids,
            self.ufos,
            self.powerups,
            self.black_holes,
            freezes=self.freezes,
            shields=self.shields,
            triple_shots=self.triple_shot,
        )

        self.events.extend(result.events)

        for player_id, delta in result.score_deltas.items():
            self.scores[player_id] = self.scores.get(player_id, 0) + delta

        for player_id, delta in result.lives_deltas.items():
            if player_id in self.lives:
                self.lives[player_id] += delta

        for pos, vel, size, special in result.asteroids_to_spawn:
            self.spawn_asteroid(pos, vel, size, special=special)

        for pos, kind in result.powerups_to_spawn:
            self.spawn_powerup(pos, kind)

        for pos in result.pickups_to_spawn:
            self.spawn_freeze_pickup(pos)

        for pos in result.triple_shoots_to_spawn:
            self.spawn_triple_shot_power_up(pos)

        for pos in result.shield_pickups_to_spawn:
            self.spawn_shield_pickup(pos)

        if result.freeze_activated:
            self.freeze_timer = float(C.FREEZE_DURATION)

        for player_id in result.shield_activated_for:
            ship = self.get_ship(player_id)
            if ship is not None:
                ship.shield_timer = float(C.SHIELD_DURATION)

        for player_id in result.ship_deaths:
            ship = self.get_ship(player_id)
            if ship is not None:
                self._ship_die(ship)

        if result.instant_kills:
            for player_id in result.instant_kills:
                self.lives[player_id] = 0
            self.events.append("ship_explosion")
            self.game_over = True

    def _ship_die(self, ship: Ship) -> None:
        pid = ship.player_id
        self.lives[pid] = self.lives.get(pid, 0) - 1
        self.events.append("ship_explosion")

        if self.lives[pid] <= 0:
            ship.kill()
            if ship in self.all_sprites:
                self.all_sprites.remove(ship)
            self.game_over = True
            return

        ship.pos.xy = (C.WIDTH / 2, C.HEIGHT / 2)
        ship.vel.xy = (0, 0)
        ship.angle = -90.0
        ship.invuln = float(C.SAFE_SPAWN_TIME)
        ship.shield_timer = 0.0