"""Collision detection and resolution."""

from dataclasses import dataclass, field
from random import random, uniform

import pygame as pg

from core import config as C
from core.entities import (
    Asteroid,
    PowerUp,
    Ship,
    SpecialAsteroid,
    Bullet,
    FreezePickup,
    ShieldPickup,
    Ship,
    UFO,
    UFO_BULLET_OWNER,
    PlayerId,
)
from core.entities import Asteroid, BlackHole, Bullet, FreezePickup, PlayerId, Ship, TripleShootPowerUp, UFO, UFO_BULLET_OWNER
from core.utils import Vec, rand_unit_vec


@dataclass
class CollisionResult:
    """Aggregated effects produced by collision checks."""
    """Resultado de um passo de resolução de colisões.

    Atributos:
        events: nomes de sons/efeitos a disparar.
        score_deltas: pontos a adicionar por jogador.
        ship_deaths: IDs de jogadores que morreram.
        asteroids_to_spawn: novos asteroides gerados por divisão.
        pickups_to_spawn: posições onde um FreezePickup deve ser criado.
        freeze_activated: True se a nave coletou um FreezePickup neste frame.
        triple_shoots_to_spawn: posições onde um TripleShootPowerUp deve ser criado.
    """

    events: list[str] = field(default_factory=list)
    score_deltas: dict[PlayerId, int] = field(default_factory=dict)
    lives_deltas: dict[PlayerId, int] = field(default_factory=dict)
    ship_deaths: list[PlayerId] = field(default_factory=list)
    asteroids_to_spawn: list[tuple[Vec, Vec, str, bool]] = field(default_factory=list)
    powerups_to_spawn: list[tuple[Vec, str]] = field(default_factory=list)

    pickups_to_spawn: list[Vec] = field(default_factory=list)
    shield_pickups_to_spawn: list[Vec] = field(default_factory=list)

    freeze_activated: bool = False
    shield_activated_for: list[PlayerId] = field(default_factory=list)
    pickups_to_spawn: list[Vec] = field(default_factory=list)   # posições para spawn de pickups
    freeze_activated: bool = False                               # True quando pickup coletado
    instant_kills: list[PlayerId] = field(default_factory=list)
    triple_shoots_to_spawn: list[Vec] = field(default_factory=list)    # posições para spawn de triple-shots


