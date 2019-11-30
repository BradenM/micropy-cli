# -*- coding: utf-8 -*-

import json

import pytest

from micropy import config


class TestConfig:

    default = {
        "one": 1,
        "two": 2,
        "sub": {
            "items": ["foo", "bar"],
            "bool": True
        }
    }

    @pytest.fixture
    def test_config(self, tmp_path):
        cfg_file = tmp_path / 'conf.json'
        conf = config.Config(cfg_file, default=self.default)
        return conf

    def get_file_data(self, conf):
        path = conf.source.file_path
        return json.loads(path.read_text())

    def test_default(self, tmp_path):
        cfg_file = tmp_path / 'conf.json'
        conf = config.Config(cfg_file, default=self.default)
        assert cfg_file.exists()
        assert self.get_file_data(conf) == conf.config

    def test_override(self, test_config, tmp_path):
        conf = test_config
        conf.config = {'one': 1}
        assert self.get_file_data(conf) == {'one': 1}
        assert conf.source == conf._source
        assert conf.config == conf.source.config
        new_cfg = tmp_path / 'newcfg.json'
        conf.source = new_cfg
        assert isinstance(conf.source, config.JSONConfigSource)
        diff_cfg = tmp_path / 'diffcfg.json'
        conf.source.file_path = diff_cfg
        conf.sync()
        assert self.get_file_data(conf) == conf.config

    def test_get(self, test_config):
        conf = test_config
        assert conf.get('one') == 1
        assert conf.get('sub.bool')
        assert conf.get('sub.items.0') == "foo"
        assert conf.get('sub.items') == ["foo", "bar"]

    def test_set(self, test_config):
        conf = test_config
        conf.set('one', 1)
        conf.set('one.sub.items.0', "foobar")
        data = json.loads(conf.source.file_path.read_text())
        assert data == conf.config

    def test_should_sync(self, tmp_path):
        cfg_file = tmp_path / 'conf.json'
        conf = config.Config(cfg_file, default=self.default, should_sync=lambda *args: False)
        assert not cfg_file.exists()
        conf.set('one', 45)
        assert not cfg_file.exists()

    def test_update_from_file(self, test_config):
        conf = test_config
        cfg_file = conf.source.file_path
        new = self.default.copy()
        new['one'] = 45
        new['section'] = {'value': 'foo'}
        cfg_file.write_text(json.dumps(new))
        conf = config.Config(cfg_file, default=self.default)
        assert conf.get('one') == 45
        assert conf.get('section.value') == 'foo'
        assert conf.config == new

    def test_merge(self, test_config):
        conf = test_config
        new_data = {
            'section': {
                'foo': 45
            }
        }
        conf.merge(new_data)
        file_data = json.loads(conf.source.file_path.read_text())
        print(file_data)
        assert file_data['section']['foo'] == 45
        assert conf.get('section.foo') == 45
