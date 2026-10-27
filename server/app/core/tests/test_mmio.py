from pathlib import Path
from unittest.mock import Mock

import polars as pl
import pytest

from ..entities import Metadata
from ..exceptions import ErrorParsingMMIO
from ..mmio import (
    MMIO,
    IMMIOParser,
    MMIOParsedData,
    Modality,
    OCABundle,
    TarMMIOParser,
    mmio_available_attrs,
    mmio_data_to_entities,
)
from .factories import tar_factory


@pytest.fixture
def mmio_data():
    file_path = Path(__file__).parent / "fixtures" / "mmio.json"
    return file_path.read_text()


@pytest.fixture
def bundle_data():
    file_path = Path(__file__).parent / "fixtures" / "bundle.json"
    return file_path.read_text()


class TestOCABundle:
    def test_valid_json(self, bundle_data):
        bundle = OCABundle(bundle_data)
        assert bundle.digest == "EB-d473DxvmtISCVwL2AC_qGHdMNdMdFWeSq7jhMupys"
        assert set(bundle.attribute_names) == {"age", "bmi"}

    def test_invalid_json(self):
        invalid_json = "{]"
        with pytest.raises(ErrorParsingMMIO, match="invalid JSON"):
            OCABundle(invalid_json)

    def test_missing_bundle_key(self):
        json_missing_bundle = '{"not_bundle": {}}'
        with pytest.raises(ErrorParsingMMIO, match="Invalid bundle"):
            OCABundle(json_missing_bundle)

    def test_missing_digest(self):
        json_missing_digest = """
        {
            "bundle": {
                "capture_base": {
                    "attributes": {
                        "attr1": {}
                    }
                }
            }
        }
        """
        with pytest.raises(ErrorParsingMMIO, match="Invalid bundle"):
            OCABundle(json_missing_digest)

    def test_missing_attributes(self):
        json_missing_attributes = """
        {
            "bundle": {
                "digest": "xyz789",
                "capture_base": {}
            }
        }
        """
        with pytest.raises(ErrorParsingMMIO, match="Invalid bundle"):
            OCABundle(json_missing_attributes)

    def test_comparison(self, bundle_data):
        other = """
        {
            "bundle": {
                "digest": "zxc123",
                "capture_base": {
                    "attributes": {
                        "name": {},
                        "age": {},
                        "email": {}
                    }
                }
            }
        }
        """
        assert OCABundle(bundle_data) == OCABundle(bundle_data)
        assert OCABundle(bundle_data) != OCABundle(other)


class TestTarMMIOParser:
    def test_success(self, mmio_data, bundle_data):
        tar_bytes = tar_factory({"mmio.json": mmio_data, "test.bundles": bundle_data})

        parser = TarMMIOParser()
        result = parser.parse(tar_bytes)

        assert result.id == "EI2z8E6zYvMF_yvquoUJedWi0rKpQsscPf7JlBgIDoOm"
        assert len(result.modalities) == 1
        assert result.modalities[0] == Modality(
            id="EEORbmaaCrfby9K7MH9MY4W6YQTMPQGfyVgSm9MX-_MA",
            modality_type="binary",
            media_type="application/octet-stream",
            oca_bundle=OCABundle(bundle_data),
        )

    def test_invalid_tar(self):
        parser = TarMMIOParser()
        with pytest.raises(ErrorParsingMMIO, match="not a valid tar archive"):
            parser.parse(b"not a tar")

    def test_missing_mmio_json(self, bundle_data):
        tar_bytes = tar_factory(
            {
                "test.bundles": bundle_data,
            }
        )

        parser = TarMMIOParser()
        with pytest.raises(ErrorParsingMMIO, match="mmio.json not found"):
            parser.parse(tar_bytes)

    def test_invalid_json(self, bundle_data):
        tar_bytes = tar_factory(
            {
                "mmio.json": "{]",
                "test.bundles": bundle_data,
            }
        )

        parser = TarMMIOParser()
        with pytest.raises(ErrorParsingMMIO, match="invalid JSON"):
            parser.parse(tar_bytes)

    def test_invalid_json_object(self, bundle_data):
        tar_bytes = tar_factory(
            {
                "mmio.json": "[]",
                "test.bundles": bundle_data,
            }
        )

        parser = TarMMIOParser()
        with pytest.raises(ErrorParsingMMIO, match="must contain a JSON object"):
            parser.parse(tar_bytes)

    def test_missing_id(self, bundle_data):
        tar_bytes = tar_factory(
            {
                "mmio.json": "{}",
                "test.bundles": bundle_data,
            }
        )

        parser = TarMMIOParser()
        with pytest.raises(ErrorParsingMMIO, match="missing the ID"):
            parser.parse(tar_bytes)

    def test_invalid_mmio(self, mmio_data, bundle_data):
        mock_mmio_reader = Mock(side_effect=Exception())
        tar_bytes = tar_factory({"mmio.json": mmio_data, "test.bundles": bundle_data})

        parser = TarMMIOParser()
        with pytest.raises(ErrorParsingMMIO, match="Invalid MMIO"):
            parser.parse(tar_bytes, mmio_reader=mock_mmio_reader)


