# -*- coding: utf-8 -*-
import re
def camel_to_snake(word:str) -> str:
    pattern = "[a-z][A-Z]"
    re_c = re.compile(pattern)
    for f in re_c.findall(word):
        new_str = ''.join((f[0],'_',f[1].lower()))
        word = re.sub(f, new_str, word)
    return word



