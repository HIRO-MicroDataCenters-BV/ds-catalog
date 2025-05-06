from pathlib import Path

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
        file_path = Path(__file__).parent / "fixtures" / "mmio.csv"
        return file_path.read_bytes()

    @pytest.fixture
    def mmio_instance(self, csv_data):
        return MMIO(csv_data)

    def test_mmio_get_data(self, mmio_instance):
        data = mmio_instance.get_data()

        assert isinstance(data.records, list)
        assert len(data.records) == 1
        assert isinstance(data.records[0], pl.DataFrame)

        df = data.records[0]
        assert df.shape == (1, 20)
        assert df.columns == [
            "age",
            "sex",
            "gender",
            "ethnicity",
            "previous_myocardial_infarction",
            "stroke",
            "chronic_obstructive_pulmonary_disease",
            "asthma",
            "atrial_fibrillation",
            "peripheral_artery_disease",
            "hypertension",
            "diabetes",
            "hypercholesterolemia",
            "chronic_kidney_disease",
            "height",
            "waist_hip_ratio",
            "waist_height_ratio",
            "sbp",
            "pulse_rate",
            "smoking_history",
        ]

        assert df[0, "age"] is True
        assert df[0, "sex"] is True
        assert df[0, "gender"] is True
        assert df[0, "ethnicity"] is False
        assert df[0, "previous_myocardial_infarction"] is True
        assert df[0, "stroke"] is True
        assert df[0, "chronic_obstructive_pulmonary_disease"] is True
        assert df[0, "asthma"] is True
        assert df[0, "atrial_fibrillation"] is False
        assert df[0, "peripheral_artery_disease"] is False
        assert df[0, "hypertension"] is True
        assert df[0, "diabetes"] is True
        assert df[0, "hypercholesterolemia"] is True
        assert df[0, "chronic_kidney_disease"] is False
        assert df[0, "height"] is True
        assert df[0, "waist_hip_ratio"] is True
        assert df[0, "waist_height_ratio"] is False
        assert df[0, "sbp"] is False
        assert df[0, "pulse_rate"] is False
        assert df[0, "smoking_history"] is False

    def test_mmio_transform(self, mmio_instance, default_schema_uri):
        transformed = mmio_instance.transform_to(default_schema_uri)

        df = transformed.records[0]
        assert df.shape == (1, 20)

        assert df.columns == [
            "hasAge",
            "hasSex",
            "hasGender",
            "hasEthnicity",
            "hasMyocardialInfarction",
            "hasStroke",
            "hasCOPD",
            "hasAsthma",
            "hasAtrialFibrillation",
            "hasPeripheralArteryDisease",
            "hasHypertension",
            "hasDiabetes",
            "hasHypercholesterolemia",
            "hasChronicKidneyDisease",
            "hasHeight",
            "hasWaistHipRatio",
            "hasWaistHeightRatio",
            "hasSystolicBloodPressure",
            "hasPulseRate",
            "hasSmokingHistory",
        ]

        assert df[0, "hasAge"] is True
        assert df[0, "hasSex"] is True
        assert df[0, "hasGender"] is True
        assert df[0, "hasEthnicity"] is False
        assert df[0, "hasMyocardialInfarction"] is True
        assert df[0, "hasStroke"] is True
        assert df[0, "hasCOPD"] is True
        assert df[0, "hasAsthma"] is True
        assert df[0, "hasAtrialFibrillation"] is False
        assert df[0, "hasPeripheralArteryDisease"] is False
        assert df[0, "hasHypertension"] is True
        assert df[0, "hasDiabetes"] is True
        assert df[0, "hasHypercholesterolemia"] is True
        assert df[0, "hasChronicKidneyDisease"] is False
        assert df[0, "hasHeight"] is True
        assert df[0, "hasWaistHipRatio"] is True
        assert df[0, "hasWaistHeightRatio"] is False
        assert df[0, "hasSystolicBloodPressure"] is False
        assert df[0, "hasPulseRate"] is False
        assert df[0, "hasSmokingHistory"] is False


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
