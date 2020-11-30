import hashlib
import hmac

from bolinette import web
from bolinette.decorators import controller, post
from bolinette.exceptions import UnprocessableEntityError, ForbiddenError

from bolinette_docs.services.providers import GitHubHooksService


@controller('github', '/webhooks/github')
class GitHubHooksController(web.Controller):
    @property
    def github_service(self) -> GitHubHooksService:
        return self.context.service('github')

    @post('/release')
    async def github_webhook(self, payload, raw_payload, headers):
        if not self.context.env['debug']:
            if 'X-Hub-Signature-256' not in headers:
                raise UnprocessableEntityError('github.release.not_signature_in_headers')
            signature = headers['X-Hub-Signature-256']
            secret = bytes(self.context.env['github_secret'], 'UTF-8')
            encoded_payload = bytes(raw_payload, 'UTF-8')
            decoded_hash = 'sha256=' + hmac.new(secret, encoded_payload, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, decoded_hash):
                raise ForbiddenError('github.release.signature_not_matching')
        if 'release' in payload and 'action' in payload:
            await self.github_service.process_release(payload['release'], payload['action'])
        return self.response.ok('OK')
