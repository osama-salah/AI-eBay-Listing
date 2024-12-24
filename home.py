import streamlit as st
import webbrowser
from urllib.parse import unquote
from page_template import header, footer
from listing_creator import create_listing_form
from eBay import EbayAuth
from lib.session import save_session_state, load_session_state, logout

# Load state
load_session_state()

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
    # Main Streamlit app
    ebay_production = EbayAuth(
        client_id='ArmojanV-OSlistin-PRD-0dc1b488a-cf971abd',
        client_secret='PRD-dc1b488a0a1e-aa29-4c7f-afe7-0447',
        dev_id='296dd38e-bc69-4a03-a77f-57e0a8d03f00',
        ru_name='Armojan_Van-ArmojanV-OSlist-fxtjxihj'
    )
    # Save the created client in session state
    st.session_state.ebay_production = ebay_production

    # Initialize session state for authentication state
    st.session_state.auth_state = None

# Restore the eBay client from session state
ebay_production = st.session_state.ebay_production

# Display the header
header()

# Display Logged-in if a user token is present
if ebay_production.user_token:
    st.write(":green[Logged in]")

    # Logout button
    if st.button("Logout"):
        logout()
else:
    st.write(":red[Please log in to access the application.]")

# Get user token if not already present
if not ebay_production.user_token:
    # If not waiting for user token, get it
    if not st.session_state.auth_state:
        scopes = ["https://api.ebay.com/oauth/api_scope", "https://api.ebay.com/oauth/api_scope/sell.marketing.readonly", "https://api.ebay.com/oauth/api_scope/sell.marketing", "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly", "https://api.ebay.com/oauth/api_scope/sell.inventory", "https://api.ebay.com/oauth/api_scope/sell.account.readonly", "https://api.ebay.com/oauth/api_scope/sell.account", "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly", "https://api.ebay.com/oauth/api_scope/sell.fulfillment", "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly", "https://api.ebay.com/oauth/api_scope/sell.finances", "https://api.ebay.com/oauth/api_scope/sell.payment.dispute", "https://api.ebay.com/oauth/api_scope/commerce.identity.readonly", "https://api.ebay.com/oauth/api_scope/sell.reputation", "https://api.ebay.com/oauth/api_scope/sell.reputation.readonly", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription", "https://api.ebay.com/oauth/api_scope/commerce.notification.subscription.readonly", "https://api.ebay.com/oauth/api_scope/sell.stores", "https://api.ebay.com/oauth/api_scope/sell.stores.readonly", "https://api.ebay.com/oauth/scope/sell.edelivery"]

        # Get authorization URL for user consent
        auth_url = ebay_production.get_auth_url(scopes)

        # Open the authorization URL in a new tab and get the code
        print("Opening browser for authorization...")
        webbrowser.open(auth_url)

        print("Waiting for authorization...") 

        # # Get the code from the redirect URL via terminal
        # auth_code = unquote(input("Enter the code from the redirect URL: "))

    if st.session_state.auth_state != 'authorized':
        # Input field for the authorization code
        auth_code = unquote(st.text_input("Enter the authorization code:"))

        # Submit button to get the user token
        if st.button("Submit"):
            # Get the user token
            ebay_production.get_user_token(auth_code)

            # Check if the user token is valid
            if ebay_production.user_token['access_token']:
                print("User token is valid.")
                st.session_state.auth_state = 'authorized'
                save_session_state()
                st.rerun()
            else:
                print("User token is invalid.") 
        else:
            st.session_state.auth_state = 'auth_waiting'

    # # Get user token
    # ebay_production.get_user_token(auth_code)
    # # print(f'authorization code: {auth_code}')
    # # print(f'user token: {ebay_production.user_token}')

# Disable navigation while processing
with st.sidebar:
    try:
        print('trying to get page')
        index = ["Home", "Listing Creator"].index(page)
        st.session_state.page = page
        save_session_state()
        print(f'page: {page}')
    except NameError:
        index = 0
    page = st.radio("Navigation", ["Home", "Listing Creator"], disabled=navigation_disabled(), index=index)

# Update the session state based on navigation immediately
st.session_state.page = page
save_session_state()

# Conditional rendering based on the selected page
if st.session_state.page == "Home":
    st.write("## Welcome to eBay Listing Creator!")
    st.write("Use the navigation menu to switch between different tools.")
elif st.session_state.page == "Listing Creator":
    create_listing_form()

# Display the footer
footer()

# Convert session state to dict before saving
serializable_dict = dict(st.session_state)

save_session_state()