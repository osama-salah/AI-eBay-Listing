import json
import requests
import streamlit as st
from itertools import product
from json.decoder import JSONDecodeError

import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lib.session import load_session_state, save_session_state
from lib.ai import compose_listing

# Create a Streamlit form for eBay product listing creation
def create_listing_form():
    # Clear previous categories from session state
    with st.expander("**Listing info**", expanded=True):
    # with st.form("Create eBay Listing"):    
        # Product basic information
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.title = st.text_input("Product Title", value=st.session_state.get('title') ,placeholder="e.g. iPhone 15 Pro Max 256GB")
            st.session_state.manufacturer = st.text_input("Manufacturer", value=st.session_state.get('manufacturer'), placeholder="e.g. Apple")
            
        with col2:
            st.session_state.summary = st.text_area("Summary",st.session_state.get('summary') , height=150)
        
        # Generate listing button
        if st.button("Generate Listing", disabled=st.session_state.get('auth_state') != 'authorized'):
            if st.session_state.title and st.session_state.manufacturer and st.session_state.summary:
                try:
                    listing = compose_listing(st.session_state.title, st.session_state.manufacturer, st.session_state.summary)
                    st.session_state.gen_title = listing.get('title')
                    st.session_state.gen_description = listing.get('description')

                except JSONDecodeError as e:
                    st.error(f"Error with GenAI. Please try again.")
            else:
                st.error("Please fill in required fields: Title, Manufacturer, and Summary.")
        
        st.session_state.gen_title = st.text_input("Title", value=st.session_state.get('gen_title', ''))
        st.session_state.gen_description = st.text_area("Description", height=150, value=st.session_state.get('gen_description', ''))

    with st.expander("**Listing Details**", expanded=True):
        # Display category suggestions button
        suggest_category_btn = st.button("Suggest a category", disabled=st.session_state.get('auth_state') != 'authorized')
        if suggest_category_btn:
            if st.session_state.title and st.session_state.manufacturer:
                display_suggestions(st.session_state.title, st.session_state.manufacturer)
            else:
                st.error("Please fill in required fields: Title and Manufacturer")

        st.session_state.selected_category = st.selectbox(
            "Suggested Categories",
            disabled=st.session_state.get('categories', None) is None or st.session_state.get('auth_state') != 'authorized',
            options=st.session_state.get('categories', []),
            index=st.session_state.get('selected_category_index', 0),
            format_func=lambda x: f"{x[0]} > {x[2]}"
        )

        st.session_state.selected_category_id = st.session_state.selected_category[1]
        st.session_state.selected_category_index = st.session_state.categories.index(st.session_state.selected_category)

        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.sku = st.text_input("SKU", value=st.session_state.get('sku', ''))
            st.session_state.price = st.number_input("Price", value=st.session_state.get('price', 0.0), min_value=0.0, step=0.01)
            st.session_state.weight = st.number_input("Weight", value=st.session_state.get('weight', 0.0) , min_value=0.0, step=0.1)

            st.session_state.condition_options = ["New with box", "New without box", "New with defects", "Pre-owned"]
            condition = st.selectbox(
                "Condition",
                options=st.session_state.get('condition_options', []),
                index=st.session_state.get('condition_options', []).index(st.session_state.get('condition', 'New with box'))
                )

            st.session_state.quantity = st.number_input("Available Quantity", value=st.session_state.get('quantity', 1), min_value=1, step=1)
            
        with col2:
            st.session_state.marketplace_options = ["EBAY_US", "EBAY_CA", "EBAY_GB", "EBAY_AU", "EBAY_DE", "EBAY_FR", "EBAY_IT", "EBAY_ES"]
            st.session_state.marketplace = st.selectbox(
                "eBay Marketplace", 
            options=st.session_state.get('marketplace_options', []),
            index=st.session_state.get('marketplace_options', []).index(st.session_state.get('marketplace', 'EBAY_US'))
            )

            st.session_state.merchant_location = st.text_input("Merchant Location", value=st.session_state.get('merchant_location', ''))
            st.session_state.fulfillment_policy = st.text_input("Fulfillment Policy", value=st.session_state.get('fulfillment_policy', ''))                        
            st.session_state.return_policy = st.text_input("Return Policy", value=st.session_state.get('return_policy', ''))                                             
            st.session_state.payment_policy = st.text_input("Payment Policy", value=st.session_state.get('payment_policy', ''))

        # Dynamic Aspects Section
        if st.session_state.get('selected_category') and st.session_state.get('auth_state') == 'authorized':
            category_id = st.session_state.selected_category[1]
            aspects = st.session_state.ebay_client.get_category_aspects(category_id)
            
            st.subheader("Category Aspects")

            if not st.session_state.get('selected_aspects', None):
                st.session_state.selected_aspects = {}

            for aspect in aspects:
                # Retrieve the selected aspect values from the session state
                try:
                    aspects_index = aspect['values'].index(st.session_state.get('selected_aspects', {}).get(aspect['name']))
                except ValueError:
                    aspects_index = 0

                st.session_state.selected_aspects[aspect['name']] = st.selectbox(
                    aspect['name'], options=aspect['values'],
                    index=aspects_index
                    )

        st.subheader("Images")
        # Media Section
        # Display existing images with remove buttons
        i = 0
        uploaded_images = st.session_state.get('uploaded_images', [])
        while i < len(uploaded_images):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if uploaded_images[i]:
                    st.image(uploaded_images[i], width=200)
            
            with col2:
                if st.button(f"Remove Image {i+1}"):
                    uploaded_images.pop(i)
                    save_session_state()
                    st.rerun()
            i += 1

        uploaded_file = st.file_uploader("Add New Image", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            if uploaded_file not in uploaded_images:
                uploaded_images.append(uploaded_file)
                save_session_state()
                st.rerun()

        # Show a message if maximum images reached
        if len(uploaded_images) >= 24:
            st.warning("Maximum number of images (24) reached.")

        # Save uploaded images in session state
        st.session_state['uploaded_images'] = uploaded_images

        # Video upload
        st.subheader("Video")

        if st.session_state.get('video_file') is None:
            video_file = st.file_uploader("Product Video",  type=['mp4', 'mov', 'avi'])

            if video_file:
                st.session_state.video_file = video_file

        if st.session_state.video_file:
            st.video(st.session_state.get('video_file'))
            if st.button("Remove Video"):
                st.session_state.video_file = None
                save_session_state()
                st.rerun()

    # Create listing button
    if st.button("Create Listing", disabled=st.session_state.get('auth_state') != 'authorized'):
        if title and manufacturer and summary:
            # Here you would integrate with eBay's Inventory API
            listing_data = {
                "title": title,
                "manufacturer": manufacturer,
                "category": selected_category if 'selected_category' in locals() else None,
                "has_image": uploaded_image is not None
            }
            st.success("Listing created successfully!")
            st.json(listing_data)
            save_session_state()
        else:
            st.error("Please fill in required fields: Title and Manufacturer")    
    
def display_suggestions(title, manufacturer, categories=None):
    if not categories:
        search_query = f"{title} {manufacturer}".strip()
        # Verify ebay_production has a valid user token
        if not st.session_state.ebay_production.app_token:
            st.error("App token is not available. Please log in.")
            return

        try:
            suggestions = st.session_state.ebay_production.get_category_suggestions(search_query)
        except ValueError as ve:
            st.error(f"Error: {ve}")
            return
        
        if 'categorySuggestions' in suggestions:
            st.session_state.categories = [(suggestion['categoryTreeNodeAncestors'][0]['categoryName'],
            suggestion['category']['categoryId'],
            suggestion['category']['categoryName']) for suggestion in suggestions['categorySuggestions']]
