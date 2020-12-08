from bolinette import core, types, mapping
from bolinette.decorators import model


@model('content')
class Content(core.Model):
    id = types.defs.Column(types.db.Integer, primary_key=True)
    name = types.defs.Column(types.db.String, nullable=False)
    position = types.defs.Column(types.db.Integer, nullable=False)
    tag = types.defs.Column(types.db.String, nullable=False)

    article_id = types.defs.Column(types.db.Integer, nullable=False, reference=types.defs.Reference('article', 'id'))
    article = types.defs.Relationship('article', foreign_key=article_id,
                                      backref=types.defs.Backref('anchors', lazy=False), lazy=True)

    parent_id = types.defs.Column(types.db.Integer, nullable=True, reference=types.defs.Reference('content', 'id'))
    parent = types.defs.Relationship('content', remote_side=id,
                                     backref=types.defs.Backref('children', lazy=False), lazy=True)

    @classmethod
    def responses(cls):
        yield [
            mapping.Column(cls.name),
            mapping.Column(cls.tag),
            mapping.Column(cls.position),
            mapping.List(mapping.Definition('content'), key='children')
        ]
