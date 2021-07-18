from bolinette import core, blnt
from bolinette.decorators import service


@service('version')
class VersionService(core.Service):
    def __init__(self, context: 'blnt.BolinetteContext'):
        super().__init__(context)

    async def get_first_by_tag(self, tag: str):
        return await self.get_first_by('tag', tag)

    async def get_latest(self):
        return await self.repo.query().order_by(lambda v: v.published_on, desc=True).first()
