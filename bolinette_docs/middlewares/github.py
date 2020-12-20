import hashlib
import hmac

from bolinette import web
from bolinette.decorators import middleware
from bolinette.exceptions import ForbiddenError, UnprocessableEntityError


@middleware('github-signature', priority=5)
class GithubSignatureMiddleware(web.InternalMiddleware):
    async def handle(self, request, params, next_func):
        headers = params['headers']
        payload = await request.text()
        if not self.context.env['debug']:
            if 'X-Hub-Signature-256' not in headers:
                raise UnprocessableEntityError('github.release.not_signature_in_headers')
            signature = headers['X-Hub-Signature-256']
            secret = bytes(self.context.env['github_secret'], 'UTF-8')
            encoded_payload = bytes(payload, 'UTF-8')
            decoded_hash = 'sha256=' + hmac.new(secret, encoded_payload, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, decoded_hash):
                raise ForbiddenError('github.release.signature_not_matching')
        return await next_func(request, params)
