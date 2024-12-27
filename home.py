import streamlit as st
import webbrowser
from urllib.parse import unquote
from page_template import header, footer
from listing_creator import create_listing_form
from eBay import EbayAuth
from lib.session import save_session_state, load_session_state, logout

# Check if navigation_radio is set in session state
refresh_navigation_radio = st.session_state.navigation_radio if 'navigation_radio' in st.session_state else None

# Load state
print("Loading session state")
load_session_state()

# Restore refresh navigation radio if it exists
if refresh_navigation_radio:
    st.session_state.navigation_radio = refresh_navigation_radio

# # Restore last selected page from session state if it exists
# if 'last_page' in st.session_state:
#     st.session_state.page = st.session_state.last_page

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

# Initialize eBay client if not already initialized
if 'ebay_production' not in st.session_state:
    print("Initializing eBay client")
    ebay_production = EbayAuth(
        client_id='ArmojanV-OSlistin-PRD-0dc1b488a-cf971abd',
        client_secret='PRD-dc1b488a0a1e-aa29-4c7f-afe7-0447',
        dev_id='296dd38e-bc69-4a03-a77f-57e0a8d03f00',
        ru_name='Armojan_Van-ArmojanV-OSlist-fxtjxihj'
    )
    st.session_state.ebay_production = ebay_production
    st.session_state.auth_state = None

ebay_production = st.session_state.ebay_production

header()

if ebay_production.user_token:
    print("User is logged in")
    st.write(":green[Logged in]")
    
    if st.button("Logout"):
        print("User logged out")
        logout()
else:
    print("User not logged in")
    st.write(":red[Please log in to access the application.]")

if not ebay_production.user_token:
    if not st.session_state.auth_state:
        scopes = ["https://api.ebay.com/oauth/api_scope", "https://api.ebay.com/oauth/api_scope/sell.marketing.readonly", "https://api.ebay.com/oauth/api_scope/sell.marketing", "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly", "https://api.ebay.com/oauth/api_scope/sell.inventory", "https://api.ebay.com/oauth/api_scope/sell.account.readonly", "https://api.ebay.com/oauth/api_scope/sell.account", "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly", "https://api.ebay.com/oauth/api_scope/sell.fulfillment", "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly", "https://api.ebay.com/oauth/api_scope/sell.finances", "https://api.ebay.com/oauth/api_scope/sell.payment.dispute", "https://api.ebay.com/oauth/api_scope/commerce.identity.readonly", "https://api.ebay.com/oauth/api_scope/sell.reputation", "https://api.ebay.com/oauth/api_scope/sell.reputation.readonly", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly", "https://api.ebay.com/oauth/api_scope/sell.stores", "https://api.ebay.com/oauth/api_scope/sell.stores.readonly", "https://api.ebay.com/oauth/scope/sell.edelivery"]

        auth_url = ebay_production.get_auth_url(scopes)
        print("Opening browser for authorization...")
        webbrowser.open(auth_url)
        print("Waiting for authorization...")

    if st.session_state.auth_state != 'authorized':
        auth_code = unquote(st.text_input("Enter the authorization code:"))
        
        if st.button("Submit"):
            ebay_production.get_user_token(auth_code)
            
            if ebay_production.user_token['access_token']:
                print("Authorization successful")
                st.session_state.auth_state = 'authorized'
                save_session_state()
                st.rerun()
            else:
                print("Authorization failed")
        else:
            st.session_state.auth_state = 'auth_waiting'

save_session_state()

with st.sidebar:
    print(f'navigation_radio 1: {st.session_state.get("navigation_radio", "Home")}')
    selected_page = st.radio(
        "Navigation",
        ["Home", "Listing Creator"],
        disabled=navigation_disabled(),
        key="navigation_radio",
        index=["Home", "Listing Creator"].index(st.session_state.get('last_page', 'Home'))
    )
    
    print(f'navigation_radio 2: {st.session_state.navigation_radio}')

save_session_state()

if st.session_state.navigation_radio == "Home":
    print("Displaying Home page")
    st.write("## Welcome to eBay Listing Creator!")
    st.write("Use the navigation menu to switch between different tools.")
elif st.session_state.navigation_radio == "Listing Creator":
    print("Displaying Listing Creator page")
    create_listing_form()

footer()

serializable_dict = dict(st.session_state)
save_session_state()
print("Session state saved")