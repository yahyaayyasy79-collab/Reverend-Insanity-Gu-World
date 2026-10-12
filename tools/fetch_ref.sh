#!/usr/bin/env bash
# Recreates ref/unciv: a shallow, sparse, blob-less clone of Unciv at a release tag.
# ref/ is gitignored; run this once per fresh checkout (cloud containers are ephemeral).
#
#   tools/fetch_ref.sh            # default tag below
#   tools/fetch_ref.sh 4.22.8     # pin another release (match the version you play)
#   tools/fetch_ref.sh master     # bleeding edge: docs may describe features your release lacks
set -euo pipefail

TAG="${1:-4.22.8}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/ref/unciv"

if [ -d "$DEST/.git" ]; then
    echo "ref/unciv already exists ($(git -C "$DEST" describe --tags --always 2>/dev/null || echo unknown))."
    echo "Delete it first to re-fetch: rm -rf ref/unciv"
    exit 0
fi

mkdir -p "$ROOT/ref"
git clone --depth 1 --branch "$TAG" --filter=blob:none --sparse \
    https://github.com/yairm210/Unciv "$DEST"

# Spec paths (docs + bundled rulesets), plus the translation template and the
# engine source used to answer behaviour questions the docs leave open.
git -C "$DEST" sparse-checkout set --no-cone \
    "/docs/Modders/" \
    "/docs/Translating/" \
    "/android/assets/jsons/Civ V - Gods & Kings/" \
    "/android/assets/jsons/Civ V - Vanilla/" \
    "/android/assets/jsons/translations/template.properties" \
    "/core/src/com/unciv/"

# Names of the images bundled with the game (no blobs needed): a mod object whose
# icon already exists in the base atlas needs no placeholder.
git -C "$DEST" ls-tree -r --name-only HEAD -- android \
    | grep -E '^android/Images[^/]*/' \
    | sed -E 's#^android/Images[^/]*/##; s#\.png$##' \
    | sort -u > "$ROOT/ref/builtin_images.txt"

echo "$TAG" > "$ROOT/ref/UNCIV_TAG"
echo "Fetched Unciv $TAG into ref/unciv ($(wc -l < "$ROOT/ref/builtin_images.txt") builtin image names)."
