# -*- coding: utf-8 -*-
"""
Define the tables of the DAL object.
"""
from pydal import Field
#from pydal.validators import *


def define_tables(db):
    db.define_table('pali',
                    Field('segment_id','string', required=True),
                    Field("text", "string", required=False)
                    )
    db.define_table('en',
                    Field('author_ref', 'reference auth'),
                    Field('text','string'))
    db.define_table('translate',
                    Field('en_ref', 'reference en'),
                    Field('pali_ref', 'reference pali'))
    db.commit()
    return    
    
