# DataProduct


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**size** | [**Size**](Size.md) |  | 
**mimetype** | **str** |  | 
**digest** | **str** |  | 
**source** | [**Source**](Source.md) |  | 
**links** | **Dict[str, str]** |  | 

## Example

```python
from ds_catalog.models.data_product import DataProduct

# TODO update the JSON string below
json = "{}"
# create an instance of DataProduct from a JSON string
data_product_instance = DataProduct.from_json(json)
# print the JSON string representation of the object
print DataProduct.to_json()

# convert the object into a dict
data_product_dict = data_product_instance.to_dict()
# create an instance of DataProduct from a dict
data_product_form_dict = data_product.from_dict(data_product_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


