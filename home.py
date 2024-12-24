import streamlit as st
import webbrowser
from urllib.parse import unquote
from page_template import header, footer
from listing_creator import create_listing_form
from eBay import EbayAuth


# Set the page configuration
st.set_page_config(page_title="Product Insights", page_icon=":mag:", layout="centered")

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
    # Main Streamlit app
    ebay_production = EbayAuth(
        client_id='ArmojanV-OSlistin-PRD-0dc1b488a-cf971abd',
        client_secret='PRD-dc1b488a0a1e-aa29-4c7f-afe7-0447',
        dev_id='296dd38e-bc69-4a03-a77f-57e0a8d03f00',
        ru_name='Armojan_Van-ArmojanV-OSlist-fxtjxihj'
    )
    # # Save the created client in session state
    st.session_state.ebay_production = ebay_production

# Restore the eBay client from session state
ebay_production = st.session_state.ebay_production

# Get user token if not already present
if not ebay_production.user_token:
    scopes = ["https://api.ebay.com/oauth/api_scope", "https://api.ebay.com/oauth/api_scope/sell.marketing.readonly", "https://api.ebay.com/oauth/api_scope/sell.marketing", "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly", "https://api.ebay.com/oauth/api_scope/sell.inventory", "https://api.ebay.com/oauth/api_scope/sell.account.readonly", "https://api.ebay.com/oauth/api_scope/sell.account", "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly", "https://api.ebay.com/oauth/api_scope/sell.fulfillment", "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly", "https://api.ebay.com/oauth/api_scope/sell.finances", "https://api.ebay.com/oauth/api_scope/sell.payment.dispute", "https://api.ebay.com/oauth/api_scope/commerce.identity.readonly", "https://api.ebay.com/oauth/api_scope/sell.reputation", "https://api.ebay.com/oauth/api_scope/sell.reputation.readonly", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly", "https://api.ebay.com/oauth/api_scope/sell.stores", "https://api.ebay.com/oauth/api_scope/sell.stores.readonly", "https://api.ebay.com/oauth/scope/sell.edelivery"]

    # Get authorization URL for user consent
    auth_url = ebay_production.get_auth_url(scopes)
    print("Auth URL:", auth_url)

    # Open the authorization URL in a new tab and get the code
    print("Opening browser for authorization...")
    webbrowser.open(auth_url)

    print("Waiting for authorization...") 

    # Get the code from the redirect URL via terminal
    auth_code = unquote(input("Enter the code from the redirect URL: "))

    # Get user token
    ebay_production.get_user_token(auth_code)
    print(f'authorization code: {auth_code}')
    print(f'user token: {ebay_production.user_token}')

    # Check if the user token is valid
    if ebay_production.user_token['access_token']:
        print("User token is valid.")
    else:
        print("User token is invalid.")    
        
# Display the header
header()

# Display Logged-in if a user token is present
if ebay_production.user_token:
    st.write(":green[Logged in]")
else:
    st.write(":red[Please log in to access the application.]")

# Disable navigation while processing
with st.sidebar:
    page = st.radio("Navigation", ["Home", "Listing Creator"], disabled=navigation_disabled())

# Update the session state based on navigation immediately
st.session_state.page = page

# Conditional rendering based on the selected page
if st.session_state.page == "Home":
    st.write("## Welcome to eBay Listing Creator!")
    st.write("Use the navigation menu to switch between different tools.")
elif st.session_state.page == "Listing Creator":
    create_listing_form()

# Display the footer
footer()
