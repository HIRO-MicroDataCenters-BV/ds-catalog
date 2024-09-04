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

from ds_catalog.models.connector import Connector

class TestConnector(unittest.TestCase):
    """Connector unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> Connector:
        """Test Connector
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `Connector`
        """
        model = Connector()
        if include_optional:
            return Connector(
                id = ''
            )
        else:
            return Connector(
                id = '',
        )
        """

    def testConnector(self):
        """Test Connector"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
