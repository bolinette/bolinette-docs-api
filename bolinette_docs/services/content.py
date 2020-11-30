from bolinette import core, blnt
from bolinette.decorators import service
from bs4 import BeautifulSoup

from bolinette_docs.models import Article


@service('content')
class ContentService(core.Service):
    def __init__(self, context: 'blnt.BolinetteContext'):
        super().__init__(context)
        self._sections = {
            'h1': 0,
            'h2': 1
        }

    async def delete_all_from_article(self, article: Article):
        if getattr(article, 'anchors', None) is None:
            return
        for content in article.anchors:
            await self.delete(content)

    async def parse_article_toc(self, article: Article):
        soup = BeautifulSoup(article.content, features="html.parser")
        position = 0
        last = []
        for section in soup:
            if section.name not in self._sections:
                continue
            content = await self.create({
                'name': section.name,
                'parent': None,
                'article': article,
                'position': position
            })
            while len(last) > 0 and self._sections[section.name] <= self._sections[last[-1].name]:
                last.pop()
            if len(last) > 0:
                content.parent = last[-1]
            last.append(content)
            position += 1
