from typing import Any, Self

from abc import ABC, abstractmethod

import m2io_tmp as mmio
import polars as pl

from .entities import Metadata


class Data(ABC):
    records: list[pl.DataFrame]

    @abstractmethod
    def to(self, standard: dict[str, Any]) -> Self:
        """Transform data to a different standard"""
        ...


class MMIOType(ABC):
    data: Data

    @abstractmethod
    def infer_semantics(self, data: pl.DataFrame) -> Data:
        """Infer semantics of the data"""
        ...

    @abstractmethod
    def ingest(self, data: pl.DataFrame) -> None:
        """Ingest data into MMIO"""
        ...

    @abstractmethod
    def link(self, standard: str, linkage: dict[str, str]) -> None:
        """Link data to a standard"""
        ...


class MMIO:
    _mmio: MMIOType

    def __init__(self, csv: bytes) -> None:
        # TODO: Implement. It is a mock for now
        df = pl.read_csv(csv)
        self._mmio = mmio.infer_semantics(df)
        self._mmio.ingest(df)
        self._mmio.link(
            "Standard1@1.0",
            linkage={
                "age": "hasAge",
                "sex": "hasSex",
                "gender": "hasGender",
                "ethnicity": "hasEthnicity",
                "previous_myocardial_infarction": "hasMyocardialInfarction",
                "stroke": "hasStroke",
                "chronic_obstructive_pulmonary_disease": "hasCOPD",
                "asthma": "hasAsthma",
                "atrial_fibrillation": "hasAtrialFibrillation",
                "peripheral_artery_disease": "hasPeripheralArteryDisease",
                "hypertension": "hasHypertension",
                "diabetes": "hasDiabetes",
                "hypercholesterolemia": "hasHypercholesterolemia",
                "chronic_kidney_disease": "hasChronicKidneyDisease",
                "height": "hasHeight",
                "waist_hip_ratio": "hasWaistHipRatio",
                "waist_height_ratio": "hasWaistHeightRatio",
                "sbp": "hasSystolicBloodPressure",
                "pulse_rate": "hasPulseRate",
                "smoking_history": "hasSmokingHistory",
            },
        )

    def __str__(self) -> str:
        return str(self._mmio.data.records)

    def get_data(self) -> Data:
        return self._mmio.data

    def transform_to(self, uri: str) -> Data:
        # TODO: Implement. It is a mock for now
        return self._mmio.data.to({"standard": "Standard1@1.0"})


def mmio_data_to_entities(schema_uri: str, mmio_id: str, data: Data) -> list[Metadata]:
    result = []
    for i, record in enumerate(data.records):
        id = f"{mmio_id}/{i}"
        result += Metadata.create_bunch_from_df(schema_uri, id, record)
    return result
