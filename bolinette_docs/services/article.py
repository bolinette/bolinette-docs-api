from typing import List, Any, Dict, TextIO

import markdown
from bolinette import core, blnt
from bolinette.decorators import service
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
                article = await self.create({
                    'name': name,
                    'position': position,
                    'lang': blnt.init['default_lang'],
                    'content': self._read_markdown(f),
                    'version': version
                })
            await self.content_service.parse_article_toc(article)
            for lang in elem.get('languages', []):
                with open(paths.join(path, elem.get('path', ''), f'{name}.{lang}.md')) as f:
                    article = await self.create({
                        'name': name,
                        'position': position,
                        'lang': lang,
                        'content': self._read_markdown(f),
                        'version': version
                    })
                await self.content_service.parse_article_toc(article)
            position += 1

    def _read_markdown(self, file: TextIO):
        return markdown.markdown(file.read(), extensions=['fenced_code'])
