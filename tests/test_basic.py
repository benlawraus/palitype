# -*- coding: utf-8 -*-
"""Created on Wed Oct 28 05:21:08 2020.

@author: ben
"""
import pytest
import logging
import pathlib
import context
from dataclasses import asdict
from typing import List, Dict, Tuple
from palitype.txt_files \
    import build_path, read_file, read_grammar, write_file, readfile
from palitype.strings import camel_to_snake
from palitype.palilex import delimiter_locations
from palitype.palilex import group_into_sections, get_settings
from palitype.db_ref import populate_sections
from palitype.palilex import markup_substitution
from palitype.classes import Delim, Mod_counter, Setting
from palitype.constants import VERSE_DELIM

#import lark
#lark.logger.setLevel(logging.DEBUG)
import re
from hypothesis import given
import hypothesis.strategies as st
d = context.set_path()
log_fn = d / 'tests' / 'error.log'
logging.basicConfig(filename=log_fn, level=logging.DEBUG, filemode='w')


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


def group_id_loop(delims, tokens):
    counter = -1
    for token in delims:
        if token.str == tokens[-1]:  # end delimiter
            counter += 1
            assert token.group_id == counter
    assert counter > -1


def test_group_sections():
    delimiters, text = get_pali_shorthand()
    delims = delimiter_locations(delimiters, text)
    delims = group_into_sections(delimiters, delims)
    assert len(delims) > 0
    group_id_loop(delims, delimiters)


@pytest.mark.parametrize('filename, directory',
                         [('palitype_instr_0.yml', 'tests')])
def test_settings(filename, directory):
    yaml_text = read_file(filename, directory)
    delim_dict = get_settings(yaml_text).delim_dict
    assert delim_dict['==.'].tag == "Pali"


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
    print(mu, istart, iend)
    assert text.replace(text[istart:iend], mu) == finished_text


def verse_line(start_whitesp: str,
               phrases: List[str],
               end_whitesp: str,
               m: str = '',
               verse: str = '') -> str:

    return '\n'.join(
        [verse + start_whitesp + m + p + m + end_whitesp for p in phrases])


def make_verse(start_whitesp: str,
               phrases: List[str],
               end_whitesp: str,
               m: str = '',
               verse: str = '') -> Tuple[str, str]:
    """Make a verse and its corresponding marked-up version.

    Parameters
    ----------
    start_whitesp : str
    phrases : List[str]
    end_whitesp : str
    m : str
        The token for inline markup.

    Returns
    -------
    test_text : str
        Original text.
    answer : str
        Marked-up version
    """

    answer = verse_line(start_whitesp, phrases, end_whitesp, m=m, verse=verse)
    test_text = verse_line(start_whitesp, phrases, end_whitesp)
    return test_text, answer


def verse_n_lang(delims: Dict[str, Delim],
                 start_whitesp: str,
                 phrases: List[str],
                 end_whitesp: str,
                 verse: str = '') -> Tuple[str, str]:
    orig_tot = []
    marked_tot = []
    for delim in list(delims.values())[:-1]:
        orig, marked = make_verse(start_whitesp,
                                  phrases,
                                  end_whitesp,
                                  m=delim.inline_markup,
                                  verse=verse)
        orig_tot.append(delim.token + orig)
        marked_tot.append(marked)
    orig_tot.append(delims[list(delims.keys())[-1]].token)

    return '\n'.join(orig_tot), '\n'.join(marked_tot)


INLINE_MARKUP = '*'


def make_delims(nr_lang: int) -> Dict[str, Delim]:
    """Make `nr_lang` delims plus verse delimiter and end delimiter.

    The first delimiter is the verse delimiter.
    The second last delimiter has inline markup '*'.
    The last delimiter is the end delimiter.


    Parameters
    ----------
    nr_lang : int
        Number of languages.

    Returns
    -------
    delim : Delim
        DESCRIPTION.
    """

    if nr_lang > 24:
        nr_lang = 24
    elif not nr_lang:
        nr_lang = 1
    inline_markup = [''] * (nr_lang + 2)  # extra verse and end delimiters
    inline_markup[-2] = INLINE_MARKUP  # 2nd last delimiter has inline markup
    verse_token = 'VT='
    VERSE_DELIM.token = 'VT='
    delim = {verse_token: Delim(**asdict(VERSE_DELIM))}
    for lang_ix, m in enumerate(inline_markup[1:]):
        ix_s = ord('a') + lang_ix
        token = chr(ix_s) + '='
        delim[token] = (Delim(token=token,
                              tag=''.join(
                                  [chr(i) for i in range(ix_s, ix_s + 3)]),
                              inline_markup=m))
    return delim


phrase_pattern = re.compile(r"[^\s=]+[ \w]+[^\s=]+")
white_space_pattern = re.compile(r" +")
verse_pattern = [
    st.from_regex(white_space_pattern, fullmatch=True),
    st.lists(st.from_regex(phrase_pattern, fullmatch=True), min_size=1),
    st.from_regex(white_space_pattern, fullmatch=True)
]


@given(*verse_pattern)  # type: ignore
def test_delim_modify_lines(start_whitesp, phrases, end_whitesp):
    delim = Delim()
    delim.inline_markup = '*'
    test_text, answer = make_verse(start_whitesp, phrases, end_whitesp,
                                   delim.inline_markup)
    mod = Mod_counter()
    mod_text = delim.get_modified_lines(test_text, mod)
    assert mod_text == answer
    assert getattr(mod, "inline_markup", 0) == 1


@given(*verse_pattern)  # type: ignore
def test_verse_n(start_whitesp, phrases, end_whitesp):
    settings = Setting({})
    settings.delim_dict = make_delims(2)
    next(iter(settings.delim_dict.values())).tag = 'dont add verse'
    test_text, answer = verse_n_lang(settings.delim_dict, start_whitesp,
                                     phrases, end_whitesp)
    mod = Mod_counter()

    delims = list(settings.delim_dict.keys())
    mod_text, mod = markup_substitution(
        settings,
        group_into_sections(delims, delimiter_locations(delims, test_text)),
        test_text)
    assert mod_text == answer


def delims_1(delim_dict):
    tokens = list(delim_dict.keys())
    assert delim_dict[tokens[0]].tag == VERSE_DELIM.tag
    assert delim_dict[tokens[-2]].inline_markup == INLINE_MARKUP
    return


@given(*verse_pattern)  # type: ignore
def test_verse_markup(start_whitesp, phrases, end_whitesp):
    settings = Setting({})
    delim_dict = make_delims(2)
    delims_1(delim_dict)
    test_text, answer = verse_n_lang(delim_dict,
                                     start_whitesp,
                                     phrases,
                                     end_whitesp,
                                     verse='| ')
    mod = Mod_counter()
    settings.delim_dict = delim_dict
    delims = list(delim_dict.keys())
    delim_list = group_into_sections(delims,
                                     delimiter_locations(delims, test_text))
    group_id_loop(delim_list, delims)
    mod_text, mod = markup_substitution(settings, delim_list, test_text)
    assert mod_text == answer


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
