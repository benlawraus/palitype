from typing import Dict

from .constants import YamlKeywords
import strictyaml as sy

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
    _yk = YamlKeywords()
    schema = sy.Map({
        sy.Optional(_yk.markup_language):
        sy.Str(),
        _yk.delimiters:
        sy.MapPattern(sy.Str(), sy.Any(), minimum_keys=2),
        _yk.end_delimiter:
        sy.Str(),
        sy.Optional(_yk.inline_markup):
        sy.MapPattern(sy.Str(), sy.Any()),
        sy.Optional(_yk.hide):
        sy.UniqueSeq(sy.Str()),
        sy.Optional(_yk.tooltip):
        sy.UniqueSeq(sy.Str()),
        sy.Optional(_yk.exclude_db):
        sy.UniqueSeq(sy.Str()),
        sy.Optional(_yk.substitute):
        sy.MapPattern(sy.Str(), sy.Any()),
        sy.Optional(_yk.indentations):
        sy.Int()
    })
    return sy.load(yaml_text, schema).data