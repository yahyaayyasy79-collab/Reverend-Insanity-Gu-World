"""Sound file names shared by the ruleset generators (no numpy) and tools/art/sfx.py, which synthesizes the files into
sounds/ (needs numpy and ffmpeg; the .ogg files are committed, so only regenerating them needs those)."""


def path_sound(key: str, tier: int) -> str:
    return f"path-{key}-{tier}"


def move_sound(key: str, immortal: bool) -> str:
    return f"move-{key}{'-immortal' if immortal else ''}"


def rank_sound(rank: int) -> str:
    return f"gu-rank-{rank}"


def dao_sound(tier: int) -> str:
    return f"dao-{tier}"
