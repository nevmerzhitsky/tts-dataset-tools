from dataclasses import dataclass
from glob import iglob
from itertools import pairwise
from os import getcwd, path, system
from typing import Iterator


@dataclass(frozen=True)
class SilencePeriod:
    start: float
    end: float


@dataclass(frozen=True)
class Chunk:
    start: float
    end: float


@dataclass(frozen=True)
class FileInfo:
    duration: float
    silence_periods: list[SilencePeriod]


def main():
    silence_periods = load_silence_periods(getcwd())
    for name, file_info in silence_periods.items():
        chunks = convert_silence_periods_to_chunks(
            file_info.silence_periods,
            file_info.duration,
            10,
            0.20
        )
        commands = convert_chunks_to_commands(name, chunks)
        [system(cmd) for cmd in commands]


def load_silence_periods(dir_path: str, suffix: str = '-silence.txt') -> dict[str, FileInfo]:
    result: dict[str, FileInfo] = {}

    for file_path in sorted(iglob(path.join(dir_path, f'*{suffix}'))):
        name = file_path[:-len(suffix)]
        result[name] = get_silence_periods_from_file(file_path)

    return result


def get_silence_periods_from_file(file_path: str) -> FileInfo:
    total_duration = None
    periods = []

    with open(file_path) as f:
        for line in f.read().splitlines():
            parts = line.split(' ')

            if len(parts) == 0 or len(parts) % 2 != 0:
                continue

            data = dict((k, v) for k, v in zip(parts[0::2], parts[1::2]))

            if 'duration' in data:
                total_duration = float(data['duration'])
            elif 'silence_start' in data and 'silence_end' in data:
                periods.append(SilencePeriod(
                    float(data['silence_start']),
                    float(data['silence_end']),
                ))

    assert total_duration is not None, "File must contain 'duration' field"

    return FileInfo(total_duration, periods)


def convert_silence_periods_to_chunks(
    silence_periods: list[SilencePeriod],
    total_duration: float,
    min_duration: float,
    extended_duration: float = 0,
    skip_short_tail: bool = False,
) -> Iterator[Chunk]:
    speech_periods = _convert_silence_periods_to_speech_periods(silence_periods, total_duration)
    return _glue_chunks_to_minimum_length(speech_periods, min_duration, extended_duration, skip_short_tail)


def _convert_silence_periods_to_speech_periods(
    silence_periods: list[SilencePeriod],
    total_duration: float,
) -> list[Chunk]:
    result: list[Chunk] = []

    if total_duration <= 0:
        return result

    # Add fake moments of silence to beginning and end of the audio. This simplifies algorythm.
    if len(silence_periods) == 0 or silence_periods[0].start != 0:
        silence_periods.insert(0, SilencePeriod(0, 0))
    if len(silence_periods) == 0 or silence_periods[-1].end != total_duration:
        silence_periods.append(SilencePeriod(total_duration, total_duration))

    for (silence, next_silence) in pairwise(silence_periods):
        result.append(Chunk(silence.end, next_silence.start))

    # Filter out zero-length chunks.
    result = list(filter(lambda c: c.start != c.end, result))

    return result


def _glue_chunks_to_minimum_length(
    speech_periods: list[Chunk],
    min_duration: float,
    extended_duration: float = 0,
    skip_short_tail: bool = False,
) -> Iterator[Chunk]:
    if len(speech_periods) == 0:
        return

    last_chunk_end = speech_periods[-1].end

    def build_chunk(chunk_start, chunk_end) -> Chunk:
        extended_start = max(chunk_start - extended_duration, 0)
        extended_end = min(chunk_end + extended_duration, last_chunk_end)
        return Chunk(extended_start, extended_end)

    chunk = prev_chunk_start = None
    for chunk in speech_periods:
        if prev_chunk_start is None:
            prev_chunk_start = chunk.start

        chunk_candidate_duration = chunk.end - prev_chunk_start

        if chunk_candidate_duration >= min_duration:
            yield build_chunk(prev_chunk_start, chunk.end)
            prev_chunk_start = None

    if not skip_short_tail and chunk is not None and prev_chunk_start is not None:
        chunk_candidate_duration = chunk.end - prev_chunk_start

        if chunk_candidate_duration > 0:
            yield build_chunk(prev_chunk_start, chunk.end)


def convert_chunks_to_commands(name: str, chunks: Iterator[Chunk]) -> Iterator[str]:
    """
    Inspired by https://stackoverflow.com/a/36077309/3155344
    """
    source_dir = path.dirname(name)
    file_name_prefix = path.basename(name)

    for (n, chunk) in enumerate(chunks, start=1):
        duration = chunk.end - chunk.start
        if duration <= 1:
            continue
        if duration > 20:
            name_suffix = "-long"
        elif duration < 5:
            name_suffix = "-short"
        else:
            name_suffix = ""

        output_file_name = f'{file_name_prefix}_{n:04d}{name_suffix}.wav'
        output_file_path = path.join(source_dir, "chunks", output_file_name)

        if path.isfile(output_file_path):
            continue

        yield f'ffmpeg -hide_banner -hwaccel nvdec -nostdin -nostats -n' \
              f' -ss {chunk.start:.4f}' \
              f' -to {chunk.end:.4f}' \
              f' -i {name}.wav' \
              f' {output_file_path}'


if __name__ == '__main__':
    main()