class TestMMIO:
    @pytest.fixture
    def mmio_bytes(self):
        return b"fake-mmio-data"

    @pytest.fixture
    def modalities(self):
        return [Mock(), Mock()]

    @pytest.fixture
    def fake_parser(self, modalities):
        parser = Mock(spec=IMMIOParser)
        parser.parse.return_value = MMIOParsedData(
            id="test-id",
            modalities=modalities,
        )
        return parser

    def test_mmio_initialization(self, mmio_bytes, modalities, fake_parser):
        mmio = MMIO(mmio_bytes, parser=fake_parser)
        assert mmio.id == "test-id"
        assert len(mmio.modalities) == 2
        assert mmio.modalities == modalities
        fake_parser.parse.assert_called_once_with(mmio_bytes)

    def test_mmio_str(self, mmio_bytes, fake_parser):
        mmio = MMIO(mmio_bytes, parser=fake_parser)
        assert str(mmio) == "test-id"

    def test_id(self, mmio_bytes, fake_parser):
        mmio = MMIO(mmio_bytes, parser=fake_parser)
        assert mmio.id == "test-id"

    def test_modalities(self, mmio_bytes, modalities, fake_parser):
        mmio = MMIO(mmio_bytes, parser=fake_parser)
        assert mmio.modalities == modalities


class TestMMIOAvailableAttrs:
    @pytest.fixture
    def mock_bundle(self):
        bundle = Mock()
        bundle.attribute_names = ["attr1", "attr2"]
        bundle.digest = "test-digest"
        return bundle

    @pytest.fixture
    def modality_with_bundle(self, mock_bundle):
        modality = Mock()
        modality.oca_bundle = mock_bundle
        return modality

    @pytest.fixture
    def modality_without_bundle(self):
        modality = Mock()
        modality.oca_bundle = None
        return modality

    def test_with_bundle(self, modality_with_bundle):
        mmio = Mock()
        mmio.modalities = [modality_with_bundle]

        result = mmio_available_attrs(mmio)
        df, digest = result[0]
        assert isinstance(df, pl.DataFrame)
        assert isinstance(digest, str)

        assert df.columns == ["attr1", "attr2"]
        assert df.height == 1
        assert df.row(0) == (True, True)

    def test_multiple_modalities(self, modality_with_bundle, modality_without_bundle):
        mmio = Mock()
        mmio.modalities = [
            modality_with_bundle,
            modality_without_bundle,
            modality_with_bundle,
        ]

        result = mmio_available_attrs(mmio)
        assert len(result) == 2  # one modality is without bundle
        for df, digest in result:
            assert isinstance(df, pl.DataFrame)
            assert isinstance(digest, str)

    def test_all_bundles_are_none(self, modality_without_bundle):
        mmio = Mock()
        mmio.modalities = [modality_without_bundle, modality_without_bundle]
        result = mmio_available_attrs(mmio)
        assert result == []


def test_mmio_data_to_entities():
    schema_uri = "http://oca.example.org/some-schema/"
    mmio_id = "123"
    df1 = pl.DataFrame({"attr1": [True, True], "attr2": [True, True]})
    df2 = pl.DataFrame({"attr3": [True], "attr4": [True]})

    data = [
        (df1, "digest1"),
        (df2, "digest2"),
    ]

    results = mmio_data_to_entities(schema_uri, mmio_id, data)

    assert len(results) == 3

    metadata1, metadata2, metadata3 = results
    assert metadata1.uri == Metadata.build_uri(schema_uri, f"{mmio_id}/{0}", 0)
    assert metadata2.uri == Metadata.build_uri(schema_uri, f"{mmio_id}/{0}", 1)
    assert metadata3.uri == Metadata.build_uri(schema_uri, f"{mmio_id}/{1}", 0)
