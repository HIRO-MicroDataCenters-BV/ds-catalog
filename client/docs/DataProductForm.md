# DataProductForm


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**size** | [**Size**](Size.md) |  | 
**mimetype** | **str** |  | 
**digest** | **str** |  | 
**source** | [**Source**](Source.md) |  | 
**access_point_url** | **str** |  | 

## Example

```python
from ds_catalog.models.data_product_form import DataProductForm

# TODO update the JSON string below
json = "{}"
# create an instance of DataProductForm from a JSON string
data_product_form_instance = DataProductForm.from_json(json)
# print the JSON string representation of the object
print DataProductForm.to_json()

# convert the object into a dict
data_product_form_dict = data_product_form_instance.to_dict()
# create an instance of DataProductForm from a dict
data_product_form_form_dict = data_product_form.from_dict(data_product_form_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


