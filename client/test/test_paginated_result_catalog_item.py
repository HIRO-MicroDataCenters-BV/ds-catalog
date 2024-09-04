# coding: utf-8

"""
    Data Space Catalog

    The service provides a REST API for managing and sharing catalog data. Interacts with connector services to obtain information about data products.

    The version of the OpenAPI document: 0.1.1
    Contact: all-hiro@hiro-microdatacenters.nl
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from ds_catalog.models.paginated_result_catalog_item import PaginatedResultCatalogItem

class TestPaginatedResultCatalogItem(unittest.TestCase):
    """PaginatedResultCatalogItem unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> PaginatedResultCatalogItem:
        """Test PaginatedResultCatalogItem
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `PaginatedResultCatalogItem`
        """
        model = PaginatedResultCatalogItem()
        if include_optional:
            return PaginatedResultCatalogItem(
                page = 56,
                size = 56,
                items = [
                    ds_catalog.models.catalog_item.CatalogItem(
                        ontology = 'DCAT-3', 
                        title = '', 
                        summary = '', 
                        id = '', 
                        is_local = True, 
                        is_shared = True, 
                        created = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        creator = ds_catalog.models.user.User(
                            id = '', 
                            full_name = '', ), 
                        data_products = [
                            ds_catalog.models.data_product.DataProduct(
                                id = '', 
                                name = '', 
                                size = null, 
                                mimetype = '', 
                                digest = '', 
                                source = ds_catalog.models.source.Source(
                                    connector = ds_catalog.models.connector.Connector(
                                        id = '', ), 
                                    node = null, 
                                    interface = null, ), 
                                _links = {
                                    'key' : ''
                                    }, )
                            ], 
                        _links = {
                            'key' : ''
                            }, )
                    ]
            )
        else:
            return PaginatedResultCatalogItem(
                page = 56,
                size = 56,
                items = [
                    ds_catalog.models.catalog_item.CatalogItem(
                        ontology = 'DCAT-3', 
                        title = '', 
                        summary = '', 
                        id = '', 
                        is_local = True, 
                        is_shared = True, 
                        created = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'), 
                        creator = ds_catalog.models.user.User(
                            id = '', 
                            full_name = '', ), 
                        data_products = [
                            ds_catalog.models.data_product.DataProduct(
                                id = '', 
                                name = '', 
                                size = null, 
                                mimetype = '', 
                                digest = '', 
                                source = ds_catalog.models.source.Source(
                                    connector = ds_catalog.models.connector.Connector(
                                        id = '', ), 
                                    node = null, 
                                    interface = null, ), 
                                _links = {
                                    'key' : ''
                                    }, )
                            ], 
                        _links = {
                            'key' : ''
                            }, )
                    ],
        )
        """

    def testPaginatedResultCatalogItem(self):
        """Test PaginatedResultCatalogItem"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
