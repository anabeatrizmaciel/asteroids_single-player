"""Collision detection and resolution."""

from dataclasses import dataclass, field
from random import random, uniform

import pygame as pg

from core import config as C
from core.entities import (
    Asteroid,
    Bullet,
    FreezePickup,
    ShieldPickup,
    Ship,
    UFO,
    UFO_BULLET_OWNER,
    PlayerId,
)
from core.utils import Vec, rand_unit_vec


@dataclass
class CollisionResult:
    """Aggregated effects produced by collision checks."""

    events: list[str] = field(default_factory=list)
    score_deltas: dict[PlayerId, int] = field(default_factory=dict)
    ship_deaths: list[PlayerId] = field(default_factory=list)
    asteroids_to_spawn: list[tuple[Vec, Vec, str]] = field(default_factory=list)

    pickups_to_spawn: list[Vec] = field(default_factory=list)
    shield_pickups_to_spawn: list[Vec] = field(default_factory=list)

    freeze_activated: bool = False
    shield_activated_for: list[PlayerId] = field(default_factory=list)


class CollisionManager:
    """Resolve todas as colisões entre entidades do jogo."""

    def resolve(
        self,
        ships: dict[PlayerId, Ship],
        bullets: pg.sprite.Group,
        asteroids: pg.sprite.Group,
        ufos: pg.sprite.Group,
        freezes: pg.sprite.Group | None = None,
        shields: pg.sprite.Group | None = None,
    ) -> CollisionResult:
        """Executa todos os testes de colisão e retorna o resultado agregado."""

        result = CollisionResult()

        self._bullets_vs_asteroids(bullets, asteroids, result)
        self._ufo_vs_player_bullets(ufos, bullets, result)
        self._ufo_vs_asteroids(ufos, asteroids, result)
        self._ship_vs_asteroids(ships, asteroids, result)
        self._ship_vs_ufo_bullets(ships, bullets, result)

        if freezes is not None:
            self._ship_vs_freeze_pickups(ships, freezes, result)

        if shields is not None:
            self._ship_vs_shield_pickups(ships, shields, result)

        return result

    def _bullets_vs_asteroids(
        self,
        bullets: pg.sprite.Group,
        asteroids: pg.sprite.Group,
        result: CollisionResult,
    ) -> None:
        hits = pg.sprite.groupcollide(
            asteroids,
            bullets,
            False,
            True,
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )

        for ast, hit_bullets in hits.items():
            if any(b.owner_id == UFO_BULLET_OWNER for b in hit_bullets):
                ast.kill()
                result.events.append("asteroid_explosion")
                continue

            player_bullets = [b for b in hit_bullets if b.owner_id > 0]
            scorer = player_bullets[0].owner_id if player_bullets else None
            self._split_asteroid(ast, scorer_id=scorer, result=result)

    def _ufo_vs_player_bullets(
        self,
        ufos: pg.sprite.Group,
        bullets: pg.sprite.Group,
        result: CollisionResult,
    ) -> None:
        for ufo in list(ufos):
            for bullet in list(bullets):
                if bullet.owner_id <= 0:
                    continue

                if (ufo.pos - bullet.pos).length() < (ufo.r + bullet.r):
                    score = C.UFO_SMALL["score"] if ufo.small else C.UFO_BIG["score"]
                    result.score_deltas[bullet.owner_id] = (
                        result.score_deltas.get(bullet.owner_id, 0) + score
                    )
                    ufo.kill()
                    bullet.kill()
                    result.events.append("ship_explosion")

    def _ufo_vs_asteroids(
        self,
        ufos: pg.sprite.Group,
        asteroids: pg.sprite.Group,
        result: CollisionResult,
    ) -> None:
        """UFO collided with asteroid.

        - UFO is destroyed.
        - Asteroid splits as if it were hit by a bullet, but without score.
        """
        for ufo in list(ufos):
            for ast in list(asteroids):
                if (ufo.pos - ast.pos).length() < (ufo.r + ast.r):
                    ufo.kill()
                    if ufo in ufos:
                        ufos.remove(ufo)
                    result.events.append("ship_explosion")
                    self._split_asteroid(ast, result=result)
                    break

    def _ship_vs_asteroids(
        self,
        ships: dict[PlayerId, Ship],
        asteroids: pg.sprite.Group,
        result: CollisionResult,
    ) -> None:
        for ship in ships.values():
            if ship.invuln > 0.0:
                continue

            for ast in list(asteroids):
                if (ast.pos - ship.pos).length() < (ast.r + ship.r):
                    if ship.shield_timer > 0.0:
                        self._split_asteroid(ast, result=result)
                        result.events.append("shield_block")
                        continue

                    result.ship_deaths.append(ship.player_id)
                    return

    def _ship_vs_ufo_bullets(
        self,
        ships: dict[PlayerId, Ship],
        bullets: pg.sprite.Group,
        result: CollisionResult,
    ) -> None:
        for ship in ships.values():
            if ship.invuln > 0.0:
                continue

            for bullet in list(bullets):
                if bullet.owner_id != UFO_BULLET_OWNER:
                    continue

                if (bullet.pos - ship.pos).length() < (bullet.r + ship.r):
                    bullet.kill()

                    if ship.shield_timer > 0.0:
                        result.events.append("shield_block")
                        continue

                    result.ship_deaths.append(ship.player_id)
                    return

    def _ship_vs_freeze_pickups(
        self,
        ships: dict[PlayerId, Ship],
        freezes: pg.sprite.Group,
        result: CollisionResult,
    ) -> None:
        """Verifica se alguma nave tocou um coletável Freeze."""
        for ship in ships.values():
            for pickup in list(freezes):
                distancia = (ship.pos - pickup.pos).length()
                if distancia < (ship.r + pickup.r):
                    pickup.kill()
                    result.freeze_activated = True
                    result.events.append("freeze_activated")
                    return

    def _ship_vs_shield_pickups(
        self,
        ships: dict[PlayerId, Ship],
        shields: pg.sprite.Group,
        result: CollisionResult,
    ) -> None:
        """Verifica se alguma nave tocou um coletável Shield."""
        for ship in ships.values():
            for pickup in list(shields):
                distancia = (ship.pos - pickup.pos).length()
                if distancia < (ship.r + pickup.r):
                    pickup.kill()
                    result.shield_activated_for.append(ship.player_id)
                    result.events.append("shield_activated")
                    return

    def _split_asteroid(
        self,
        ast: Asteroid,
        result: CollisionResult,
        scorer_id: PlayerId | None = None,
    ) -> None:
        """Divide ou destrói um asteroide."""
        if scorer_id is not None:
            result.score_deltas[scorer_id] = (
                result.score_deltas.get(scorer_id, 0) + C.AST_SIZES[ast.size]["score"]
            )

        split = C.AST_SIZES[ast.size]["split"]
        pos = Vec(ast.pos)

        ast.kill()
        result.events.append("asteroid_explosion")

        if random() < C.FREEZE_SPAWN_CHANCE:
            result.pickups_to_spawn.append(Vec(pos))

        if random() < C.SHIELD_SPAWN_CHANCE:
            result.shield_pickups_to_spawn.append(Vec(pos))

        for new_size in split:
            dirv = rand_unit_vec()
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX) * C.AST_SPLIT_SPEED_MULT
            result.asteroids_to_spawn.append((pos, dirv * speed, new_size))