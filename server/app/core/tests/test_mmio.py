import polars as pl
import pytest

from ..entities import Metadata
from ..mmio import MMIO, mmio_data_to_entities


@pytest.fixture
def default_schema_uri():
    return "http://oca.example.org/some-schema/"


class TestMMIO:
    @pytest.fixture
    def csv_data(self):
        return b"name,surname,height,weight\nDeirdre,Patterson,174,68\n"

    @pytest.fixture
    def mmio_instance(self, csv_data):
        return MMIO(csv_data)

    def test_mmio_get_data(self, mmio_instance):
        data = mmio_instance.get_data()

        assert isinstance(data.records, list)
        assert len(data.records) == 1
        assert isinstance(data.records[0], pl.DataFrame)

        df = data.records[0]
        assert df.shape == (1, 4)
        assert df.columns == ["name", "surname", "height", "weight"]
        assert df[0, "name"] == "Deirdre"
        assert df[0, "surname"] == "Patterson"
        assert df[0, "height"] == 174
        assert df[0, "weight"] == 68

    def test_mmio_transform(self, mmio_instance, default_schema_uri):
        transformed = mmio_instance.transform_to(default_schema_uri)
        assert transformed.records[0].columns == [
            "patientFirstName",
            "patientLastName",
            "patientHeight",
            "patientWeight",
        ]
        df = transformed.records[0]
        assert df[0, "patientFirstName"] == "Deirdre"
        assert df[0, "patientLastName"] == "Patterson"
        assert df[0, "patientHeight"] == 174
        assert df[0, "patientWeight"] == 68


def test_mmio_data_to_entities(default_schema_uri):
    mmio_id = "123"
    csv_data = (
        b"name,surname,height,weight\n"
        + b"Deirdre,Patterson,174,68\n"
        + b"Luis,Hembree,181,79\n"
    )
    mmio_instance = MMIO(csv_data)
    data = mmio_instance.get_data()

    results = mmio_data_to_entities(default_schema_uri, mmio_id, data)

    assert len(results) == 2

    metadata1, metadata2 = results
    assert metadata1.uri == Metadata.build_uri(default_schema_uri, f"{mmio_id}/{0}", 0)
    assert metadata2.uri == Metadata.build_uri(default_schema_uri, f"{mmio_id}/{0}", 1)
