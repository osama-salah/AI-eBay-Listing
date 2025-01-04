from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from threading import Thread
import uvicorn

import streamlit as st
import webbrowser
from urllib.parse import unquote
from page_template import header, footer
from listing_creator import create_listing_form
from eBay import EbayAPI
from lib.session import save_session_state, load_session_state, logout

SANDBOX_ENABLE = True

app = FastAPI()

@app.get("/test")
async def test():
    return {"status": "Server is running!"}

@app.get("/callback")
async def callback(code: str):
    print("Received callback")
    load_session_state()
    st.session_state.callback_auth_code = code
    save_session_state()
    return RedirectResponse(url="http://localhost:8501")

def run_fastapi():
    uvicorn.run(app, host="localhost", port=8000)
    # uvicorn.run(app, host="localhost", port=8000, ssl_keyfile="key.pem", ssl_certfile="cert.pem")

# stop the server
def stop_server():
    uvicorn.Server.server_state.should_exit = True
    st.session_state.server_started = False
    print("Server stopped")

# Check if navigation_radio is set in session state
refresh_navigation_radio = st.session_state.navigation_radio if 'navigation_radio' in st.session_state else None

# Load state (without navigation_radio)
print("Loading session state")
load_session_state()

# Restore navigation radio if it exists
if refresh_navigation_radio:
    st.session_state.navigation_radio = refresh_navigation_radio

# Set the page configuration
st.set_page_config(page_title="eBay Listing App", page_icon=":mag:", layout="centered")

