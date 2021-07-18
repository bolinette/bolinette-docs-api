from bolinette import web
from bolinette.decorators import controller, post

from bolinette_docs.services.providers import GitHubHooksService


@controller('github', '/webhooks/github')
class GitHubHooksController(web.Controller):
    @property
    def github_service(self) -> GitHubHooksService:
        return self.context.service('github')

    @post('/release', middlewares=['github-signature'])
    async def github_webhook(self, payload):
        if 'release' in payload and 'action' in payload:
            await self.github_service.process_release(payload['release'], payload['action'])
        return self.response.ok()
