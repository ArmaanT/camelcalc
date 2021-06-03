from functools import reduce
from typing import Iterable, TypeVar


T = TypeVar("T")


def multiline_concat(
    s1: str, s2: str, merge_from_bottom: bool = True, sep: str = "    "
) -> str:
    """
    Horizontally joins two multiline strings using seperator `sep`
    with proper spacing. Used to join two "column" of data
    """

    s1_split = s1.split("\n")
    s2_split = s2.split("\n")

    # Pad number of lines in each string to ensure they're equal
    s1_split_length = len(s1_split)
    s2_split_length = len(s2_split)
    s1_fixed_length = [
        "" for _ in range(max(s1_split_length, s2_split_length) - s1_split_length)
    ]
    s2_fixed_length = [
        "" for _ in range(max(s1_split_length, s2_split_length) - s2_split_length)
    ]

    # Determine merge order
    if merge_from_bottom:
        s1_fixed_length.extend(s1_split)
        s2_fixed_length.extend(s2_split)
    else:
        s1_split.extend(s1_fixed_length)
        s2_split.extend(s2_fixed_length)
        s1_fixed_length = s1_split
        s2_fixed_length = s2_split

    # Pad each individual string within each column to ensure they're equal
    s1_length_max = max(len(s) for s in s1_fixed_length)
    s2_length_max = max(len(s) for s in s2_fixed_length)
    s1_fixed_width = [f"{s:<{s1_length_max}}" for s in s1_fixed_length]
    s2_fixed_width = [f"{s:<{s2_length_max}}" for s in s2_fixed_length]

    # Concatenate the two multiline strings
    return "\n".join(sep.join(elem) for elem in zip(s1_fixed_width, s2_fixed_width))


def multiline_concat_list(
    s: Iterable[str], merge_from_bottom: bool = True, sep: str = "    "
) -> str:
    """
    Horizontally joins a list of multiline strings
    """

    return reduce(lambda x, y: multiline_concat(x, y, merge_from_bottom, sep), s)


def to_string(list_: Iterable[T]) -> Iterable[str]:
    return map(str, list_)
