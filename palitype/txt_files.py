#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Wed Oct 28 05:22:11 2020.

@author: ben
"""
import pathlib


def build_path(filename, directory='source') -> pathlib.Path:
    root = pathlib.Path.cwd() / directory / filename
    return root


def write_file(text: str, filename: str, directory='source'):
    fn = build_path(filename, directory)
    return fn.write_text(text)


def read_file(filename: str, directory='source'):
    fn = build_path(filename, directory)
    return fn.read_text()


def read_grammar(filename='palitype.grammar'):
    return (pathlib.Path(__file__).parent / 'grammar' / filename).read_text()


def readfile(filename: str, directory: str = 'source'):
    """Reads a file and outputs the text and an array of newline characters
    used at the end of each line.

    Parameters
    ----------
    filename : str
    directory : str, optional
        Directory of the file. The default is 'source'.

    Returns
    -------
    text : TYPE
        DESCRIPTION.
    n : TYPE
        DESCRIPTION.
    """
    fn = build_path(filename, directory)
    n = []
    with fn.open("r") as f:
        lines = f.readlines()
        text = ''.join(lines)  #list(f))
        n.extend(f.newlines)
        """
        line = f.readline()
        text = line
        while line:
            line = f.readline()
            text = ''.join((text,line))
            n.append(f.newlines)
        """
    return text, n
