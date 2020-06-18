import unittest
from gordian.config import Config
from gordian.gordian import apply_transformations
from unittest.mock import MagicMock, patch, call, Mock, ANY


class TestGordian(unittest.TestCase):

    class Args(object):
        def __init__(self, config_file='./tests/fixtures/test_config.yaml', dry_run = False):
            self.config_file = config_file
            self.major = False
            self.minor = False
            self.patch = False
            self.dry_run = dry_run
            self.pr_message = 'test'
            self.branch = 'test'
            self.github_api = None
            self.semver_label = None
            self.target_branch = 'master'
            self.pr_labels = 'test'

    def test_apply_transformations_without_changes(self):
        with patch('gordian.gordian.Repo') as RepoMock, patch('gordian.transformations.Transformation') as TransformationMockClass:
            instance = RepoMock.return_value
            instance.dirty = False
            apply_transformations(TestGordian.Args(), [TransformationMockClass])
            RepoMock.assert_has_calls([
                call('testOrg/TestService1', github_api_url=None, branch='test', semver_label=None, target_branch='master'),
                call('testOrg/TestService2', github_api_url=None, branch='test', semver_label=None, target_branch='master')
                ])

    def test_apply_transformations_with_changes(self):
        with patch('gordian.gordian.Repo') as RepoMock, patch('gordian.transformations.Transformation', ) as TransformationMockClass:
            instance = RepoMock.return_value
            instance.dirty = True
            apply_transformations(TestGordian.Args(), [TransformationMockClass])
            RepoMock.assert_has_calls([call().bump_version(False), call().bump_version(False)], any_order=True)
            RepoMock.assert_has_calls([call()._repo.create_pull('test', '', 'master', ANY), call()._repo.create_pull('test', '', 'master', ANY)], any_order=True)

    def test_apply_transformations_with_changes_dry_run(self):
        with patch('gordian.gordian.Repo') as RepoMock, patch('gordian.transformations.Transformation', ) as TransformationMockClass:
            instance = RepoMock.return_value
            instance.dirty = True
            apply_transformations(TestGordian.Args(dry_run=True), [TransformationMockClass])
            RepoMock.assert_has_calls([call().bump_version(True), call().bump_version(True)], any_order=True)
            self.assertNotIn(call().repo.create_pull('test', '', 'master', ANY), RepoMock.mock_calls)

    def test_apply_transformations_with_changes_and_callback(self):
        with patch('gordian.gordian.Repo') as RepoMock, patch('gordian.transformations.Transformation', ) as TransformationMockClass:
            instance = RepoMock.return_value
            instance.dirty = True
            callback_mock = MagicMock()
            args = TestGordian.Args()
            args.target_branch = 'target_branch'
            apply_transformations(args, [TransformationMockClass], callback_mock)
            pull_request = RepoMock.return_value._repo.create_pull.return_value
            RepoMock.assert_has_calls([call().bump_version(False), call().bump_version(False)], any_order=True)
            RepoMock.assert_has_calls([
                call()._repo.create_pull('test', '', 'target_branch', ANY),
                call()._repo.create_pull('test', '', 'target_branch', ANY)],
                any_order=True)
            callback_mock.assert_has_calls([
                call('testOrg/TestService1', pull_request),
                call('testOrg/TestService2', pull_request)]
                )
