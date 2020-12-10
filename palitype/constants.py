# -*- coding: utf-8 -*-
"""Contains constants."""
END_DELIMITER = '__EnD__TeRmINaL__'
YAML_KEYS = ("markup_language", "delimiters", "end_delimiter", "inline_markup",
             "hide", "tooltip", "exclude_db", "substitute")
DELIMITER_KEYS = (
    "token",
    "tag",
) + YAML_KEYS[3:]
