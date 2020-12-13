# -*- coding: utf-8 -*-
"""Contains classes."""
from dataclasses import dataclass
from .constants import Delimiter, END_DELIMITER, Yaml_keywords
from typing import List, TypedDict, Any, Dict
from collections import namedtuple

Pair_item = namedtuple("Pair_item", "start end")
Pair_delimiter_text = namedtuple("Pair_delimiter_text", "delimiter text")


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
        self.group_id:int

    def __lt__(self, other)->bool:
        """Less than."""
        return self.p.start < other.p.start

    def __repr__(self)->str:
        """Stringify all members."""
        group_id = getattr(self, 'group_id', -1)
        return \
            f"s:'{self.str}' start:{self.p[0]} end:{self.p[1]} g_id:{group_id}"

    def equals(self, other:str)->bool:
        """Equal the token string."""
        return self.str == other


@dataclass
class Mod_counter:
    """Count the changes to the input text."""

    last_change = None

    def inc(self, key):
        """Increment an attribute."""
        self.last_change = key
        self.__setattr__(key, getattr(self, key, 0) + 1)
        return


class Delim(Delimiter):
    """Class describing the yml file information of each delimiter.

    The class has the form of:

    ..  code-block:: python

        __dict__ = {"token":"e=", "tag":"English", "inline_markup":"*",
              "hide":False, "tooltip":False, "exclude_db":False,
            "substitute":".. class m-noindent"}
    """
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
        return '\n'.join(_text)

    def get_modified_lines(self, text: str, mod: Mod_counter) -> str:
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
            _line = self.substitute + text 
            mod.inc('substitute')
        elif self.hide:    
            mod.inc('hide')
            return ''
        else:
            _line = text
            mod.inc('untouched')
        return _line


class Setting:
    """Contain all the information from the input yaml file instructions."""
    
    def __init__(self, yaml_dict: Dict):
        self.markup_language = self.get_markup_language(
            yaml_dict.get('markup_language', ''))
        self.delim_dict = self.get_delims(yaml_dict)
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
    def get_delims(yaml_dict: Dict) -> Dict:
        """Use `strictyaml` schema to return a `dict`.

        Parameters
        ----------
        settings : TypedDict
            DESCRIPTION.

        Returns
        -------
        TypedDict
            DESCRIPTION.
        """
        delim_dict = {}
        yk=Yaml_keywords()
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
        end_token = str(yaml_dict.get(yk.end_delimiter)) # for mypy
        delim_dict[end_token] = Delim(end_token, END_DELIMITER)
        return delim_dict
