from bolinette import core, types
from bolinette.decorators import model


@model('article')
class Article(core.Model):
    id = types.defs.Column(types.db.Integer, primary_key=True)
    name = types.defs.Column(types.db.String, nullable=False)
    position = types.defs.Column(types.db.Integer, nullable=False)
    lang = types.defs.Column(types.db.String, nullable=False)
    content = types.defs.Column(types.db.String, nullable=False)

    version_id = types.defs.Column(types.db.Integer, reference=types.defs.Reference('version', 'id'), nullable=False)
    version = types.defs.Relationship('version', foreign_key=version_id, lazy=True,
                                      backref=types.defs.Backref('articles', lazy=False))
