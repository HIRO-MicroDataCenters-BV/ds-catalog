from enum import Enum


class Tags(str, Enum):
    Catalog = "Catalog"
    Datasets = "Datasets"
    Sharing = "Sharing"
    MMIO = "MMIO"
