import json
import requests
import streamlit as st
from itertools import product

import sys
import os

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lib.session import load_session_state

# Initialize session state variables
rerun_flag = False
st.session_state.title = None
st.session_state.manufacturer = None
st.session_state.image_url = None

# Create a Streamlit form for eBay product listing creation
def create_listing_form():
    st.markdown('<h2 style="text-align: center;">Create eBay Listing</h2>', unsafe_allow_html=True)
    
    # Product basic information
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input("Product Title", value=st.session_state.get('title') or '' ,placeholder="e.g. iPhone 15 Pro Max 256GB")
        manufacturer = st.text_input("Manufacturer", value=st.session_state.get('manufacturer') or '',placeholder="e.g. Apple")
        st.session_state.title = title
        st.session_state.manufacturer = manufacturer
        
    with col2:
        if image_url := st.text_input("Image URL", value=st.session_state.get('image_url') or '',placeholder="e.g. https://example.com/image.jpg"):
            st.image(image_url, caption="Product Image Preview", width=300)
            st.session_state.image_url = uploaded_image.getvalue()

    
    # Display suggestions button
    if st.button("Get Suggestions"):
        if st.session_state.title and st.session_state.manufacturer:
            print(f'title: {title}, manufacturer: {manufacturer}')
            display_suggestions()
        else:
            st.error("Please fill in required fields: Title and Manufacturer")
    elif 'categories' in st.session_state:
        display_suggestions(st.session_state.categories)
    
    # Create listing button
    if st.button("Create Listing", type="primary"):
        if st.session_state.title and st.session_state.manufacturer:
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
            st.error("User token is not available. Please log in.")
            return

        try:
            suggestions = st.session_state.ebay_production.get_category_suggestions(search_query)
        except ValueError as ve:
            st.error(f"Error: {ve}")
            return
        
        if 'categorySuggestions' in suggestions:
            categories = [(suggestion['categoryTreeNodeAncestors'][0]['categoryName'], 
                            suggestion['category']['categoryName']) 
                        for suggestion in suggestions['categorySuggestions']]

            # Save the categories in session state
            st.session_state.categories = categories

            # Clear the previous selected category
            st.session_state.selected_category = None
                        
    selected_category = st.selectbox(
        "Suggested Categories",
        options=categories,
        format_func=lambda x: f"{x[0]} > {x[1]}",
        index=st.session_state.categories.index(st.session_state.selected_category) if st.session_state.get('selected_category') else 0
    )

    # Save the selected category in session state
    st.session_state.selected_category = selected_category

