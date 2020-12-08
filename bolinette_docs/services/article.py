from typing import List, Any, Dict

import markdown
from bolinette import core, blnt
from bolinette.decorators import service
from bolinette.exceptions import EntityNotFoundError
from bolinette.utils import paths

from bolinette_docs.models import Version
from bolinette_docs.services import ContentService


@service('article')
class ArticleService(core.Service):
    def __init__(self, context: 'blnt.BolinetteContext'):
        super().__init__(context)

    @property
    def content_service(self) -> ContentService:
        return self.context.service('content')

    def _read_markdown(self, content: str):
        return markdown.markdown(content, extensions=['fenced_code'])

    async def delete_all_from_version(self, version: Version):
        if getattr(version, 'articles', None) is None:
            return
        for article in version.articles:
            await self.content_service.delete_all_from_article(article)
            await self.delete(article)
        version.articles = []

    async def parse_toc(self, version: Version, toc: List[Dict[str, Any]], path: str):
        await self.delete_all_from_version(version)
        position = 0
        for elem in toc:
            name = elem['name']
            with open(paths.join(path, elem.get('path', ''), f'{name}.md')) as f:
                content = f.read()
                article = await self.create({
                    'name': name,
                    'position': position,
                    'lang': blnt.init['default_lang'],
                    'markdown': content,
                    'html': self._read_markdown(content),
                    'version': version
                })
            await self.content_service.parse_article_toc(article)
            for lang in elem.get('languages', []):
                with open(paths.join(path, elem.get('path', ''), f'{name}.{lang}.md')) as f:
                    content = f.read()
                    article = await self.create({
                        'name': name,
                        'position': position,
                        'lang': lang,
                        'markdown': content,
                        'html': self._read_markdown(content),
                        'version': version
                    })
                await self.content_service.parse_article_toc(article)
            position += 1

    async def get_by_version_and_language(self, version: Version, lang: str):
        return [a for a in version.articles if a.lang == lang]

    async def get_one(self, version: Version, lang: str, name: str):
        article = await self.repo.query().filter_by(version_id=version.id, lang=lang, name=name).first()
        if article is None:
            raise EntityNotFoundError('article', 'version,lang,name', f'{version.id},{lang},{name}')
        return article
