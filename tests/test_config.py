import json

import pytest
from micropy import config


class TestConfig:

    default = {"one": 1, "two": 2, "sub": {"items": ["foo", "bar"], "bool": True}}

    @pytest.fixture
    def test_config(self, tmp_path):
        cfg_file = tmp_path / "conf.json"
        conf = config.Config(cfg_file, default=self.default)
        return conf

    def get_file_data(self, conf):
        path = conf.source.file_path
        return json.loads(path.read_text())

    def test_default(self, tmp_path):
        cfg_file = tmp_path / "conf.json"
        conf = config.Config(cfg_file, default=self.default)
        # should not create source file until first change
        assert not cfg_file.exists()
        # make change
        conf.set("one", 2)
        assert cfg_file.exists()
        assert self.get_file_data(conf) == conf.raw()

    def test_load_from_file(self, tmp_path, utils):
        cfg_file = tmp_path / "conf.json"
        cfg_file.write_text(json.dumps(self.default))
        conf = config.Config(cfg_file, default={})
        assert conf.config == self.default
        # default should be overriden
        conf = config.Config(cfg_file, default={"one": 1})
        assert utils.dict_equal(conf.raw(), self.default)

    def test_override(self, test_config, tmp_path):
        conf = test_config
        new_cfg = tmp_path / "newcfg.json"
        conf.source = new_cfg
        assert isinstance(conf.source, config.JSONConfigSource)
        diff_cfg = tmp_path / "diffcfg.json"
        conf.source.file_path = diff_cfg
        conf.sync()
        assert self.get_file_data(conf) == conf.config

    def test_get(self, test_config):
        conf = test_config
        assert conf.get("one") == 1
        assert conf.get("sub/bool")
        assert conf.get("sub/items/0") == "foo"
        assert conf.get("sub/items") == ["foo", "bar"]

    def test_set(self, test_config):
        conf = test_config
        conf.set("one", 1)
        conf.set("one/sub/items.0", "foobar")
        data = json.loads(conf.source.file_path.read_text())
        assert data == conf.config

    def test_update_from_file(self, test_config):
        conf = test_config
        cfg_file = conf.source.file_path
        new = self.default.copy()
        new["one"] = 45
        new["section"] = {"value": "foo"}
        cfg_file.write_text(json.dumps(new))
        conf = config.Config(cfg_file, default=self.default)
        assert conf.get("one") == 45
        assert conf.get("section/value") == "foo"
        assert conf.config == new

    def test_extend(self, test_config):
        conf = test_config
        conf.extend("sub/items", ["foobar", "barfoo"])
        file_data = json.loads(conf.source.file_path.read_text())
        print(file_data)
        assert file_data["sub"]["items"] == ["foo", "bar", "foobar", "barfoo"]
        assert conf.get("sub/items") == ["foo", "bar", "foobar", "barfoo"]

    def test_upsert(self, test_config):
        conf = test_config
        conf.upsert("sub/items", ["barfoo", "foobar", "bar", "foo"])
        file_data = self.get_file_data(conf)
        assert file_data["sub"]["items"] == ["barfoo", "foobar", "bar", "foo"]
        assert conf.get("sub/items") == ["barfoo", "foobar", "bar", "foo"]

    def test_dict(self):
        conf = config.Config(source_format=config.DictConfigSource, default=self.default)
        assert conf.get("one") == 1
        conf.set("sub/bool", False)
        assert not conf.get("sub/bool")
