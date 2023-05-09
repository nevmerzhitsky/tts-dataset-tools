import pytest

from split_by_silence import Chunk, SilencePeriod, convert_silence_periods_to_chunks


@pytest.mark.parametrize(
    'silence_periods, total_duration, min_duration, extended_duration, skip_short_tail',
    [
        ([], 0.0, 10, 0, False),
        ([], 0.0, 10, 0, True),
        ([], 1.0, 10, 1.1, True),
        ([], 5.0, 10, 0, True),
        ([SilencePeriod(0.0, 0.8)], 9.9, 10, 0, True),
        ([SilencePeriod(5.0, 5.1)], 9.9, 10, 0, True),
        ([SilencePeriod(9.9, 9.9)], 9.9, 10, 0, True),
    ]
)
def test_convert_silence_periods_to_chunks_returns_empty_list(
    silence_periods: list,
    total_duration: float,
    min_duration: float,
    extended_duration: float,
    skip_short_tail: bool,
):
    result = convert_silence_periods_to_chunks(
        silence_periods,
        total_duration,
        min_duration,
        extended_duration,
        skip_short_tail,
    )
    assert list(result) == []


@pytest.mark.parametrize(
    'silence_periods, total_duration, min_duration, extended_duration, skip_short_tail, expected',
    [
        ([], 10.0, 10, 0, False, [Chunk(0, 10.0)]),
        ([], 10.0, 10, 0, True, [Chunk(0, 10.0)]),
        ([], 30.0, 10, 0, False, [Chunk(0, 30.0)]),
        ([], 30.0, 10, 0, True, [Chunk(0, 30.0)]),
    ]
)
def test_convert_silence_periods_to_chunks_when_no_silence_periods(
    silence_periods: list,
    total_duration: float,
    min_duration: float,
    extended_duration: float,
    skip_short_tail: bool,
    expected: list[Chunk],
):
    result = convert_silence_periods_to_chunks(
        silence_periods,
        total_duration,
        min_duration,
        extended_duration,
        skip_short_tail,
    )
    assert list(result) == expected


def data_with_silence_periods():
    silence_periods = [
        SilencePeriod(9.1, 10.0),
        SilencePeriod(16.7, 17.3),
        SilencePeriod(21.8, 22.3),
        SilencePeriod(28.4, 28.9),
        SilencePeriod(30.2, 30.6),
    ]
    yield silence_periods, 32.7, 10, 0, False, \
        [Chunk(0.0, 16.7), Chunk(17.3, 28.4), Chunk(28.9, 32.7)]
    yield silence_periods, 32.7, 10, 0, True, \
        [Chunk(0.0, 16.7), Chunk(17.3, 28.4)]
    yield [SilencePeriod(0.0, 0.8), *silence_periods], 32.7, 10, 0, False, \
        [Chunk(0.8, 16.7), Chunk(17.3, 28.4), Chunk(28.9, 32.7)]
    yield [SilencePeriod(0.0, 0.8), *silence_periods], 32.7, 10, 0, True, \
        [Chunk(0.8, 16.7), Chunk(17.3, 28.4)]
    yield [*silence_periods, SilencePeriod(30.9, 32.7)], 32.7, 10, 0, False, \
        [Chunk(0.0, 16.7), Chunk(17.3, 28.4), Chunk(28.9, 30.9)]
    yield [*silence_periods, SilencePeriod(30.9, 32.7)], 32.7, 10, 0, True, \
        [Chunk(0.0, 16.7), Chunk(17.3, 28.4)]
    yield [SilencePeriod(0.0, 0.8), *silence_periods, SilencePeriod(30.9, 32.7)], 32.7, 10, 0, \
        False, [Chunk(0.8, 16.7), Chunk(17.3, 28.4), Chunk(28.9, 30.9)]
    yield [SilencePeriod(0.0, 0.8), *silence_periods, SilencePeriod(30.9, 32.7)], 32.7, 10, 0, \
        True, [Chunk(0.8, 16.7), Chunk(17.3, 28.4)]


@pytest.mark.parametrize(
    'silence_periods, total_duration, min_duration, extended_duration, skip_short_tail, expected',
    data_with_silence_periods()
)
def test_convert_silence_periods_to_chunks_when_silence_periods(
    silence_periods: list,
    total_duration: float,
    min_duration: float,
    extended_duration: float,
    skip_short_tail: bool,
    expected: list[Chunk],
):
    result = convert_silence_periods_to_chunks(
        silence_periods,
        total_duration,
        min_duration,
        extended_duration,
        skip_short_tail,
    )
    assert list(result) == expected
