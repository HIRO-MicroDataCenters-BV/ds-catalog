from typing import Any, Callable, Protocol, Self

import io
import json
import os
import tarfile
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import httpx
import m2io_nextgen as mmio
import polars as pl

from .entities import Metadata
from .exceptions import ErrorParsingMMIO


class MMIOReaderOCABundle(Protocol):
    def is_reference(self) -> bool:
        ...

    def is_bundle(self) -> bool:
        ...


@dataclass
class MMIOReaderID:
    value: str


@dataclass
class MMIOReaderModality:
    id: MMIOReaderID
    modality_type: str
    media_type: str
    oca_bundle: MMIOReaderOCABundle


@dataclass
class MMIOReaderResult:
    modalities: list[MMIOReaderModality]


MMIOReader = Callable[[str], MMIOReaderResult]


class OCABundle:
    _digest: str
    _attribute_names: list[str]

    def __init__(self, bundle_str: str) -> None:
        try:
            bundle = json.loads(bundle_str)
        except json.JSONDecodeError:
            raise ErrorParsingMMIO("The bundle file contains invalid JSON")

        try:
            self._digest = bundle["bundle"]["digest"]
            self._attribute_names = list(
                bundle["bundle"]["capture_base"]["attributes"].keys()
            )
        except Exception as err:
            raise ErrorParsingMMIO(f"Invalid bundle: {err}")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, OCABundle):
            return False
        return self.digest == other.digest

    @property
    def digest(self) -> str:
        return self._digest

    @property
    def attribute_names(self) -> list[str]:
        return self._attribute_names


@dataclass
class Modality:
    id: str
    modality_type: str
    media_type: str
    oca_bundle: OCABundle | None


@dataclass
class MMIOParsedData:
    id: str
    modalities: list[Modality]


class IMMIOParser(ABC):
    @abstractmethod
    def parse(self, data: bytes) -> MMIOParsedData:
        ...


class TarMMIOParser(IMMIOParser):
    def parse(self, data: bytes, mmio_reader: MMIOReader = mmio.open) -> MMIOParsedData:
        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                with tarfile.open(fileobj=io.BytesIO(data)) as tar:
                    tar.extractall(path=tmp_dir)
            except tarfile.ReadError:
                raise ErrorParsingMMIO("The file is not a valid tar archive")

            mmio_file = Path(tmp_dir, "mmio.json")
            try:
                mmio_str = mmio_file.read_text()
            except FileNotFoundError:
                raise ErrorParsingMMIO("File mmio.json not found in archive")
            except OSError:
                raise ErrorParsingMMIO("Unable to read mmio.json file")

            try:
                mmio_dict = json.loads(mmio_str)
            except json.JSONDecodeError:
                raise ErrorParsingMMIO("The mmio.json file contains invalid JSON")

            if not isinstance(mmio_dict, dict):
                raise ErrorParsingMMIO("The mmio.json file must contain a JSON object")
            if "id" not in mmio_dict or not mmio_dict["id"]:
                raise ErrorParsingMMIO("The mmio.json file is missing the ID")

            id = mmio_dict["id"]

            bundles = self._parse_bundle_files(tmp_dir)

            try:
                mmio_obj = mmio_reader(mmio_str)
            except Exception as err:
                raise ErrorParsingMMIO(f"Invalid MMIO: {err}")

            modalities = self._parse_modalities(bundles, mmio_obj.modalities)

            return MMIOParsedData(id=id, modalities=modalities)

    def _parse_bundle_files(self, dir_path: str) -> dict[str, OCABundle]:
        result = {}
        bundle_files = Path(dir_path).glob("*.bundles")
        for bundle_file in bundle_files:
            bundle = OCABundle(bundle_file.read_text())
            result[bundle.digest] = bundle
        return result

    def _parse_modalities(
        self, bundles_store: dict[str, OCABundle], modalities: list[MMIOReaderModality]
    ) -> list[Modality]:
        result = []
        for modality in modalities:
            if modality.oca_bundle.is_reference():
                ref = str(modality.oca_bundle)
                oca_bundle = bundles_store.get(ref)
            elif modality.oca_bundle.is_bundle():
                oca_bundle = OCABundle(f'{{"bundle": {modality.oca_bundle}}}')
            else:
                oca_bundle = None

            result.append(
                Modality(
                    id=modality.id.value,
                    modality_type=modality.modality_type,
                    media_type=modality.media_type,
                    oca_bundle=oca_bundle,
                )
            )
        return result


