import google.generativeai as genai
import json

def compose_listing(title, manufacturer, summary):
    genai.configure(api_key=st.secrets['GOOGLE_API_KEY'])

    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    response = model.generate_content(
        f'Generate an eBay listing following product {title} \
            Manufacturer: {manufacturer} \
            Summary: {summary} \
            The listing should be attractive and inducing, but not misleading. \
            Always encourage customers to purchase. \
            Format the response as json with keys title and description. \
        '
    )

    return json.loads(response.text)
    