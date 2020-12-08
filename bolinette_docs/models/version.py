from typing import List, Any

from bolinette import core, types, mapping
from bolinette.decorators import model


@model('version')
class Version(core.Model):
    id = types.defs.Column(types.db.Integer, primary_key=True)
    tag = types.defs.Column(types.db.String, nullable=False)
    released = types.defs.Column(types.db.Boolean, nullable=False)
    built = types.defs.Column(types.db.Boolean, nullable=False)

    @classmethod
    def responses(cls):
        base: List[Any] = [
            mapping.Column(cls.tag)
        ]
        yield base
        yield 'complete', base + [
            mapping.List(mapping.Definition('article', 'toc'), key='articles')
        ]
