#!/usr/bin/env bash
cd "$(dirname "$0")/.."
find . -type f -not -path './.git/*' -print0 | xargs -0 sha256sum | sort > MANIFEST.sha256
echo "MANIFEST.sha256 generated."
