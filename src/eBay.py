import streamlit as st
import xml.etree.ElementTree as ET

import base64
import requests
import webbrowser
import xml.etree.ElementTree as ET
from urllib.parse import urlencode, unquote

class EbayAPI:
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
        print(f'endpoint: {endpoint}')
        
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

        try:
            self.app_token = response.json()
            return self.app_token
        except KeyError as e:
            print(f"Error getting app token from: {response.json()}")
            return None

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
        
        return self.user_token

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
            query (str): Search query for category suggestions
            marketplace_id (str): Target marketplace ID
        """
        endpoint = "https://api.ebay.com/commerce/taxonomy/v1/category_tree/0/get_category_suggestions"

        if not self.app_token:
            raise ValueError("Production app token is required.")    
        
        headers = {
            "Authorization": f"Bearer {self.app_token['access_token']}",
            "Accept": "application/json",
        }
        
        params = {
            "q": query
        }
        
        response = requests.get(endpoint, headers=headers, params=params)
        return response.json()

    @staticmethod
    def load_credentials(env='production', config_file='config/ebay_credentials.xml'):
        tree = ET.parse(config_file)
        root = tree.getroot()
        
        # environment = root.find(env)
        # creds = {
        #     'client_id': environment.find('client_id').text,
        #     'client_secret': environment.find('client_secret').text,
        #     'dev_id': environment.find('dev_id').text,
        #     'ru_name': environment.find('ru_name').text
        # }
        # Load credentials from secrets manager for production/sandbox
        creds = {
                'client_id': st.secrets[f'{env}-credentials']['client_id'],
                'client_secret': st.secrets[f'{env}-credentials']['client_secret'],
                'dev_id': st.secrets['dev_id'],
                'ru_name': st.secrets[f'{env}-credentials']['ru_name']
        }
            
        return creds

if __name__ == "__main__":
    # Initialize sandbox environment
    print('Initializing sandbox environment...')
    sandbox_creds = EbayAPI.load_credentials(env='sandbox')
    ebay_sandbox = EbayAPI(**sandbox_creds)

    # Get application token (sandbox)
    print("Getting sandbox application token...")
    app_token_sandbox = ebay_sandbox.get_app_token(env='sandbox')

    # Initialize production environment 
    production_creds = EbayAPI.load_credentials('production')
    ebay_production = EbayAPI(**production_creds)

    # Get application token (production)
    ebay_production.get_app_token()

    scopes_production = ["https://api.ebay.com/oauth/api_scope", "https://api.ebay.com/oauth/api_scope/sell.marketing.readonly", "https://api.ebay.com/oauth/api_scope/sell.marketing", "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly", "https://api.ebay.com/oauth/api_scope/sell.inventory", "https://api.ebay.com/oauth/api_scope/sell.account.readonly", "https://api.ebay.com/oauth/api_scope/sell.account", "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly", "https://api.ebay.com/oauth/api_scope/sell.fulfillment", "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly", "https://api.ebay.com/oauth/api_scope/sell.finances", "https://api.ebay.com/oauth/api_scope/sell.payment.dispute", "https://api.ebay.com/oauth/api_scope/commerce.identity.readonly", "https://api.ebay.com/oauth/api_scope/sell.reputation", "https://api.ebay.com/oauth/api_scope/sell.reputation.readonly", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly", "https://api.ebay.com/oauth/api_scope/sell.stores", "https://api.ebay.com/oauth/api_scope/sell.stores.readonly", "https://api.ebay.com/oauth/scope/sell.edelivery"]
    scopes_sandbox =    ["https://api.ebay.com/oauth/api_scope", "https://api.ebay.com/oauth/api_scope/buy.order.readonly", "https://api.ebay.com/oauth/api_scope/buy.guest.order", "https://api.ebay.com/oauth/api_scope/sell.marketing.readonly", "https://api.ebay.com/oauth/api_scope/sell.marketing", "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly", "https://api.ebay.com/oauth/api_scope/sell.inventory", "https://api.ebay.com/oauth/api_scope/sell.account.readonly", "https://api.ebay.com/oauth/api_scope/sell.account", "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly", "https://api.ebay.com/oauth/api_scope/sell.fulfillment", "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly", "https://api.ebay.com/oauth/api_scope/sell.marketplace.insights.readonly", "https://api.ebay.com/oauth/api_scope/commerce.catalog.readonly", "https://api.ebay.com/oauth/api_scope/buy.shopping.cart", "https://api.ebay.com/oauth/api_scope/buy.offer.auction", "https://api.ebay.com/oauth/api_scope/commerce.identity.readonly", "https://api.ebay.com/oauth/api_scope/commerce.identity.email.readonly", "https://api.ebay.com/oauth/api_scope/commerce.identity.phone.readonly", "https://api.ebay.com/oauth/api_scope/commerce.identity.address.readonly", "https://api.ebay.com/oauth/api_scope/commerce.identity.name.readonly", "https://api.ebay.com/oauth/api_scope/commerce.identity.status.readonly", "https://api.ebay.com/oauth/api_scope/sell.finances", "https://api.ebay.com/oauth/api_scope/sell.payment.dispute", "https://api.ebay.com/oauth/api_scope/sell.item.draft", "https://api.ebay.com/oauth/api_scope/sell.item", "https://api.ebay.com/oauth/api_scope/sell.reputation", "https://api.ebay.com/oauth/api_scope/sell.reputation.readonly", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly", "https://api.ebay.com/oauth/api_scope/sell.stores", "https://api.ebay.com/oauth/api_scope/sell.stores.readonly"]

    # Get sandbox authorization URL for user consent
    print("Getting sandbox authorization URL...")
    auth_url = ebay_sandbox.get_auth_url(scopes_sandbox, env='sandbox')
    # Automatically open the URL in the default browser
    webbrowser.open(auth_url)
    
    # After sandbox user authorizes and you get the code from callback URL
    auth_code = unquote(input("Enter the code from the redirect URL: "))
    sandbox_user_token = ebay_sandbox.get_user_token(auth_code, env='sandbox')
    print("Successfully retrieved sandbox user token." if 'access_token' in sandbox_user_token else "Failed to retrieve sandbox user token.")

    # Get production authorization URL for user consent
    print("Getting prduction authorization URL...")
    auth_url = ebay_production.get_auth_url(scopes_production)
    # Automatically open the URL in the default browser
    webbrowser.open(auth_url)

    # After production user authorizes and you get the code from callback URL  
    auth_code = unquote(input("Enter the code from the redirect URL: "))
    production_user_token = ebay_production.get_user_token(auth_code)
    print("Successfully retrieved production user token." if 'access_token' in production_user_token else "Failed to retrieve production user token.")    

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