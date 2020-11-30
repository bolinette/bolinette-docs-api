import asyncio
import tarfile

import requests
import yaml
from bolinette import core, blnt
from bolinette.exceptions import UnprocessableEntityError
from bolinette.decorators import service
from bolinette.utils import paths

from bolinette_docs.models import Version
from bolinette_docs.services import VersionService, ArticleService


@service('github')
class GitHubHooksService(core.Service):
    def __init__(self, context: 'blnt.BolinetteContext'):
        super().__init__(context)

    @property
    def version_service(self) -> VersionService:
        return self.context.service('version')

    @property
    def article_service(self) -> ArticleService:
        return self.context.service('article')

    async def process_release(self, release, action):
        if 'tag_name' not in release:
            raise UnprocessableEntityError('github.release.no_tag_name')
        if action in ['released']:
            version = await self.version_service.get_first_by('tag', release['tag_name'], safe=True)
            if version is None:
                version = await self.version_service.create({
                    'tag': release['tag_name'],
                    'released': not release.get('prerelease', False),
                    'built': False
                })
            version.built = False
            asyncio.create_task(self.create_release(version))

    async def create_release(self, version: Version):
        try:
            async with blnt.Transaction(self.context):
                tmp_dir = self.context.instance_path('tmp')
                await self._download_and_extract(version, tmp_dir)
                await self._process_docs(version, tmp_dir)
                version.built = True
        finally:
            paths.rm_r(tmp_dir)

    async def _download_and_extract(self, version: Version, path: str):
        if not paths.exists(path):
            paths.mkdir(path)
        with open(paths.join(path, 'archive.tar.gz'), 'wb') as archive:
            response = requests.get(blnt.init['archive_url'].replace('{tag}', version.tag))
            archive.write(response.content)
        with tarfile.open(paths.join(path, 'archive.tar.gz'), 'r:gz') as archive:
            archive.extractall(path)

    async def _process_docs(self, version: Version, path: str):
        app_path = paths.join(path, blnt.init['project_name'].replace('{version}', version.tag), 'docs')
        if not paths.exists(app_path):
            return
        with open(paths.join(app_path, 'docs.yaml'), 'r') as doc_config:
            config = yaml.safe_load(doc_config)
        await self.article_service.parse_toc(version, config.get('toc', []), app_path)
