import streamlit as st

import base64
import requests
from urllib.parse import urlencode, unquote

class EbayAuth:
    def __init__(self, client_id, client_secret, dev_id, ru_name):
        """
        Initialize eBay OAuth authentication utility
        
        Args:
            client_id (str): Your eBay application client ID
            client_secret (str): Your eBay application client secret  
            ru_name (str): RuName value from your eBay application
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.dev_id = dev_id
        self.ru_name = ru_name
        self.user_token = None
        self.app_token = None
        
        # eBay OAuth endpoints
        self.endpoints = {
            'production': {
                'api': 'https://api.ebay.com',
                'auth': 'https://auth.ebay.com'
            },
            'sandbox': {
                'api': 'https://api.sandbox.ebay.com',
                'auth': 'https://auth.sandbox.ebay.com'
            }
        }

    def get_app_token(self, env='production'):
        """
        Get application OAuth token using client credentials grant
        
        Args:
            env (str): Environment - 'production' or 'sandbox'
            
        Returns:
            dict: Response containing access token and expiration
        """
        endpoint = f"{self.endpoints[env]['api']}/identity/v1/oauth2/token"
        
        # Encode credentials
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()).decode()
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {credentials}'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }
        
        response = requests.post(endpoint, headers=headers, data=data)

        self.app_token = response.json()['access_token']

        return response.json()

    def get_auth_url(self, scopes, env='production'):
        """
        Get authorization URL for user consent
        
        Args:
            scopes (list): List of eBay API scopes to request
            env (str): Environment - 'production' or 'sandbox'
            
        Returns:
            str: Authorization URL
        """
        endpoint = f"{self.endpoints[env]['auth']}/oauth2/authorize"
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.ru_name,
            'scope': ' '.join(scopes)
        }
        
        return f"{endpoint}?{urlencode(params)}"

    def get_user_token(self, auth_code, env='production'):
        """
        Get user OAuth token using authorization code
        
        Args:
            auth_code (str): Authorization code from callback URL
            env (str): Environment - 'production' or 'sandbox'
            
        Returns:
            dict: Response containing access token, refresh token and expiration
        """
        endpoint = f"{self.endpoints[env]['api']}/identity/v1/oauth2/token"
        
        # Encode credentials
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()).decode()
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {credentials}'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.ru_name
        }

        self.user_token = requests.post(endpoint, headers=headers, data=data).json()
        
        response = requests.post(endpoint, headers=headers, data=data)
        return response.json()

    def refresh_user_token(self, refresh_token, env='production'):
        """
        Refresh user OAuth token using refresh token
        
        Args:
            refresh_token (str): Refresh token from previous auth
            env (str): Environment - 'production' or 'sandbox'
            
        Returns:
            dict: Response containing new access token and expiration
        """
        endpoint = f"{self.endpoints[env]['api']}/identity/v1/oauth2/token"
        
        # Encode credentials
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()).decode()
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {credentials}'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }

        self.user_token = requests.post(endpoint, headers=headers, data=data).json()
        
        response = requests.post(endpoint, headers=headers, data=data)
        return response.json()  
        
    def get_category_suggestions(self, query, marketplace_id="EBAY_US"):
        """
        Get category suggestions for a given query
        
        Args:
            app_token (str): Application OAuth token
            query (str): Search query for category suggestions
            marketplace_id (str): Target marketplace ID
        """
        endpoint = "https://api.ebay.com/commerce/taxonomy/v1/category_tree/0/get_category_suggestions"

        if not self.user_token:
            raise ValueError("User token is required.")    
        
        headers = {
            "Authorization": f"Bearer {self.user_token['access_token']}",
            "Accept": "application/json",
        }
        
        params = {
            "q": query
        }
        
        response = requests.get(endpoint, headers=headers, params=params)
        return response.json()

# Example usage
if __name__ == '__main__':
    # Initialize with your credentials
    # ebay_sandbox = EbayAuth(
    #     client_id='ArmojanV-OSlistin-SBX-3c261000e-27f91c7c',
    #     client_secret='SBX-c261000e7b35-e8c9-452e-b172-6d81',
    #     ru_name='https://signin.ebay.com/ws/eBayISAPI.dll?ThirdPartyAuthSucessFailure&isAuthSuccessful=true'
    # )

    ebay_production = EbayAuth(
        client_id='ArmojanV-OSlistin-PRD-0dc1b488a-cf971abd',
        client_secret='PRD-dc1b488a0a1e-aa29-4c7f-afe7-0447',
        dev_id='296dd38e-bc69-4a03-a77f-57e0a8d03f00',
        ru_name='Armojan_Van-ArmojanV-OSlist-fxtjxihj'
    )
    
    # # Get application token (sandox)
    # app_token_sandbox = ebay_sandbox.get_app_token(env='sandbox')
    # print("App Token:", app_token_sandbox)

    # Get application token (production)
    # app_token = ebay.get_app_token()
    # print("App Token:", app_token)

    scopes = ["https://api.ebay.com/oauth/api_scope", "https://api.ebay.com/oauth/api_scope/sell.marketing.readonly", "https://api.ebay.com/oauth/api_scope/sell.marketing", "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly", "https://api.ebay.com/oauth/api_scope/sell.inventory", "https://api.ebay.com/oauth/api_scope/sell.account.readonly", "https://api.ebay.com/oauth/api_scope/sell.account", "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly", "https://api.ebay.com/oauth/api_scope/sell.fulfillment", "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly", "https://api.ebay.com/oauth/api_scope/sell.finances", "https://api.ebay.com/oauth/api_scope/sell.payment.dispute", "https://api.ebay.com/oauth/api_scope/commerce.identity.readonly", "https://api.ebay.com/oauth/api_scope/sell.reputation", "https://api.ebay.com/oauth/api_scope/sell.reputation.readonly", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly", "https://api.ebay.com/oauth/api_scope/sell.stores", "https://api.ebay.com/oauth/api_scope/sell.stores.readonly", "https://api.ebay.com/oauth/scope/sell.edelivery"]

    # Get authorization URL for user consent
    auth_url = ebay_production.get_auth_url(scopes)
    print("Auth URL:", auth_url)
    
    # After user authorizes and you get the code from callback URL
    auth_code = unquote(input("Enter the code from the redirect URL: "))
    user_token = ebay_production.get_user_token(auth_code)
    print("User Token:", user_token)

    # Get category suggestions
    suggestions = ebay_production.get_category_suggestions('IPhone 15')

    # Extract category and sub-category names
    suggested_categories = [(suggestion['categoryTreeNodeAncestors'][0]['categoryName'], suggestion['category']['categoryName']) for suggestion in suggestions['categorySuggestions']]

    # Print the suggested categories
    print("Suggested Categories:", suggested_categories)
    
    # Later, refresh the user token
    # refresh_token = user_token['refresh_token']
    # new_token = ebay_sandbox.refresh_user_token(refresh_token)
    # print("Refreshed Token:", new_token)