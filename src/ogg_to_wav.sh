#!/usr/bin/env sh
find . -type f -name "*.ogg" \
| sort \
| xargs -I{} -n1 basename {} .ogg \
| xargs -I{} -n1 ffmpeg \
  -hide_banner \
  -hwaccel nvdec \
  -nostdin \
  -n \
  -i {}.ogg \
  -ac 1 \
  -af "highpass=f=50,lowpass=f=4000,afftdn=nr=10:nf=-30:tn=1" \
  -ar 22050 \
  {}.wav

# The band is from https://en.wikipedia.org/wiki/Voice_frequency
# Other filters of noise https://superuser.com/a/1393535/597070
