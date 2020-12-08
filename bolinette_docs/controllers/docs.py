from bolinette import web
from bolinette.decorators import controller, get

from bolinette_docs.services import VersionService, ArticleService


@controller('docs', service_name='article')
class DocsController(web.Controller):
    @property
    def version_service(self) -> VersionService:
        return self.context.service('version')

    @property
    def article_service(self) -> ArticleService:
        return self.context.service('article')

    @get('', returns=web.Returns('version', 'complete'))
    @get('/v/{version}', returns=web.Returns('version', 'complete'))
    async def get_all_articles(self, match):
        version_name = match.get('version', None)
        if version_name is not None:
            version = await self.version_service.get_first_by_tag(version_name)
        else:
            version = await self.version_service.get_latest()
        return self.response.ok('OK', version)

    @get('/a/{lang}/{version}/{name}', returns=web.Returns('article', 'complete'))
    async def get_article(self, match):
        lang = match['lang']
        version_name = match['version']
        article_name = match['name']
        version = await self.version_service.get_first_by_tag(version_name)
        article = await self.article_service.get_one(version, lang, article_name)
        return self.response.ok('OK', article)
