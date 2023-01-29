#!/usr/bin/env sh
find . -type f -name "*.ogg" \
| sort \
| xargs -I{} -n1 basename {} .ogg \
| xargs -I{} -n1 docker run --rm --runtime=nvidia -v $(pwd):/config linuxserver/ffmpeg \
  -hide_banner \
  -hwaccel nvdec \
  -nostdin \
  -i /config/{}.ogg \
  -af "highpass=f=50,lowpass=f=4000,afftdn=nr=10:nf=-30:tn=1" \
  -ar 22050 \
  -n \
  /config/{}.wav

# The band is from https://en.wikipedia.org/wiki/Voice_frequency
# Other filters of noise https://superuser.com/a/1393535/597070
