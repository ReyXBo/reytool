# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-08 13:18:24
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Text methods.
"""


from typing import Any, List, Tuple, Literal, Iterable, Optional
from decimal import Decimal
from urwid import old_str_util
from pprint import pformat as pprint_pformat
from json import dumps as json_dumps

from .rmonkey import monkey_patch_pprint_modify_width_judgment
from .rsystem import throw


__all__ = (
    "split_text",
    "get_width",
    "fill_width",
    "join_data_text",
    "join_filter_text",
    "add_text_frame",
    "to_json",
    "to_text"
)


# Monkey path.
monkey_patch_pprint_modify_width_judgment()


def split_text(text: str, man_len: int, by_width: bool = False) -> List[str]:
    """
    Split text by max length or not greater than display width.

    Parameters
    ----------
    text : Text.
    man_len : max length.
    by_width : Whether by char displayed width count length.

    Returns
    -------
    Split text.
    """

    # Split.
    texts = []

    ## By char displayed width.
    if by_width:
        str_group = []
        str_width = 0
        for char in text:
            char_width = get_width(char)
            str_width += char_width
            if str_width > man_len:
                string = "".join(str_group)
                texts.append(string)
                str_group = [char]
                str_width = char_width
            else:
                str_group.append(char)
        string = "".join(str_group)
        texts.append(string)

    ## By char number.
    else:
        test_len = len(text)
        split_n = test_len // man_len
        if test_len % man_len:
            split_n += 1
        for n in range(split_n):
            start_indxe = man_len * n
            end_index = man_len * (n + 1)
            text_group = text[start_indxe:end_index]
            texts.append(text_group)

    return texts


def get_width(text: str) -> int:
    """
    Get text display width.

    Parameters
    ----------
    text : Text.

    Returns
    -------
    Text display width.
    """

    # Get width.
    total_width = 0
    for char in text:
        char_unicode = ord(char)
        char_width = old_str_util.get_width(char_unicode)
        total_width += char_width

    return total_width


def fill_width(text: str, char: str, width: int, align: Literal["left", "right", "center"] = "right") -> str:
    """
    Text fill character by display width.

    Parameters
    ----------
    text : Fill text.
    char : Fill character.
    width : Fill width.
    align : Align orientation.
        - `Literal[`left`]` : Fill right, align left.
        - `Literal[`right`]` : Fill left, align right.
        - `Literal[`center`]` : Fill both sides, align center.

    Returns
    -------
    Text after fill.
    """

    # Check parameter.
    if get_width(char) != 1:
        throw(ValueError, char)

    # Fill width.
    text_width = get_width(text)
    fill_width = width - text_width
    if fill_width > 0:
        if align == "left":
            new_text = "".join((char * fill_width, text))
        elif align == "right":
            new_text = "".join((text, char * fill_width))
        elif align == "center":
            fill_width_left = int(fill_width / 2)
            fill_width_right = fill_width - fill_width_left
            new_text = "".join((char * fill_width_left, text, char * fill_width_right))
        else:
            throw(ValueError, align)
    else:
        new_text = text

    return new_text


def join_data_text(data: Iterable) -> str:
    """
    Join data to text.

    Parameters
    ----------
    data : Data.

    Returns
    -------
    Joined text.
    """

    # Join.

    ## Dict type.
    if data.__class__ == dict:
        texts = []
        for key, value in data.items():
            key_str = str(key)
            value_str = str(value)
            if "\n" in value_str:
                value_str = value_str.replace("\n", "\n    ")
                text_part = f"{key_str}:\n    {value_str}"
            else:
                text_part = f"{key_str}: {value_str}"
            texts.append(text_part)
        text = "\n".join(texts)

    ## Other type.
    else:
        text = "\n".join(
            [
                str(element)
                for element in data
            ]
        )

    return text


def join_filter_text(data: Iterable, char: str = ",", filter_: Tuple = (None, "")) -> str:
    """
    Join and filter text.

    Parameters
    ----------
    data : Data.
        - `Element is 'str'` : Join.
        - `Element is 'Any'` : Convert to string and join.

    char : Join character.
    filter_ : Filter elements.

    Returns
    -------
    Joined text.
    """

    # Filter and convert.
    data = [
        str(element)
        for element in data
        if element not in filter_
    ]

    # Join.
    text = char.join(data)

    return text


def add_text_frame(
    *texts: str,
    title: Optional[str],
    width: int,
    frame: Literal["full", "half", "top", "half_plain", "top_plain"]
) -> str:
    """
    Add text frame.

    Parameters
    ----------
    texts : Texts.
    title : Frame title.
        - `Union[None, Literal['']]` : No title.
        - `str` : Use this value as the title.

    width : Frame width.
    frame : Frame type.
        - `Literal[`full`]` : Add beautiful four side frame and limit length.
            * When throw `exception`, then frame is `half` type.
        - `Literal[`half`]` : Add beautiful top and bottom side frame.
        - `Literal[`top`]` : Add beautiful top side frame.
        - `Literal[`half_plain`]` : Add plain top and bottom side frame.
        - `Literal[`top_plain`]` : Add plain top side frame.

    Returns
    -------
    Added frame text.
    """

    # Handle parameter.
    if title is None or len(title) > width - 6:
        title = ""

    # Generate frame.

    ## Full type.
    if frame == "full":
        if title != "":
            title = f"╡ {title} ╞"
        width_in = width - 2
        _contents = []
        try:
            for content in texts:
                content_str = str(content)
                pieces_str = content_str.split("\n")
                content_str = [
                    "║%s║" % fill_width(line_str, " ", width_in)
                    for piece_str in pieces_str
                    for line_str in split_text(piece_str, width_in, True)
                ]
                content = "\n".join(content_str)
                _contents.append(content)
        except:
            frame_top = fill_width(title, "═", width, "center")
            frame_split = "─" * width
            frame_bottom = "═" * width
            _contents = texts
        else:
            frame_top = "╔%s╗" % fill_width(title, "═", width_in, "center")
            frame_split = "╟%s╢" % ("─" * width_in)
            frame_bottom = "╚%s╝" % ("═" * width_in)

    ## Half type.
    elif frame in ("half", "top"):
        if title != "":
            title = f"╡ {title} ╞"
        frame_top = fill_width(title, "═", width, "center")
        frame_split = "─" * width
        if frame == "half":
            frame_bottom = "═" * width
        elif frame == "top":
            frame_bottom = None
        _contents = texts

    ## Plain type.
    elif frame in ("half_plain", "top_plain"):
        if title != "":
            title = f"| {title} |"
        frame_top = fill_width(title, "=", width, "center")
        frame_split = "-" * width
        if frame == "half_plain":
            frame_bottom = "=" * width
        elif frame == "top_plain":
            frame_bottom = None
        _contents = texts

    ## Raise.
    else:
        throw(ValueError, frame)

    # Join.
    texts = [frame_top]
    for index, content in enumerate(_contents):
        if index != 0:
            texts.append(frame_split)
        texts.append(content)
    texts.append(frame_bottom)
    text = join_filter_text(texts, "\n")

    return text


def to_json(
    data: Any,
    compact: bool = True
) -> str:
    """
    Convert data to JSON format string.

    Parameters
    ----------
    data : Data.
    compact : Whether compact content.

    Returns
    -------
    JSON format string.
    """

    # Get parameter.
    if compact:
        indent = None
        separators = (",", ":")
    else:
        indent = 4
        separators = None

    # Convert.
    default = lambda value: (
        value.__float__()
        if value.__class__ == Decimal
        else repr(value)
    )
    string = json_dumps(
        data,
        ensure_ascii=False,
        indent=indent,
        separators=separators,
        default=default
    )

    return string


def to_text(
    data: Any,
    width: int = 100
) -> str:
    """
    Format data to text.

    Parameters
    ----------
    data : Data.
    width : Format width.

    Returns
    -------
    Formatted text.
    """

    # Format.

    ## Replace tab.
    if data.__class__ == str:
        text = data.replace("\t", "    ")

    ## Format contents.
    elif data.__class__ in (list, tuple, dict, set):
        text = pprint_pformat(data, width=width, sort_dicts=False)

    ## Other.
    else:
        text = str(data)

    return text