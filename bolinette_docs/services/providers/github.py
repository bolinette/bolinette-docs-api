import asyncio
import os
import tarfile
from datetime import datetime

import requests
import yaml
from bolinette import core, blnt
from bolinette.exceptions import UnprocessableEntityError
from bolinette.decorators import service
from bolinette.utils import paths

from bolinette_docs.models import Version
from bolinette_docs.services import VersionService, ArticleService


@service('github')
class GitHubHooksService(core.SimpleService):
    def __init__(self, context: 'blnt.BolinetteContext'):
        super().__init__(context)

    @property
    def version_service(self) -> VersionService:
        return self.context.service('version')

    @property
    def article_service(self) -> ArticleService:
        return self.context.service('article')

    async def process_release(self, release, action):
        if action in ['released']:
            if 'tag_name' not in release or 'tarball_url' not in release:
                raise UnprocessableEntityError('github.release.no_tag_name')
            version = await self.version_service.get_first_by('tag', release['tag_name'], safe=True)
            if version is None:
                version = await self.version_service.create({
                    'tag': release['tag_name'],
                    'released': not release.get('prerelease', False),
                    'built': False,
                    'created_on': datetime.utcnow(),
                    'published_on': None
                })
            asyncio.create_task(self.create_release(version, release['tarball_url']))

    async def create_release(self, version: Version, archive_url: str):
        try:
            async with blnt.Transaction(self.context):
                tmp_dir = self.context.instance_path('tmp')
                await self._download_and_extract(tmp_dir, archive_url)
                await self._process_docs(version, tmp_dir)
                version.built = True
                version.published_on = datetime.utcnow()
        finally:
            paths.rm_r(tmp_dir)

    async def _download_and_extract(self, path: str, archive_url: str):
        if not paths.exists(path):
            paths.mkdir(path)
        with open(paths.join(path, 'archive.tar.gz'), 'wb') as archive:
            response = requests.get(archive_url)
            archive.write(response.content)
        with tarfile.open(paths.join(path, 'archive.tar.gz'), 'r:gz') as archive:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(archive, path)

    async def _process_docs(self, version: Version, path: str):
        for file in os.listdir(path):
            file_path = paths.join(path, file)
            app_path = paths.join(path, file, 'docs')
            if os.path.isdir(file_path) and paths.exists(app_path):
                with open(paths.join(app_path, 'docs.yaml'), 'r') as doc_config:
                    config = yaml.safe_load(doc_config)
                await self.article_service.parse_toc(version, config.get('toc', []), app_path)
