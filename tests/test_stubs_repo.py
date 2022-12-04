import pytest


def test_repo_inits(test_repo):
    assert len(test_repo.manifests) == 2
    assert len(list(test_repo.packages)) == 3


@pytest.mark.parametrize(
    "query,expect_name",
    [
        ("esp32", ["micropython-esp32-stubs-1.18.post1"]),
        ("EsP32", ["micropython-esp32-stubs-1.18.post1"]),
        ("8266", ["esp8266-micropython-1.15.0-abc123"]),
        (
            "micropython",
            [
                "micropython-esp32-stubs-1.18.post1",
                "micropython-7ff2cce0237268cd52164b77b6c2df6be6249a67ee285edc122960af869b8ed2",
                "esp8266-micropython-1.15.0-abc123",
            ],
        ),
    ],
)
def test_repo_search(test_repo, query, expect_name):
    results = test_repo.search(query)
    names = [i.versioned_name for i in results]
    assert sorted(names) == sorted(expect_name)
