import asyncio
import time

from pyflowlauncher import FlowLauncherV2, Plugin, Result

import bttv

TOP_EMOTES_MAX_AGE = 300

plugin = Plugin(launcher=FlowLauncherV2())
api = plugin.launcher.api
icons = plugin.launcher.icons


class TopEmotes:

    def __init__(self, max_age=TOP_EMOTES_MAX_AGE, clock=time.monotonic):
        self.max_age = max_age
        self.clock = clock
        self._emotes = []
        self._fetched_at = 0.0

    def get(self):
        if self._emotes and self.clock() - self._fetched_at < self.max_age:
            return self._emotes
        emotes = bttv.top_emotes()
        if emotes:
            self._emotes = emotes
            self._fetched_at = self.clock()
        return emotes


top_emotes = TopEmotes()


async def in_thread(func, *args):
    return await asyncio.get_running_loop().run_in_executor(None, func, *args)


def emote_result(emote):
    return Result(
        title=emote["code"],
        subtitle=f"Streamer: {emote['user']['name']}",
        icon=bttv.image_url(emote),
        context_data=[emote],
    ).add_action(copy_to_clipboard, [bttv.image_url(emote, "3x"), emote["code"]])


@plugin.on_method
async def query(query: str):
    if len(query) >= bttv.MIN_QUERY_LEN:
        emotes = await in_thread(bttv.search_emotes, query)
    elif not query:
        emotes = await in_thread(top_emotes.get)
    else:
        return Result(
            title="Invalid search!",
            subtitle=f"{bttv.MIN_QUERY_LEN} or more characters required.",
            icon=icons.app_error,
        )
    return [emote_result(emote) for emote in emotes]


@plugin.on_method
async def copy_to_clipboard(url: str, code: str):
    await api.invoke(api.copy_to_clipboard(url, show_default_notification=False))
    return api.show_msg("Copied to clipboard", f"Emote: {code}", url)


@plugin.on_method
def context_menu(data):
    emote = data[0]
    url = bttv.image_url(emote, "3x")
    return [
        Result(
            title="Open in browser",
            subtitle="Open icon in web browser.",
            icon=icons.browser,
        ).add_action(api.open_url(url)),
        Result(
            title="Copy to clipboard",
            subtitle="Copy emote to clipboard.",
            icon=icons.copy,
        ).add_action(copy_to_clipboard, [url, emote["code"]]),
    ]
