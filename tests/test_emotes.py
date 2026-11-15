import emotes


def titles(response):
    return [result["Title"] for result in response["Result"]]


def test_search_lists_matching_emotes(api, downloads, rpc):
    response = rpc("query", "pog")

    assert titles(response) == ["pogDance", "pogWave"]
    assert api.calls == [("search", {"query": "pog", "limit": 25}, 10)]
    first = response["Result"][0]
    assert first["SubTitle"] == "Streamer: streamer_one"
    assert first["ContextData"][0]["code"] == "pogDance"


def test_enter_copies_the_large_image_url(api, downloads, rpc):
    action = rpc("query", "pog")["Result"][0]["JsonRPCAction"]

    assert action["Method"] == "copy_to_clipboard"
    assert action["Parameters"] == ["https://cdn.betterttv.net/emote/5f1b0186cf6d2144653d2970/3x.gif", "pogDance"]


def test_short_query_asks_for_more_characters(api, rpc):
    response = rpc("query", "po")

    assert titles(response) == ["Invalid search!"]
    assert response["Result"][0]["SubTitle"] == "3 or more characters required."
    assert api.calls == []


def test_empty_query_lists_top_emotes(api, downloads, rpc):
    response = rpc("query", "")

    assert titles(response) == ["coffeeTime"]
    assert api.calls == [("top", {"offset": 0, "limit": 25}, 10)]


def test_top_emotes_are_cached_for_five_minutes(api, monkeypatch):
    now = [1000.0]
    cache = emotes.TopEmotes(clock=lambda: now[0])

    cache.get()
    now[0] += 299
    cache.get()
    assert len(api.calls) == 1

    now[0] += 2
    cache.get()
    assert len(api.calls) == 2


def test_empty_top_emotes_are_not_cached(api):
    api.payloads["top"] = []
    cache = emotes.TopEmotes(clock=lambda: 0.0)

    assert cache.get() == []
    cache.get()
    assert len(api.calls) == 2


def test_api_error_payload_gives_no_results(api, downloads, rpc):
    api.payloads["search"] = {"message": "unauthorized"}

    assert rpc("query", "pog")["Result"] == []


def test_context_menu_opens_and_copies_the_emote(api, downloads, rpc):
    emote = rpc("query", "pog")["Result"][0]["ContextData"]

    menu = rpc("context_menu", emote)["Result"]

    url = "https://cdn.betterttv.net/emote/5f1b0186cf6d2144653d2970/3x.gif"
    assert [item["Title"] for item in menu] == ["Open in browser", "Copy to clipboard"]
    assert menu[0]["JsonRPCAction"]["Method"] == "Flow.Launcher.OpenUrl"
    assert menu[0]["JsonRPCAction"]["Parameters"] == [url, False]
    assert menu[1]["JsonRPCAction"]["Method"] == "copy_to_clipboard"
    assert menu[1]["JsonRPCAction"]["Parameters"] == [url, "pogDance"]


def test_copy_puts_the_url_on_the_clipboard_and_says_so(host, rpc):
    url = "https://cdn.betterttv.net/emote/abc/3x.png"

    command = rpc("copy_to_clipboard", url, "pogWave")

    assert host.requests == [("CopyToClipboard", [url, False, False])]
    assert command == {"Method": "Flow.Launcher.ShowMsg", "Parameters": ["Copied to clipboard", "Emote: pogWave", url]}
