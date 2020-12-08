from typing import Any

from bolinette import core, types, mapping
from bolinette.decorators import model


@model('article')
class Article(core.Model):
    id = types.defs.Column(types.db.Integer, primary_key=True)
    name = types.defs.Column(types.db.String, nullable=False)
    position = types.defs.Column(types.db.Integer, nullable=False)
    lang = types.defs.Column(types.db.String, nullable=False)
    markdown = types.defs.Column(types.db.String, nullable=False)
    html = types.defs.Column(types.db.String, nullable=False)

    version_id = types.defs.Column(types.db.Integer, reference=types.defs.Reference('version', 'id'), nullable=False)
    version = types.defs.Relationship('version', foreign_key=version_id, lazy=True,
                                      backref=types.defs.Backref('articles', lazy=False))

    @staticmethod
    def _get_top_anchors(article):
        return [a for a in article.anchors if a.parent_id is None]

    @classmethod
    def responses(cls):
        base: Any = [
            mapping.Column(cls.name),
            mapping.Column(cls.position),
            mapping.Column(cls.lang)
        ]
        yield base
        with_anchors = base + [
            mapping.List(mapping.Definition('content'), function=cls._get_top_anchors, name='anchors')
        ]
        yield 'toc', with_anchors
        yield 'complete', with_anchors + [
            mapping.Column(cls.markdown),
            mapping.Column(cls.html)
        ]
