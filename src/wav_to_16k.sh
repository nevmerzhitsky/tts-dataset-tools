#!/usr/bin/env sh
find . -type f -name "*.wav" \
| sort \
| xargs -I{} -n1 basename {} .wav \
| xargs -I{} -n1 ffmpeg \
  -hide_banner \
  -hwaccel nvdec \
  -nostdin \
  -n \
  -i {}.wav \
  -ac 1 \
  -ar 16000 \
  wav-16k/{}.wav
