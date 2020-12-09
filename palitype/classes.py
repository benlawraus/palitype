# -*- coding: utf-8 -*-
from dataclasses import dataclass
from . import constants as ptcon
from typing import List
from collections import namedtuple

Pair_item = namedtuple("Pair_item","start end")
Pair_delimiter_text = namedtuple("Pair_delimiter_text","delimiter text")
class Token():
    def __init__(self,s:str,p:int):
        """
        

        Parameters
        ----------
        s : str
            token.
        p : int
            location of first char of token.

        """
        self.str = s
        self.p = Pair_item(p, p+len(s))

    def __lt__(self, other):
        return self.p.start < other.p.start
    def __repr__(self):
        group_id = getattr(self, 'group_id', -1)
        return f"s:'{self.str}' start:{self.p[0]} end:{self.p[1]} g_id:{group_id}"
    def __eq__(self,other:str):
        return self.str == other
    def equals(self, other):
        return self.str == other.str and self.p == other.p

@dataclass
class Mod_counter:
    last_change = None
    
    def inc(self, key):
        self.last_change = key
        self.__setattr__(key,getattr(self, key, 0)+1)
        return

class Delim():
    """
    Class describing the yml file information of each delimiter.
    
    The class has the form of:
    
    ..  code-block:: python
    
        __dict__ = {"token":"e=", "tag":"English", "inline_markup":"*",
              "hide":False, "tooltip":False, "exclude_db":False,
            "substitute":".. class m-noindent"}
        
    """
    def __init__(self, *args):
        for ix,d in enumerate(ptcon.DELIMITER_KEYS):
            if ix<len(args):  # assign from args
                self.__setattr__(d, args[ix])
            # these require text, so make null string as default
            elif d in ["inline_markup","substitute"]: 
                self.__setattr__(d, '')
            # these are bool so default to False
            else:
                self.__setattr__(d, False)
                
        
    def __eq__(self, token:str)->bool:
        """
        Used to compare to token objec with a str.

        
        Parameters
        ----------
        token : str

        Returns
        -------
        bool
        """
        return self.token == token
    
    @staticmethod
    def surround(m:str, text:str)->str:
        """
        Modifies text to include inline_markup `m`.
        
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
                _text.append(line.replace(_l,''.join((m,_l,m))))
            else:
                _text.append(line)
        return _text

    def get_modified_lines(self, text:str, mod:Mod_counter)->List[str]:
        """
        Modifies the line by adding inline-markup or substituting or hiding.

        Parameters
        ----------
        text : str
            The string that is to be modified. Does not contain any markup.
        mod : Mod_counter
            A counter of what was modified.
    
        Returns
        -------
        List[str]
            A list of the modified text broken up into lines according to the presence of newline.
        """
        if self.inline_markup:
            # markup insertion
            _line = Delim.surround( \
                    self.inline_markup,
                    text)
            mod.inc('inline_markup')
        elif self.substitute:    
            _line = [self.substitute \
                + text]
            mod.inc('substitute')
        elif self.hide:
            mod.inc('hide')
            return None
        else:
            _line = [text]
            mod.inc('untouched')
        return _line

        

