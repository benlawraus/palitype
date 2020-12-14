# -*- coding: utf-8 -*-
"""Contains constants."""
from dataclasses import dataclass

from typing import NamedTuple

END_DELIMITER = '__EnD__TeRmINaL__'


class Yaml_keywords(NamedTuple):
    """Stores yaml file keywords."""

    markup_language: str = "Markup Language".lower()
    delimiters: str = 'Delimiters'.lower()
    end_delimiter: str = 'End delimiter'.lower()
    inline_markup: str = 'Inner markup'.lower()
    substitute: str = "Substitute".lower()
    hide: str = 'Do not show'.lower()
    tooltip: str = 'Show when hover'.lower()
    exclude_db: str = "Exclude from database".lower()


@dataclass
class Delimiter:
    """Base class for delimiters, Also defaults."""

    token: str = 'TOKEN'
    tag: str = 'TAG'
    inline_markup: str = ''
    substitute: str = ''
    hide: bool = False
    tooltip: bool = False
    exclude_db: bool = False


VERSE_DELIM = Delimiter(tag='verse')
