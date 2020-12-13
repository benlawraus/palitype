# -*- coding: utf-8 -*-
"""To make writing about pali texts easier."""


from typing import List, Tuple, TypedDict, Dict, cast
import strictyaml as sy
import pathlib
import argparse

import sys
from .classes import Yaml_keywords, Token, Mod_counter, Setting
# from palitype.lists import L
from more_itertools import (pairwise)
module_dir = pathlib.Path(__file__).parent
if str(module_dir) not in sys.path:
    sys.path.append(str(module_dir))


def str_location(delim: str, text: str) -> List[int]:
    """Find all the str in the text. Returns list of locations.

    Parameters
    ----------
    delim : str
        DESCRIPTION.
    text : str
        DESCRIPTION.

    Returns
    -------
    List[int]
        A list of character locations in the string `text`
    """
    found = True
    locs = []
    start = 0
    while found:
        loc = text.find(delim, start)
        start = loc + 1
        if loc != -1:
            locs.append(loc)
        else:
            found = False
    return locs


def delimiter_locations(delimiters: Tuple[str], text: str) -> List[Token]:
    """Find location of the delimiters in the text as the appear in the text.

    Parameters
    ----------
    delimiters : List[str]
        DESCRIPTION.
    text : str
        DESCRIPTION.

    Returns
    -------
    List[Token]
        DESCRIPTION.
    """
    tokens = []
    for delim in delimiters:
        _locations = str_location(delim, text)
        tokens.extend([Token(delim, p) for p in _locations])
    return sorted(tokens)


def group_into_sections(delim: Tuple[str], tokens: List[Token]) -> List[Token]:
    """Take a list of Tokens and assign a group.

    Each group is meant to
    assign to once piece of text that has a similar meaning. For example::

        DELIMITER1 some English text DELIMITER2 some Pali text DELIMITER3

    Some delimiters do not need to belong to a group, such as *hidden
    text* or *substitute*. But they are assigned a group anyway, because
    these delimiters still rely on the ``END_DELIMITER`` to mark the end
    of their designated text.

    Parameters
    ----------
    delimiters : Tuple[str]
        A list of unique tokens (specified by user)
        used to label parts of the text.
    tokens : List[Token]
        List of the token and its position in the text.

    Returns
    -------
    tokens : List[Token]
        List of the token and its position in the text after being
        assigned a ``group_id``
    """
    istart = 0
    # go through the whole list of tokens
    group_id = 0
    while istart < len(tokens):
        if tokens[istart].str in delim[:-1]:    # start delimiter
            used_tokens = [tokens[istart]]
            for iend, tt in enumerate(tokens[istart + 1:]):
                if tt in used_tokens:    # something wrong, repeated token
                    istart += iend
                    break
                if tt.str == delim[-1]:    # end delimiter
                    for t_ix in range(istart, iend + istart + 2):
                        tokens[t_ix].group_id = group_id
                    group_id += 1
                    istart += iend + 1
                    break
                used_tokens.append(tt)
        istart += 1
    return tokens


def read_yaml_string(yaml_text: str) -> Dict:
    """Decode the ``yaml_text`` according to a schema.

    Parameters
    ----------
    yaml_text : str
        The text read from a ``.yml`` file.
    
    Returns
    -------
    TypedDict
        settings dict.
    """
    YK = Yaml_keywords()
    schema = sy.Map({
        sy.Optional(YK.markup_language): sy.Str(),
        YK.delimiters: sy.MapPattern(sy.Str(), sy.Any(), minimum_keys=2),
        YK.end_delimiter: sy.Str(),
        sy.Optional(YK.inline_markup): sy.MapPattern(sy.Str(), sy.Any()),
        sy.Optional(YK.hide): sy.UniqueSeq(sy.Str()),
        sy.Optional(YK.tooltip): sy.UniqueSeq(sy.Str()),
        sy.Optional(YK.exclude_db): sy.UniqueSeq(sy.Str()),
        sy.Optional(YK.substitute): sy.MapPattern(sy.Str(), sy.Any())
    })
    return sy.load(yaml_text, schema).data


def get_settings(yaml_text: str) -> Setting:
    """Decode the yaml string into a dict of class `Delim`.

    Examples yml file:

    .. literalinclude:: ../tests/palitype_instr_1.yml
      :language: yaml

    Parameters
    ----------
    filename : str
    directory : str

    Returns
    -------
    Dict
    """
    
    yaml_settings = read_yaml_string(yaml_text)
    text_settings = Setting(yaml_settings)

    return text_settings


def markup_substitution(settings: Setting, delim_positions: List[Token],
                        text: str) -> Tuple[str, Mod_counter]:
    """Take the palitype and replace with rst equivalent.

    Replaces the pali type instructions to produce a standard rst output.
    1.  Finds the text affected by the mark-up element.
    2.  Replace it with the standard markup of something like restructuredText.
    """
    delim_dict = settings.delim_dict
    positions = sorted(delim_positions)
    mod = Mod_counter()
    _text = [text[:positions[0].p.start]]    # text up to first delim
    mod.inc('untouched')
    verse_markup = ''
    for _this, _next in pairwise(positions):
        _line = delim_dict[_this.str].get_modified_lines(
            text[_this.p.end:_next.p.start], mod)
        if _line == '':
            continue

        if settings.verse_line_markup:
            if delim_dict[_next.str].tag == "verse":
                # start of group that contains a verse
                verse_markup = settings.verse_line_markup
            elif verse_markup and (_this.group_id != _next.group_id):
                verse_markup = ''
            elif verse_markup and delim_dict[_this.str].tag != "verse":

                _line_by_line = _line.splitlines()
                _line = '\n'.join([
                    a_line.replace(a_line.strip(),
                                   verse_markup + a_line.strip())
                    for a_line in _line_by_line
                ])
        _text.append(_line)
    # add section after the last delimiter
    _text.append(text[_next.p.end:])
    mod.inc('untouched')
    _complete = ''.join(_text)
    return _complete, mod


def palilex(files: List[str]):
    """Read files and formats them.

    Parameters
    ----------
    files : List[str]
        List of input files returned from the argument list

    Returns
    -------
    None.
    """
    for infile in files:
        p = pathlib.Path(infile)
        input_text = p.read_text()
        (firstline, text) = input_text.split('\n', maxsplit=1)
        instr_filename = firstline.partition(':: ')[2]
        if instr_filename == '':
            raise Exception("No instruction filename in file.")
        yaml_text = (p.parent / instr_filename).read_text()
        settings = get_settings(yaml_text)
        delims = cast(Tuple[str],list(settings.delim_dict.keys()))
        mod_text, mod = markup_substitution(
            settings,
            group_into_sections(delims, delimiter_locations(delims, text)),
            text) 
        for k, v in mod.__dict__.items():
            if k == 'last_change':
                continue
            print(f"number of {k} sections is {v}")
        pathlib.Path(infile + '.rst').write_text(mod_text)
        return


def main():
    """Start the pre-formatting.

    Returns
    -------
    None.
    """
    parser = argparse.ArgumentParser(description='Markup a text file.')
    parser.add_argument('infile',
                        metavar='in_filename',
                        type=str,
                        nargs='+',
                        help='filename of input text')
    args = parser.parse_args()
    palilex(args.infile)


if __name__ == "__main__":

    main()
