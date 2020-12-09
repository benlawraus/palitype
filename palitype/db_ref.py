# -*- coding: utf-8 -*-
from .palilex import Token
from typing import List
class Token_text:
    def __init__(self,token:Token, text:str):
        self.token = token
        self.text = text

    def __str__(self):
        return f"{self.token}\n{self.text}"
    def __lt__(self, other):
        return self.token < other.token

        
def get_section(elements:List[Token], text:str)->List[Token_text]:
    """
    A list of Token_text within text needed to associate one piece of
    text to another piece of text, e.g. English=Pali
    
    The End delimiter
    is mandatory, but the internal delimiters are optional.
    
    A mark-up element marks two or more sections of
    text together. An example would be where the first section is English and
    the second section is in the language of Pali. The pali would correspond 
    to the english part.
    e.g.
    DELIMITER1 some English text DELIMITER2 some Pali text DELIMITER3

    For three equivalent languages, e.g. English Pali and Sanskrit
    DELIMITER1 English DELIMITER2 Pali DELIMITER3 Sanskrit DELIMITER4    

    Parameters
    ----------
    element : List[Token]
        DESCRIPTION.
    text : str
        DESCRIPTION.

    Returns
    -------
    List[Token_text]
        DESCRIPTION.

    """
    _t = [Token_text(e, text[e.p.end : elements[ix+1].p.start]) \
            for ix,e in enumerate(elements[:-1])]
    _t.append(Token_text(elements[-1],''))  # end delimiter
    return _t
            
def populate_sections(sections:List[List[Token]], text:str)\
        -> List[List[Token_text]]:
    return [get_section(section, text) for section in sections]

