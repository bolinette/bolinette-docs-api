from bolinette import core, types
from bolinette.decorators import model


@model('version')
class Version(core.Model):
    id = types.defs.Column(types.db.Integer, primary_key=True)
    name = types.defs.Column(types.db.String, nullable=False)
