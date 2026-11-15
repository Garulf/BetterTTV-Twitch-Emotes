import asyncio

import pytest

import bttv
import emotes


def make_emote(emote_id, code, user, image_type="png"):
    return {
        "id": emote_id,
        "code": code,
        "imageType": image_type,
        "animated": image_type == "gif",
        "user": {"id": f"u-{user}", "name": user, "displayName": user, "providerId": "1000"},
    }


SEARCH = [
    make_emote("5f1b0186cf6d2144653d2970", "pogDance", "streamer_one", "gif"),
    make_emote("5e0fa9d40550d42106b8a489", "pogWave", "another_streamer"),
]
TOP = [
    {"id": "5e0fa9d40550d42106b8a489", "total": 100, "emote": make_emote("5e0fa9d40550d42106b8a489", "coffeeTime", "cozy_corner")},
]


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


class FakeApi:
    def __init__(self):
        self.calls = []
        self.payloads = {"search": SEARCH, "top": TOP}
        self.status_code = 200

    def get(self, url, headers=None, params=None, timeout=None):
        endpoint = url[len(bttv.API_URL):]
        self.calls.append((endpoint, dict(params or {}), timeout))
        return FakeResponse(self.payloads[endpoint], self.status_code)


@pytest.fixture
def api(monkeypatch):
    fake = FakeApi()
    monkeypatch.setattr(bttv.requests, "get", fake.get)
    return fake


@pytest.fixture(autouse=True)
def fresh_top_emotes(monkeypatch):
    monkeypatch.setattr(emotes, "top_emotes", emotes.TopEmotes())


class FakeHost:
    def __init__(self):
        self.requests = []

    async def request(self, method, params, timeout=None):
        self.requests.append((method, params))


@pytest.fixture
def host(monkeypatch):
    fake = FakeHost()
    monkeypatch.setattr(emotes.plugin.launcher._client, "request", fake.request)
    return fake


@pytest.fixture
def rpc():
    def call(method, *params):
        return asyncio.run(emotes.plugin._event_handler.trigger_event(method, *params))

    return call
