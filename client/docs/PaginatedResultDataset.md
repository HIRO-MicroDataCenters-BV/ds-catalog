# PaginatedResultDataset


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**page** | **int** |  | 
**size** | **int** |  | 
**items** | [**List[Dataset]**](Dataset.md) |  | 

## Example

```python
from ds_catalog.models.paginated_result_dataset import PaginatedResultDataset

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedResultDataset from a JSON string
paginated_result_dataset_instance = PaginatedResultDataset.from_json(json)
# print the JSON string representation of the object
print(PaginatedResultDataset.to_json())

# convert the object into a dict
paginated_result_dataset_dict = paginated_result_dataset_instance.to_dict()
# create an instance of PaginatedResultDataset from a dict
paginated_result_dataset_from_dict = PaginatedResultDataset.from_dict(paginated_result_dataset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


