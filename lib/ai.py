import streamlit as st

import google.generativeai as genai
import json

def compose_listing(title, manufacturer, summary):
    genai.configure(api_key=st.secrets['GOOGLE_API_KEY'])

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        f'''
        Write an eBay product listing for the product {title} manufactured by {manufacturer} 
        with the following summary: {summary}. Make the listing attractive and persuasive, 
        encouraging customers to purchase, but ensure it is accurate and not misleading. 
        Format the response as a pure JSON object with the keys "title" and "description". 
        Do not include any additional text or format specifiers in the response.
        Do not add any markdown code fences (like ```json or ```) or any extra text outside the JSON object.
        '''
        )

    print(f'Gemini response: {response.text}')

    return json.loads(response.text)
    