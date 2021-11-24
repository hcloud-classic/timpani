import logging
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from .schema.auth import LOGIN_QUERY, CHECKTOKEN_QUERY
from .schema.sync import NODELIST_QUERY, VOLUMELIST_QUERY

logger = logging.getLogger(__name__)

class GqlClient:

    def __init__(self, target_url, app):
        self.url = target_url
        self.transport = RequestsHTTPTransport(
            url=target_url,
            timeout=3,
            verify=True,
            retries=1
        )
        # self.client = Client(transport=self.transport, fetch_schema_from_transport=True)
        self.app = app

    def login_request(self, username, password):
        query = gql(LOGIN_QUERY.replace("X_USERNAME", username).replace("X_PASSWORD", password))
        client = Client(transport=self.transport, fetch_schema_from_transport=True)
        result = client.execute(query)
        client.close()
        if self.app is not None:
            self.app.logger.info('login_result : {}'.format(result))
        return result

    def checktoken_request(self, token):
        query = gql(CHECKTOKEN_QUERY.replace("X_TOKEN", token))
        client = Client(transport=self.transport, fetch_schema_from_transport=True)
        result = client.execute(query)
        client.close()
        if self.app is not None:
            self.app.logger.info('checktoken_result : {}'.format(result))
        return result

    def nodelist_request(self, token):
        query = gql(NODELIST_QUERY.replace("X_TOKEN", token))
        client = Client(transport=self.transport, fetch_schema_from_transport=True)
        result = client.execute(query)
        client.close()
        if self.app is not None:
            self.app.logger.info('nodelist_result : {}'.format(result))
        return result

    def volumelist_request(self, token):
        query = gql(VOLUMELIST_QUERY.replace("X_TOKEN", token))
        client = Client(transport=self.transport, fetch_schema_from_transport=True)
        result = client.execute(query)
        client.close()
        if self.app is not None:
            self.app.logger.info('volumelist_result : {}'.format(result))
        return result

