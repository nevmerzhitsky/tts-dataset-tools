# Prepare dataset for training a text-to-speech/vocoder model

## Audio files preparation

For example, let's prepare a dataset from a Telegram channel/chat audio files.

First of all, export a desired audio files by Telegram Desktop.

Fix name of files from Telegram (`audio_10@28-04-2021_03-20-45.ogg` to `20210428_032045.ogg`):

```shell
cd telegram-oggs-dir/
./convert_telegram_audios.sh
mv *.ogg source-oggs-dir/
```

Convert OGG files to WAV:

```shell
cd source-oggs-dir/
./ogg_to_wav.sh
mv *.wav big-wavs-dir/
```

Noise filtering, down-sampling and other filters are also applied.

Links:
- https://superuser.com/a/1393535/597070

Split audio files to 10+ second chunks by find moments of silence:

```shell
cd big-wavs-dir/
./silence_info.sh
python ./split_by_silence.py
```
