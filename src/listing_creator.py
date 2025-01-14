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

# Initialize session state variables
rerun_flag = False
st.session_state.title = None
st.session_state.manufacturer = None
st.session_state.image_url = None

# Create a Streamlit form for eBay product listing creation
def create_listing_form():
        # Hide file uploader's filename display using custom CSS
    st.markdown("""
        <style>
            .uploadedFile {
                display: none;
            }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<h2 style="text-align: center;">Create eBay Listing</h2>', unsafe_allow_html=True)
    
    # Product basic information
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Product Title", value=st.session_state.get('title') or '', placeholder="e.g. iPhone 15 Pro Max 256GB")
        manufacturer = st.text_input("Manufacturer", value=st.session_state.get('manufacturer') or '',placeholder="e.g. Apple")
        st.session_state.title = title
        st.session_state.manufacturer = manufacturer
        
    with col2:
        summary = st.text_area("Summary", value=st.session_state.get('summary') or '', height=150)
        st.session_state.summary = summary
    
    col1, col2 = st.columns(2)
    with col1:
        # Display category suggestions button
        if st.button("Suggest a category", disabled=not st.session_state.auth_state == 'authorized'):
            if st.session_state.title and st.session_state.manufacturer:
                display_suggestions()
            else:
                st.error("Please fill in required fields: Title, Manufacturer, and Summary.")
        elif 'categories' in st.session_state:
            display_suggestions(st.session_state.categories)

    with col2:
        # Generate listing button
        if st.button("Generate Listing", type="primary", disabled=not st.session_state.auth_state == 'authorized'):
            if st.session_state.title and st.session_state.manufacturer and st.session_state.summary:
                try:
                    listing = compose_listing(st.session_state.title, st.session_state.manufacturer, st.session_state.summary)
                    st.session_state.gen_title = listing.get('title')
                    st.session_state.gen_description = listing.get('description')
                    save_session_state()
                    st.rerun()
                except JSONDecodeError as e:
                    st.error(f"Error with GenAI. Please try again.")
            else:
                st.error("Please fill in required fields: Title and Manufacturer")
            
    selected_category = st.selectbox(
        "Suggested Categories",
        disabled=st.session_state.get('categories') is None or not st.session_state.auth_state == 'authorized',
        options=st.session_state.get('categories') or [],
        format_func=lambda x: f"{x[0]} > {x[2]}",
        index=st.session_state.categories.index(st.session_state.selected_category) if st.session_state.get('selected_category') else 0
    )
    # Save the selected category in session state
    st.session_state.selected_category = selected_category
    
    # Product information form
    with st.container():
        st.subheader("Suggested Listing")
        
        gen_title = st.text_input("Title", value=st.session_state.get('gen_title') or '')
        gen_description = st.text_area(
            "Description", height=150, 
            value=st.session_state.get('gen_description') or ''
            )

        st.subheader("Manual Entries")

        col1, col2 = st.columns(2)
        
        with col1:
            sku = st.text_input("SKU", key="sku")
            
            price = st.number_input("Price", min_value=0.0, step=0.01, key="price")            
            weight = st.number_input("Weight", min_value=0.0, step=0.1, key="weight")

            condition_options = ["New with box", "New without box", "New with defects", "Pre-owned"]
            condition = st.selectbox("Condition", options=condition_options, key="condition")

            quantity = st.number_input("Available Quantity", min_value=1, step=1, key="quantity")
            
        with col2:
            marketplace_options = ["EBAY_US", "EBAY_CA", "EBAY_GB", "EBAY_AU", "EBAY_DE", "EBAY_FR", "EBAY_IT", "EBAY_ES"]
            marketplace = st.selectbox("eBay Marketplace", options=marketplace_options, key="marketplace")

            merchant_location = st.text_input("Merchant Location", key="merchant_location") 

            fulfillment_policy = st.text_input("Fulfillment Policy", key="fulfillment_policy")
            return_policy = st.text_input("Return Policy", key="return_policy")                                    
            payment_policy = st.text_input("Payment Policy", key="payment_policy")            

        # Dynamic Aspects Section
        if st.session_state.get('selected_category') and st.session_state.auth_state == 'authorized':
            category_id = st.session_state.selected_category[1]
            aspects = st.session_state.ebay_client.get_category_aspects(category_id)
            
            st.subheader("Category Aspects")

            selected_aspects = {}
            for aspect in aspects:
                selected_aspects[aspect['name']] = st.selectbox(aspect['name'], options=aspect['values'], 
                index = aspect['values'].index(st.session_state.get('selected_aspects', {}).get(aspect['name'], aspect['values'][0])) if st.session_state.get('selected_aspects', {}).get(aspect['name']) in aspect['values'] else 0)
                
            # Save the selected aspect in session state
            st.session_state.selected_aspects = selected_aspects

    # Media Section
    # Initialize images list in session state if not present
    if 'uploaded_images' not in st.session_state:
        st.session_state.uploaded_images = []

    # Display existing images with remove buttons
    i = 0
    while i < len(st.session_state.uploaded_images):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.session_state.uploaded_images[i]:
                st.image(st.session_state.uploaded_images[i], width=200)
        
        with col2:
            if st.button(f"Remove Image {i+1}"):
                st.session_state.uploaded_images.pop(i)
                save_session_state()
                st.rerun()
        i += 1

    # Single file uploader for new images
    uploaded_file = st.file_uploader("Add New Image", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        if uploaded_file not in st.session_state.uploaded_images:
            st.session_state.uploaded_images.append(uploaded_file)
            save_session_state()
            st.rerun()

    # Show a message if maximum images reached
    if len(st.session_state.uploaded_images) >= 24:
        st.warning("Maximum number of images (24) reached.")

    # Video upload
    video_file = st.file_uploader("Product Video", type=['mp4', 'mov', 'avi'])
    if video_file:
        st.video(video_file)    

    # Create listing button
    if st.button("Create Listing", type="primary", disabled=not st.session_state.auth_state == 'authorized'):
        if st.session_state.title and st.session_state.manufacturer and st.session_state.summary:
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
    
def display_suggestions(categories=None):
    if not categories:
        search_query = f"{st.session_state.title} {st.session_state.manufacturer}".strip()
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
            categories = [(suggestion['categoryTreeNodeAncestors'][0]['categoryName'],
            suggestion['category']['categoryId'],
            suggestion['category']['categoryName']) for suggestion in suggestions['categorySuggestions']]

            # Save the categories in session state
            st.session_state.categories = categories

            # Clear the previous selected category
            st.session_state.selected_category = None