# Load CSS styles
with open('static/css/styles.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'Home'  # Default to Home

# Initialize session state for processing
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Function to disable navigation buttons
def navigation_disabled():
    return st.session_state.processing

def authorize_client(env='production'):
    if not ebay_production.app_token:        
        # Get production application token
        print(f"Getting production application token...")
        ebay_production.get_app_token()

        if ebay_production.app_token.get('access_token'):
            print("Production application token obtained successfully.")
        else:
            print("Failed to obtain production application token.")
            return

    if not ebay_sandbox.app_token:
        # Get sandbox application token
        print(f"Getting sandbox application token...")
        ebay_sandbox.get_app_token(env='sandbox')

        if ebay_sandbox.app_token.get('access_token'):
            print("Sandbox application token obtained successfully.")
        else:
            print("Failed to obtain sandbox application token.")
            return

    # If auth_state is set to authorize, start the authorization process
    if st.session_state.get('auth_state') == 'authorize':
        if env == 'production':
            scopes = ["https://api.ebay.com/oauth/api_scope", "https://api.ebay.com/oauth/api_scope/sell.marketing.readonly", "https://api.ebay.com/oauth/api_scope/sell.marketing", "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly", "https://api.ebay.com/oauth/api_scope/sell.inventory", "https://api.ebay.com/oauth/api_scope/sell.account.readonly", "https://api.ebay.com/oauth/api_scope/sell.account", "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly", "https://api.ebay.com/oauth/api_scope/sell.fulfillment", "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly", "https://api.ebay.com/oauth/api_scope/sell.finances", "https://api.ebay.com/oauth/api_scope/sell.payment.dispute", "https://api.ebay.com/oauth/api_scope/commerce.identity.readonly", "https://api.ebay.com/oauth/api_scope/sell.reputation", "https://api.ebay.com/oauth/api_scope/sell.reputation.readonly", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly", "https://api.ebay.com/oauth/api_scope/sell.stores", "https://api.ebay.com/oauth/api_scope/sell.stores.readonly", "https://api.ebay.com/oauth/scope/sell.edelivery"]
            
        elif env == 'sandbox':
            scopes = ["https://api.ebay.com/oauth/api_scope", "https://api.ebay.com/oauth/api_scope/buy.order.readonly", "https://api.ebay.com/oauth/api_scope/buy.guest.order", "https://api.ebay.com/oauth/api_scope/sell.marketing.readonly", "https://api.ebay.com/oauth/api_scope/sell.marketing", "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly", "https://api.ebay.com/oauth/api_scope/sell.inventory", "https://api.ebay.com/oauth/api_scope/sell.account.readonly", "https://api.ebay.com/oauth/api_scope/sell.account", "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly", "https://api.ebay.com/oauth/api_scope/sell.fulfillment", "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly", "https://api.ebay.com/oauth/api_scope/sell.marketplace.insights.readonly", "https://api.ebay.com/oauth/api_scope/commerce.catalog.readonly", "https://api.ebay.com/oauth/api_scope/buy.shopping.cart", "https://api.ebay.com/oauth/api_scope/buy.offer.auction", "https://api.ebay.com/oauth/api_scope/commerce.identity.readonly", "https://api.ebay.com/oauth/api_scope/commerce.identity.email.readonly", "https://api.ebay.com/oauth/api_scope/commerce.identity.phone.readonly", "https://api.ebay.com/oauth/api_scope/commerce.identity.address.readonly", "https://api.ebay.com/oauth/api_scope/commerce.identity.name.readonly", "https://api.ebay.com/oauth/api_scope/commerce.identity.status.readonly", "https://api.ebay.com/oauth/api_scope/sell.finances", "https://api.ebay.com/oauth/api_scope/sell.payment.dispute", "https://api.ebay.com/oauth/api_scope/sell.item.draft", "https://api.ebay.com/oauth/api_scope/sell.item", "https://api.ebay.com/oauth/api_scope/sell.reputation", "https://api.ebay.com/oauth/api_scope/sell.reputation.readonly", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly", "https://api.ebay.com/oauth/api_scope/sell.stores", "https://api.ebay.com/oauth/api_scope/sell.stores.readonly"]     

        # Get authorization URL for user consent
        print(f"Getting {env} authorization URL...")
        auth_url = st.session_state.ebay_client.get_auth_url(scopes, env=env)

        # Automatically open the URL in the same tab
        # webbrowser.open(auth_url)
        st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)

        # Start FastAPI server in a separate thread
        if 'server_started' not in st.session_state:
            Thread(target=run_fastapi, daemon=True).start()
            st.session_state.server_started = True                            

            print("FastAPI server started")

        st.session_state['auth_state'] = 'auth_waiting'

    if st.session_state.get('auth_state') != 'authorized':      
        if st.session_state.callback_auth_code:
            print('Getting user token...')
            st.session_state.ebay_client.get_user_token(st.session_state.callback_auth_code, env=env)
            
            if st.session_state.ebay_client.user_token['access_token']:
                print(f"{env}: Authorization successful")
                st.session_state['auth_state'] = 'authorized'

                save_session_state()
                st.rerun()
            else:
                print(f"{env}: Authorization failed")
        else:
            st.info(f"{env}: Waiting for authorization...")
            st.session_state['auth_state'] = 'auth_waiting'

# Initialize eBay Production client if not already initialized
if 'ebay_production' not in st.session_state:
    print('Initializing Production client...')
    
    creds = EbayAPI.load_credentials(env='production')
    ebay_production = EbayAPI(**creds)

    st.session_state.ebay_production = ebay_production
    st.session_state.callback_auth_code = None

# Initialize eBay Sandbox client if not already initialized
if 'ebay_sandbox' not in st.session_state:
    print('Initializing Sandbox client...')

    creds = EbayAPI.load_credentials(env='sandbox')
    ebay_sandbox = EbayAPI(**creds)

    st.session_state.ebay_sandbox = ebay_sandbox
    st.session_state.callback_auth_code = None

ebay_production = st.session_state.ebay_production
ebay_sandbox = st.session_state.ebay_sandbox

# Set the eBay client based on the selected environment
st.session_state.ebay_client = ebay_sandbox if SANDBOX_ENABLE else ebay_production

header()

# Check if user is logged in
if st.session_state.ebay_client.user_token and st.session_state.ebay_production.app_token:
    print("User is logged in")
    st.write(":green[Logged in]")
    
    if st.button("Logout"):
        print("User logged out")
        logout()
else:
    print("User not logged in")
    # Display login button
    if st.button("Login"):
        # Clear any log in session state
        # logout()
        st.session_state.auth_state = 'authorize'
        
        print('Logging in...')
    
    st.write(":red[Please log in to access the application.]")


# Start client authorization flow if auth_state is 'authorize'
if st.session_state.get('auth_state') == 'authorize' or st.session_state.get('auth_state') == 'auth_waiting':
    print("Starting/resuming client authorization flow")
    
    env = 'sandbox' if SANDBOX_ENABLE else 'production'
    authorize_client(env)

with st.sidebar:
    print(f'navigation_radio 1: {st.session_state.get("navigation_radio", "Home")}')
    selected_page = st.radio(
        "Navigation",
        ["Home", "Listing Creator"],
        disabled=navigation_disabled(),
        key="navigation_radio",
        index=["Home", "Listing Creator"].index(st.session_state.get('last_page', 'Home'))
    )

if st.session_state.navigation_radio == "Home":
    print("Displaying Home page")
    st.write("## Welcome to eBay Listing Creator!")
    st.write("Use the navigation menu to switch between different tools.")
elif st.session_state.navigation_radio == "Listing Creator":
    print("Displaying Listing Creator page")
    create_listing_form()

footer()

save_session_state()

