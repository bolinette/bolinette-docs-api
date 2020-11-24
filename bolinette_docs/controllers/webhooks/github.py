from bolinette import web
from bolinette.decorators import controller, post


@controller('github')
class GitHubHooksController(web.Controller):
    @post('/github/release')
    async def github_webhook(self, payload):
        if 'action' in payload and payload['action'] == 'published':
            pass
        return self.response.ok('OK')
