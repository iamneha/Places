#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Add import context."""

from pathlib import Path
import sys
import pytest

src = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(src))

ENV_VARS = {
    "POSTGRES_HOST": "",
    "POSTGRES_USER": "",
    "POSTGRES_PASSWORD": "",
    "POSTGRES_PORT": "",
    "POSTGRES_DB": "",
    "API_KEY": "",
}


@pytest.fixture(scope="session", autouse=True)
def set_envs(request):
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    for env, value in ENV_VARS.items():
        mpatch.setenv(env, value)


@pytest.fixture(scope="session")
def client():
    from backend.app import create_app, app

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with create_app().test_client() as test_client:
        yield test_client
