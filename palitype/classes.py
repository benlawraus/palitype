# -*- coding: utf-8 -*-
"""Contains classes."""
from dataclasses import dataclass
from .constants import YAML_KEYS, DELIMITER_KEYS, END_DELIMITER
from typing import List, TypedDict
from collections import namedtuple

Pair_item = namedtuple("Pair_item", "start end")
Pair_delimiter_text = namedtuple("Pair_delimiter_text", "delimiter text")

Yaml_keywords = namedtuple("Yaml_keywords", YAML_KEYS)


class Token():
    """Contains token string and its position in the input text."""

    def __init__(self, s: str, p: int):
        """Initiate.

        Parameters
        ----------
        s : str
            token.
        p : int
            location of first char of token.

        """
        self.str = s
        self.p = Pair_item(p, p + len(s))

    def __lt__(self, other):
        """Less than."""
        return self.p.start < other.p.start

    def __repr__(self):
        """Stringify all members."""
        group_id = getattr(self, 'group_id', -1)
        return \
            f"s:'{self.str}' start:{self.p[0]} end:{self.p[1]} g_id:{group_id}"

    def __eq__(self, other: str):
        """Equal the token string."""
        return self.str == other

    def equals(self, other):
        """Equal the token string and the position."""
        return self.str == other.str and self.p == other.p


@dataclass
class Mod_counter:
    """Count the changes to the input text."""

    last_change = None

    def inc(self, key):
        """Increment an attribute."""
        self.last_change = key
        self.__setattr__(key, getattr(self, key, 0) + 1)
        return


class Delim():
    """Class describing the yml file information of each delimiter.

    The class has the form of:

    ..  code-block:: python

        __dict__ = {"token":"e=", "tag":"English", "inline_markup":"*",
              "hide":False, "tooltip":False, "exclude_db":False,
            "substitute":".. class m-noindent"}
    """

    def __init__(self, *args):
        for ix, d in enumerate(DELIMITER_KEYS):
            if ix < len(args):    # assign from args
                self.__setattr__(d, args[ix])
            # these require text, so make null string as default
            elif d in ["inline_markup", "substitute"]:
                self.__setattr__(d, '')
            # these are bool so default to False
            else:
                self.__setattr__(d, False)

    def __eq__(self, token: str) -> bool:
        """Use to compare to token object with a str.

        Parameters
        ----------
        token : str

        Returns
        -------
        bool
        """
        return self.token == token

    @staticmethod
    def surround(m: str, text: str) -> str:
        """Modify text to include inline_markup `m`.

        Specifically for markup when text that requires inline markup
        spans multiple lines. So the markup must also be added on each line
        separately.

        Parameters
        ----------
        m : str
            The markup instruction that encloses the text.
        text : str
            The input text.

        Returns
        -------
        str
            text enclosed in the m string.
        """
        _text = []
        for line in text.splitlines():
            _l = line.strip()
            if _l:
                _text.append(line.replace(_l, ''.join((m, _l, m))))
            else:
                _text.append(line)
        return _text

    def get_modified_lines(self, text: str, mod: Mod_counter) -> List[str]:
        """Modify the line by adding inline-markup or substituting or hiding.

        Parameters
        ----------
        text : str
            The string that is to be modified. Does not contain any markup.
        mod : Mod_counter
            A counter of what was modified.

        Returns
        -------
        List[str]
            A list of the modified text broken up into lines
            according to the presence of newline.
        """
        if self.inline_markup:
            # markup insertion
            _line = Delim.surround(self.inline_markup, text)
            mod.inc('inline_markup')
        elif self.substitute:
            _line = [self.substitute + text]
            mod.inc('substitute')
        elif self.hide:
            mod.inc('hide')
            return None
        else:
            _line = [text]
            mod.inc('untouched')
        return _line


class Setting:
    """Contain all the information from the input yaml file instructions."""

    def __init__(self, yaml_dict: TypedDict, yk: Yaml_keywords):
        self.markup_language = self.get_markup_language(
            yaml_dict.get('markup_language', ''))
        self.delim_dict = self.get_delims(yaml_dict, yk)
        self.verse_line_markup = '| ' \
            if self.markup_language == 'rst' else ''

    @staticmethod
    def get_markup_language(lang: str = '') -> str:
        """Limit variations in descriptor to `rst` or `md` etc."""
        _m = lang.strip().replace(' ', '').lower()
        if _m in ('restructuredtext', 'rst', 'rest', ''):
            return 'rst'
        if _m in ('markdown', 'md'):
            return 'md'
        return 'rst'

    @staticmethod
    def get_delims(yaml_dict: TypedDict, yk: Yaml_keywords) -> TypedDict:
        """Use `strictyaml` schema to return a `dict`.

        Parameters
        ----------
        settings : TypedDict
            DESCRIPTION.
        yk : Yaml_keywords
            DESCRIPTION.

        Returns
        -------
        TypedDict
            DESCRIPTION.
        """
        delim_dict = {}
        for tag, delim in yaml_dict.get(yk.delimiters, {}).items():
            if tag in ['Verse']:
                _d = Delim(delim, tag.lower())
            else:
                _d = Delim(delim, tag)
            _d.inline_markup = yaml_dict.get(yk.inline_markup, {
                tag: ''
            }).get(tag, '')
            _d.hide = tag in yaml_dict.get(yk.hide, [])
            _d.tooltip = tag in yaml_dict.get(yk.tooltip, [])
            _d.exclude_db = tag in yaml_dict.get(yk.exclude_db, [])
            _d.substitute = yaml_dict.get(yk.substitute, {tag: ''})\
                .get(tag, '')
            delim_dict[_d.token] = _d
        delim_dict[yaml_dict.get(yk.end_delimiter)] = \
            Delim(yaml_dict.get(yk.end_delimiter), END_DELIMITER)
        return delim_dict
