# -*- coding: utf-8 -*-
import pytest
import logging
import pathlib
import context
from typing import List, TypedDict
from palitype.txt_files \
    import build_path, read_file, read_grammar, write_file, readfile
from palitype.strings import camel_to_snake
from palitype.palilex import delimiter_locations
from palitype.palilex import group_into_sections, get_settings
from palitype.db_ref import populate_sections
from palitype.palilex import markup_substitution
from palitype.classes import Delim, ModCounter
from palitype.constants import END_DELIMITER, Delimiter
from test_basic import get_pali_shorthand
#import lark
#lark.logger.setLevel(logging.DEBUG)
import re
from hypothesis import given
import hypothesis.strategies as st
d = context.set_path()
log_fn = d / 'tests' / 'error.log'
logging.basicConfig(filename=log_fn, level=logging.DEBUG, filemode='w')


@pytest.mark.skip(reason="not finished")
@pytest.mark.parametrize('text_ix, element_ix, delim_ix, quote',
                         [(0, 0, 0, '[ Cross the flood '),
                          (0, 2, 1, '''
Appatiṭṭhaṃ khvāhaṃ anāyūhaṃ [#āyūhaṃ]_ ogham atari.
'''), (0, 4, 1, 'āyūhaṃ')])
def test_populate_sections(text_ix, element_ix, delim_ix, quote):
    delimiters, text = get_pali_shorthand()
    d = group_into_sections(delimiters, delimiter_locations(delimiters, text))
    elements = populate_sections(d, text)

    assert elements[element_ix][delim_ix].text == quote
    assert elements[element_ix][delim_ix].token.str == delimiters[delim_ix]


@pytest.mark.skip(reason="not finished")
@pytest.mark.parametrize('filename, directory, eng, pli, eix', [
    ('palitype_instr_0.yml', 'tests', "[ Cross the flood ", " Ogha taraṇa ]",
     0),
    ('palitype_instr_0.yml', 'tests', """
By not standing (on the bottom), by not reaching out, is the flood crossed.""",
     """
Appatiṭṭhaṃ khvāhaṃ anāyūhaṃ [#āyūhaṃ]_ ogham atari.
""", 2),
    ('palitype_instr_1.yml', 'tests',
     "By not reaching out, is the flood crossed.\n",
     "Appatiṭṭhaṃ khvāhaṃ anāyūhaṃ [#āyūhaṃ]_ ogham atari.", 0),
    ('palitype_instr_1.yml', 'tests',
     "By not reaching out, is the flood crossed.",
     """Appatiṭṭhaṃ khvāhaṃ anāyūhaṃ
[#āyūhaṃ]_ ogham atari.""", 1),
])
def test_populate(filename, directory, eng, pli, eix):
    yaml_text = read_file(filename, directory)
    settings = get_settings(yaml_text)
    delim_dict = settings.get('delim_dict')
    _, text = get_pali_shorthand()
    delims = list(delim_dict.keys())

    d = group_into_sections(delims, delimiter_locations(delims, text))
    elements = populate_sections(d, text)
    english = next(e for e in elements[eix]
                   if delim_dict[e.token.str].tag == "English")
    pali = next(e for e in elements[eix]
                if delim_dict[e.token.str].tag == "Pali")
    assert english.text == eng
    assert pali.text == pli
