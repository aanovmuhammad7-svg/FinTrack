from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.system import router as system_router_module


class FakeConnection:
    async def __aenter__(self) -> "FakeConnection":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def execute(self, statement) -> None:
        return None


class FakeEngine:
    def connect(self) -> FakeConnection:
        return FakeConnection()


class FakeRedis:
    async def ping(self) -> bool:
        return True


class BrokenRedis:
    async def ping(self) -> bool:
        raise RuntimeError("redis unavailable")


def create_test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(system_router_module.router)
    app.state.redis = FakeRedis()
    return app


def test_liveness_probe_returns_ok() -> None:
    client = TestClient(create_test_app())

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_probe_checks_database_and_redis(monkeypatch) -> None:
    monkeypatch.setattr(system_router_module, "engine", FakeEngine())
    client = TestClient(create_test_app())

    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "checks": {
            "database": "ok",
            "redis": "ok",
        },
    }


def test_readiness_probe_returns_503_when_dependency_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(system_router_module, "engine", FakeEngine())
    app = create_test_app()
    app.state.redis = BrokenRedis()
    client = TestClient(app)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": {
            "status": "error",
            "checks": {
                "database": "ok",
                "redis": "error",
            },
        }
    }
