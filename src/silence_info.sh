#!/usr/bin/env sh
for f in *.wav; do
  name=`basename "$f" .wav`
  echo Dumping silence data of $f...
  ffprobe -hide_banner -of ini -show_streams -i "$f" 2>&1 \
    | grep '^duration=' \
    | sed 's/=/ /' \
      > "$name-silence.txt"
  ffmpeg -hide_banner \
    -nostdin \
    -nostats \
    -i "$f" \
    -af silencedetect=noise=-30dB:duration=0.4 \
    -f null - 2>&1 \
    | sed 's/\r/\n/' \
    | grep silencedetect \
    | cut -d' ' -f4- \
    | sed 's/[\|\:]//g' \
    | xargs -n6 echo \
      >> "$name-silence.txt"
done
