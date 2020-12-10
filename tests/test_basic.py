#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Wed Oct 28 05:21:08 2020.

@author: ben
"""
import pytest
import logging
import pathlib
import context
from palitype.txt_files \
    import build_path, read_file, read_grammar, write_file, readfile
from palitype.strings import camel_to_snake
from palitype.palilex import delimiter_locations
from palitype.palilex import group_into_sections, get_settings
from palitype.db_ref import populate_sections
from palitype.palilex import markup_substitution
from palitype.classes import Delim, Mod_counter
#import lark
#lark.logger.setLevel(logging.DEBUG)
import re
from hypothesis import given
import hypothesis.strategies as st
d = context.set_path()
log_fn = d / 'tests' / 'error.log'
logging.basicConfig(filename=log_fn, level=logging.DEBUG, filemode='w')


# ONLY APPEND NEW TEXT TO THE END OTHERWISE EXISTING TESTS WILL FAIL!!!
# ONLY APPEND NEW TEXT TO THE END OTHERWISE EXISTING TESTS WILL FAIL!!!
def get_pali_shorthand(file_nr: int = 0):
    """Example text.

    Notes:
        1. extra '{' before 'striving' that has no '}'
    """
    _l = (('{', '=', '}'), read_file(f"input_text_{file_nr}.txt", 'tests'))
    return _l


def test_write_read_file():
    filename = "test.txt"
    dir_name = pathlib.Path(__file__).parent
    delimiters, text = get_pali_shorthand()
    nr_char = write_file(text, filename, dir_name)
    fn = build_path(filename, dir_name)
    assert nr_char == len(text) and fn.is_file()
    file_text = read_file(filename, dir_name)
    logging.info('test')
    assert file_text[0] == text[0]
    fn.unlink()
    assert not fn.is_file()

    grammar = read_grammar('restructuredtext.grammar')
    assert grammar[0] == '/'


def test_camel_to_snake():
    """
    Tests:
        Changing camel style strings to snake-style strings.
    """
    test_str = "sectionElement"
    assert camel_to_snake(test_str) == "section_element"
    assert test_str == "sectionElement"
    test_str = "SectionElement"
    assert camel_to_snake(test_str) == "Section_element"
    grammar = read_grammar('restructuredtext.grammar')
    new_grammar = camel_to_snake(grammar)
    assert re.search('comment_line', new_grammar)
    assert re.search('Line_break', new_grammar)


def test_group_sections():
    delimiters, text = get_pali_shorthand()
    delims = delimiter_locations(delimiters, text)
    delims = group_into_sections(delimiters, delims)
    assert len(delims) > 0
    counter = -1
    for token in delims:
        if token.str == delimiters[-1]:    # end delimiter
            counter += 1
            assert token.group_id == counter
    assert counter > -1


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


@pytest.mark.parametrize('filename, directory',
                         [('palitype_instr_0.yml', 'tests')])
def test_settings(filename, directory):
    yaml_text = read_file(filename, directory)
    delim_dict = get_settings(yaml_text).delim_dict
    assert delim_dict['==.'].tag == "Pali"


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
    english = next(
        e for e in elements[eix] if delim_dict[e.token.str].tag == "English")
    pali = next(
        e for e in elements[eix] if delim_dict[e.token.str].tag == "Pali")
    assert english.text == eng
    assert pali.text == pli


@pytest.mark.parametrize(
    'text, text_to_markup, finished_text, tok',
    [("""Appatiṭṭhaṃ khvāhaṃ anāyūhaṃ
[#āyūhaṃ] ogham atari ti.""", """anāyūhaṃ
[#āyūhaṃ]_ ogham atari""", """Appatiṭṭhaṃ khvāhaṃ anāyūhaṃ
[#āyūhaṃ] ogham atari ti.""", '*'),
     ("""e=By not reaching out, is the flood crossed.
      p=Appatiṭṭhaṃ khvāhaṃ anāyūhaṃ [#āyūhaṃ]_ ogham atari.=.i=SN1.1.1
      e=By not reaching out, is the flood crossed.""",
      """Appatiṭṭhaṃ khvāhaṃ anāyūhaṃ [#āyūhaṃ]_ ogham atari.""",
      """e=By not reaching out, is the flood crossed.
      p=*Appatiṭṭhaṃ khvāhaṃ anāyūhaṃ [#āyūhaṃ]_ ogham atari.*=.i=SN1.1.1
      e=By not reaching out, is the flood crossed.""", '*')])
def test_surround(text, text_to_markup, finished_text, tok):

    istart = text.find(text_to_markup)
    iend = istart + len(text_to_markup)
    mu = Delim.surround(tok, text[istart:iend])
    mod_text = '\n'.join(mu)
    print(mu, istart, iend)
    assert text.replace(text[istart:iend], mod_text) == finished_text


d = {
    "token": "p=",
    "tag": "Pali",
    "inline_markup": "*",
    "hide": False,
    "tooltip": False,
    "exclude_db": False,
    "substitute": ".. class m-noindent"
}
phrase_pattern = re.compile(r"[^\s]+[ \w]+[^\s]+")
white_space_pattern = re.compile(r" +")


@given(st.from_regex(white_space_pattern, fullmatch=True),
       st.lists(st.from_regex(phrase_pattern, fullmatch=True), min_size=1),
       st.from_regex(white_space_pattern, fullmatch=True))
def test_delim_modify_lines(start_whitesp, phrases, end_whitesp):
    delim = Delim(*list(d.values()))
    delim.substitute = ''
    m = delim.inline_markup
    _a = start_whitesp + '\n'.join([m + p + m for p in phrases]) + end_whitesp
    answer = _a.splitlines()
    test_text = start_whitesp + '\n'.join(phrases) + end_whitesp
    mod = Mod_counter()
    mod_text = delim.get_modified_lines(test_text, mod)
    for ix, a in enumerate(answer):
        assert mod_text[ix] == a
    assert mod.inline_markup == 1


@pytest.mark.parametrize('filename, directory, nr_pali',
                         [('palitype_instr_1.yml', 'tests', 3),
                          ('palitype_instr_0.yml', 'tests', 7)])
def test_inline_markup(filename, directory, nr_pali):
    yaml_text = read_file(filename, directory)
    settings = get_settings(yaml_text)
    delim_dict = settings.delim_dict
    _, text = get_pali_shorthand()
    delims = list(delim_dict.keys())
    d = delimiter_locations(delims, text)
    group_into_sections(delims, d)
    mod_text, mod = markup_substitution(settings, d, text)
    assert mod.inline_markup == nr_pali


@pytest.mark.parametrize('filename, directory', [
    ('input_text_0.txt', 'tests'),
])
def test_newlines(filename, directory):
    t, n = readfile(filename, directory)
    assert True


@pytest.mark.parametrize('filename, directory, sub_ix_1',
                         [('palitype_instr_1.yml', 'tests', 1033)])
def test_substitute(filename, directory, sub_ix_1):
    yaml_text = read_file(filename, directory)
    settings = get_settings(yaml_text)
    delim_dict = settings.delim_dict
    assert delim_dict
    _, text = get_pali_shorthand(1)
    delims = list(delim_dict.keys())

    d = group_into_sections(delims, delimiter_locations(delims, text))
    mod_text, mod = markup_substitution(settings, d, text)
    sub_text = next(delim_dict[ix]
                    for ix in delim_dict.keys()
                    if delim_dict[ix].tag == "verse").substitute

    assert mod_text.find(sub_text) == sub_ix_1
