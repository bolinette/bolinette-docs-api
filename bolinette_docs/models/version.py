from bolinette import core, types
from bolinette.decorators import model


@model('version')
class Version(core.Model):
    id = types.defs.Column(types.db.Integer, primary_key=True)
    tag = types.defs.Column(types.db.String, nullable=False)
    released = types.defs.Column(types.db.Boolean, nullable=False)
    built = types.defs.Column(types.db.Boolean, nullable=False)
