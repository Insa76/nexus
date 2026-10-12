from security.models import Actor, ActorType


def test_create_user_actor() -> None:
    actor = Actor.user(
        "user-1",
        name="Usuario de prueba",
    )

    assert actor.id == "user-1"
    assert actor.actor_type == ActorType.USER
    assert actor.name == "Usuario de prueba"


def test_create_system_actor() -> None:
    actor = Actor.system()

    assert actor.id == "system"
    assert actor.actor_type == ActorType.SYSTEM


def test_create_service_actor() -> None:
    actor = Actor.service(
        "service-1",
        name="Servicio de prueba",
    )

    assert actor.id == "service-1"
    assert actor.actor_type == ActorType.SERVICE
    assert actor.name == "Servicio de prueba"
