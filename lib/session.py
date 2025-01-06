import streamlit as st
import pickle
import os

def save_session_state():
    with open('session_state.pkl', 'wb') as f:
        # # Dump session state except for 'navigation_radio' key
        # state_to_save = {key: value for key, value in st.session_state.items() if key != 'navigation_radio'}
        # pickle.dump(state_to_save, f)

        # Dump session state to a file
        pickle.dump(dict(st.session_state), f)

def load_session_state():
    if os.path.exists('session_state.pkl'):
        with open('session_state.pkl', 'rb') as f:
            saved_state = pickle.load(f)
            for key, value in saved_state.items():
                st.session_state[key] = value

def logout():
    # st.session_state.clear()
    st.session_state.pop('callback_auth_code', None)
    st.session_state.pop('auth_state', None) 
    st.session_state.pop('ebay_client', None)
    st.session_state.pop('ebay_production', None)
    st.session_state.pop('ebay_sandbox', None)

    save_session_state()
    # os.remove('session_state.pkl')
    st.rerun()