class CollisionManager:
    """Resolve todas as colisões entre entidades do jogo."""

    def resolve(
        self,
        ships: dict[PlayerId, Ship],
        bullets: pg.sprite.Group,
        asteroids: pg.sprite.Group,
        ufos: pg.sprite.Group,
        powerups: pg.sprite.Group,
        black_holes: pg.sprite.Group,
        freezes: pg.sprite.Group | None = None,
        shields: pg.sprite.Group | None = None,
        triple_shots: pg.sprite.Group | None = None,
    ) -> CollisionResult:
        """Executa todos os testes de colisão e retorna o resultado agregado."""

        result = CollisionResult()

        self._bullets_vs_asteroids(bullets, asteroids, result)
        self._ufo_vs_player_bullets(ufos, bullets, result)
        self._ufo_vs_asteroids(ufos, asteroids, result)
        self._ship_vs_powerups(ships, powerups, result)
        self._ship_vs_asteroids(ships, asteroids, result)
        self._ship_vs_ufo_bullets(ships, bullets, result)

        if freezes is not None:
            self._ship_vs_freeze_pickups(ships, freezes, result)

        if shields is not None:
            self._ship_vs_shield_pickups(ships, shields, result)

        self._ship_vs_black_holes(ships, black_holes, result)
        if triple_shots is not None:
            self._ship_vs_triple_shot_power_ups(ships, triple_shots, result)
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
                self._split_asteroid(
                    ast,
                    result,
                    killer="ufo_bullet",
                    scorer_id=None,
                )
                continue

            player_bullets = [b for b in hit_bullets if b.owner_id > 0]
            scorer = player_bullets[0].owner_id if player_bullets else None
            self._split_asteroid(
                ast,
                result,
                killer="player",
                scorer_id=scorer,
            )

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
                    self._split_asteroid(
                        ast,
                        result,
                        killer="ufo_body",
                        scorer_id=None,
                    )
                    break

    def _ship_vs_powerups(
        self,
        ships: dict[PlayerId, Ship],
        powerups: pg.sprite.Group,
        result: CollisionResult,
    ) -> None:
        for ship in ships.values():
            if ship.invuln > 0.0:
                continue
            for pup in list(powerups):
                if not isinstance(pup, PowerUp):
                    continue
                if (ship.pos - pup.pos).length() < (ship.r + pup.r):
                    if pup.kind == "extra_life":
                        result.lives_deltas[ship.player_id] = (
                            result.lives_deltas.get(ship.player_id, 0) + 1
                        )
                    pup.kill()

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
                    self._split_asteroid(
                        ast,
                        result,
                        killer="ship",
                        scorer_id=None,
                    )
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
                    return          # um pickup por frame é suficiente
                
    def _ship_vs_triple_shot_power_ups(
        self,
        ships: dict[PlayerId, Ship],
        triple_shots: pg.sprite.Group,
        result: CollisionResult,
    ) -> None:
        """Verifica se alguma nave tocou um coletável de tiro triplo.

        Ao coletar, remove o power-up e ativa o efeito de tiro triplo na nave.
        """
        for ship in ships.values():
            for power_up in list(triple_shots):
                distancia = (ship.pos - power_up.pos).length()
                if distancia < (ship.r + power_up.r):
                    power_up.kill()
                    ship.triple_shoot = True
                    ship.triple_shot_timer = float(C.TRIPLE_SHOT_DURATION)
                    result.events.append("triple_shot_activated")
                    return

    def _ship_vs_black_holes(
        self,
        ships: dict[PlayerId, Ship],
        black_holes: pg.sprite.Group,
        result: CollisionResult,
    ) -> None:
        """Instant Game Over when a ship touches a black hole."""
        for ship in ships.values():
            for bh in black_holes:
                if (bh.pos - ship.pos).length() < (bh.r + ship.r):
                    result.instant_kills.append(ship.player_id)
                    return

    def _split_asteroid(
        self,
        ast: Asteroid,
        result: CollisionResult,
        *,
        killer: str,
        scorer_id: PlayerId | None,
    ) -> None:
        if killer == "player" and scorer_id is not None:
            result.score_deltas[scorer_id] = (
                result.score_deltas.get(scorer_id, 0) + C.AST_SIZES[ast.size]["score"]
            )

        split = C.AST_SIZES[ast.size]["split"]
        pos = Vec(ast.pos)
        is_special = isinstance(ast, SpecialAsteroid)

        if killer == "player" and is_special and ast.size == "S":
            ast.kill()
            result.events.append("asteroid_explosion")
            result.powerups_to_spawn.append((pos, "extra_life"))
            return

        ast.kill()
        result.events.append("asteroid_explosion")

        inherit_one = (
            is_special
            and len(split) == 2
            and killer in ("player", "ship")
        )
        special_slot = int(uniform(0, 1) < 0.5) if inherit_one else -1

        for i, new_size in enumerate(split):
            dirv = rand_unit_vec()
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX) * C.AST_SPLIT_SPEED_MULT
            child_special = inherit_one and i == special_slot
            result.asteroids_to_spawn.append((pos, dirv * speed, new_size, child_special))
        if random() < C.FREEZE_SPAWN_CHANCE:
            result.pickups_to_spawn.append(Vec(pos))
        
        if random() < C.TRIPLE_SHOT_SPAWN_CHANCE:
            result.triple_shoots_to_spawn.append(Vec(pos))

        if random() < C.SHIELD_SPAWN_CHANCE:
            result.shield_pickups_to_spawn.append(Vec(pos))

        for new_size in split:
            dirv = rand_unit_vec()
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX) * C.AST_SPLIT_SPEED_MULT
            result.asteroids_to_spawn.append((pos, dirv * speed, new_size))