class JsonMMIOParser(IMMIOParser):
    def __init__(self):
        self.errors: list[str] = []

    def parse(self, data: bytes, schema_uri: str | None = None) -> MMIOParsedData:
        try:
            mmio_dict = json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            raise ErrorParsingMMIO("The mmio.json file contains invalid JSON")

        if not isinstance(mmio_dict, dict):
            raise ErrorParsingMMIO("The mmio.json file must contain a JSON object")
        if "id" not in mmio_dict or not mmio_dict["id"]:
            raise ErrorParsingMMIO("The mmio.json file is missing the ID")

        mmio_id = mmio_dict["id"]
        modalities = self._parse_modalities(mmio_dict.get("modalities", []), schema_uri)
        return MMIOParsedData(id=mmio_id, modalities=modalities)

    def _parse_modalities(
        self, modalities_data: list[dict[str, Any]], schema_uri: str | None
    ) -> list[Modality]:
        result = []
        for modality in modalities_data:
            bundle_info = modality.get("oca_bundle")
            oca_bundle = None

            if bundle_info:
                if bundle_info["type"] == "Reference":
                    said = bundle_info["value"]
                    try:
                        oca_bundle = self._download_oca_bundle(said, schema_uri)
                    except Exception as e:
                        # Save error but don’t stop
                        self.errors.append(f"Failed to fetch OCA bundle {said}: {e}")
                        oca_bundle = None
                elif bundle_info["type"] == "Bundle":
                    oca_bundle = OCABundle(json.dumps({"bundle": bundle_info["value"]}))

            result.append(
                Modality(
                    id=modality["id"],
                    modality_type=modality.get("modality_type", ""),
                    media_type=modality.get("media_type", ""),
                    oca_bundle=oca_bundle,
                )
            )
        return result

    def _download_oca_bundle(self, said: str, schema_uri: str | None) -> OCABundle:
        base_url = (
            schema_uri
            or os.getenv(
                "DS_OCA_BUNDLES_BASE_URL",
                "https://oca-repository.marketplace.nextgen.hiro-develop.nl/oca-bundles",
            )
        ).rstrip("/")
        url = f"{base_url}/{said}"
        resp = httpx.get(url, timeout=10.0)
        resp.raise_for_status()
        return OCABundle(resp.text)


class MMIO:
    _id: str
    _modalities: list[Modality]

    def __init__(
        self, mmio_data: bytes, parser: IMMIOParser, schema_uri: str | None = None
    ) -> None:
        if isinstance(parser, JsonMMIOParser):
            parsed_data = parser.parse(mmio_data, schema_uri)
        else:
            parsed_data = parser.parse(mmio_data)
        self._id = parsed_data.id
        self._modalities = parsed_data.modalities

    def __str__(self) -> str:
        return self.id

    @property
    def id(self) -> str:
        return self._id

    @property
    def modalities(self) -> list[Modality]:
        return self._modalities

    def transform_to(self, schema_uri: str) -> Self:
        # TODO: Implement
        return self


def mmio_available_attrs(mmio_obj: MMIO) -> list[pl.DataFrame]:
    result = []
    for modality in mmio_obj.modalities:
        bundle = modality.oca_bundle
        if bundle is not None:
            df = pl.DataFrame({attr: [True] for attr in bundle.attribute_names})
            result.append(df)
    return result


def mmio_data_to_entities(
    schema_uri: str, mmio_id: str, data: list[pl.DataFrame]
) -> list[Metadata]:
    result = []
    for i, record in enumerate(data):
        id = f"{mmio_id}/{i}"
        result += Metadata.create_bunch_from_df(schema_uri, id, record)
    return result
