from bolinette import core, blnt
from bolinette.decorators import service


@service('github')
class GitHubHooksService(core.Service):
    def __init__(self, context: 'blnt.BolinetteContext'):
        super().__init__(context)

    async def create_release(self, repo, tag, action):
        pass
