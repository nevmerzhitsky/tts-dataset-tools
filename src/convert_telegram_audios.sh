#!/usr/bin/env sh
find . -type f -name "audio_*.ogg" \
| sed -nE "s/@([[:digit:]]+)-([[:digit:]]+)-([[:digit:]]+)_([[:digit:]]+)-([[:digit:]]+)-([[:digit:]]+).ogg/& \3\2\1_\4\5\6.ogg/p" \
| xargs -n2 mv
