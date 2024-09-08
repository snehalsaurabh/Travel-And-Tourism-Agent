import streamlit as st
import googlemaps
import requests
from PIL import Image
from io import BytesIO
import base64
import folium
from streamlit_folium import st_folium
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.utilities import WikipediaAPIWrapper

# OpenAI and Google API keys
#GOOGLE_API_KEY =
#OPENAI_API_KEY =


# Initialize Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# Initialize Langchain OpenAI and Wikipedia wrappers
llm = OpenAI(temperature=0.7, openai_api_key=OPENAI_API_KEY)
wiki = WikipediaAPIWrapper()

# Custom CSS for card flip effect and animated title
st.markdown("""
    <style>
    .animated-title {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        animation: slideIn 2s ease-out;
    }

    @keyframes slideIn {
        from {
            transform: translateX(-100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .card-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        gap: 20px;
        padding: 20px;
    }

    .flip-card {
        background-color: transparent;
        width: 100%;
        max-width: 300px;
        height: 400px;
        perspective: 1000px;
        margin-bottom: 20px;
    }

    .flip-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.6s;
        transform-style: preserve-3d;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    }

    .flip-card:hover .flip-card-inner {
        transform: rotateY(180deg);
    }

    .flip-card-front, .flip-card-back {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
    }

    .flip-card-front {
        background-color: #fff;
        color: black;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .flip-card-back {
        background-color: #2980b9;
        color: white;
        transform: rotateY(180deg);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        padding: 20px;
    }

    .place-image {
        width: 100%;
        height: 200px;
        border-radius: 12px;
        object-fit: cover;
    }

    .place-title {
        font-size: 24px;
        font-weight: bold;
        margin-top: 10px;
    }

    .place-details {
        padding: 10px;
        font-size: 14px;
        text-align: left;
        overflow-y: auto;
        height: 200px;
    }
    </style>
""", unsafe_allow_html=True)


# Function to convert image to base64 format
def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


# Function to fetch place images from Google Places API
def fetch_place_image(photo_reference):
    url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    return None


# Function to get top places using Google Places API
def fetch_places(city):
    places_result = gmaps.places(query=f"Top places to visit in {city}")
    return places_result.get("results", [])


# Function to fetch Wikipedia details of a place
def get_wikipedia_details(place_name):
    result = wiki.run(place_name)
    return result

import requests

# # Function to fetch ticket price using RapidAPI
# def get_ticket_price_rapidapi(place_name):
#     url = "https://viator-api.p.rapidapi.com/products/search"
    
#     # Your RapidAPI key
#     headers = {
#         "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",
#         "X-RapidAPI-Host": "viator-api.p.rapidapi.com"
#     }
    
#     # Parameters to pass to the API (this will vary based on the API you are using)
#     querystring = {"query": place_name}

#     # Make the request
#     response = requests.get(url, headers=headers, params=querystring)

#     # Check if the request was successful
#     if response.status_code == 200:
#         data = response.json()
#         # Parse ticket price (this will depend on the specific API's response structure)
#         if data and data.get("data"):
#             ticket_price = data["data"][0].get("retail_price", "Price not available")
#             return ticket_price
#         else:
#             return "Price not available"
#     else:
#         return "Price not available


def get_content_id(place_name):
    url = "https://your-rapidapi-endpoint.com/get-content-id"
    headers = {
        "X-RapidAPI-Key": "your-rapidapi-key",
        "X-RapidAPI-Host": "your-rapidapi-host"
    }
    querystring = {"place_name": place_name}

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        # Assuming the API response has a "content_id" field
        return response.json().get("content_id")
    else:
        print(f"Error fetching content ID for {place_name}: {response.status_code}")
        return None


# Example usage
place_name = "New York"
content_id = get_content_id(place_name)
if content_id:
    print(f"Content ID for {place_name} is: {content_id}")
else:
    print(f"Could not find content ID for {place_name}")



def get_ticket_price_rapidapi(content_type, content_id):
    url = "https://travel-advisor.p.rapidapi.com/answers/v2/list"
    
    querystring = {"currency":"USD","units":"km","lang":"en_US"}

    payload = {
        "contentType": ,  # Can be 'hotel', 'attraction', etc.
        "contentId": content_id,      # ID of the place you're querying
        "questionId": "8393250",      # Example question ID
        "pagee": 0,
        "updateToken": ""
    }
    headers = {
        "x-rapidapi-key": "c20c9b3c32msh0ad0c7f2f2e2169p143c7bjsn1dfa4eb0c1c6",
        "x-rapidapi-host": "travel-advisor.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    # Make the request
    response = requests.post(url, json=payload, headers=headers, params=querystring)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Assuming ticket price or info is in the response
        if "data" in data:
            return data.get("data", "Price or info not available")
        else:
            return "Price or info not available"
    else:
        return "Error: Unable to fetch ticket info"


# City Input Section
city = st.text_input("Enter the city name:", placeholder="e.g., Paris")

if city:
    st.markdown("<h1 class='animated-title'>Top places to visit in {city}</h1>", unsafe_allow_html=True)

    # Fetch places
    places = fetch_places(city)

    if places:
        first_place_lat, first_place_lng = places[0]['geometry']['location']['lat'], places[0]['geometry']['location'][
            'lng']

        # Folium map
        m = folium.Map(location=[first_place_lat, first_place_lng], zoom_start=12)
        for place in places:
            place_name = place.get("name")
            lat = place['geometry']['location']['lat']
            lng = place['geometry']['location']['lng']
            folium.Marker([lat, lng], popup=place_name).add_to(m)

        # Display the map in Streamlit
        st_folium(m, width=700, height=500)

        # Display places in flip cards - three per row
        st.markdown("<div class='card-container'>", unsafe_allow_html=True)

        for place in places:
            place_name = place.get("name")
            place_details = place.get("formatted_address", "No details available")
            photo_reference = place.get("photos", [{}])[0].get("photo_reference")

            # Fetch the image of the place
            place_image = fetch_place_image(photo_reference)
            img_str = ""
            if place_image:
                img_str = image_to_base64(place_image)

            # Get Wikipedia details and truncate the content
            wiki_details = get_wikipedia_details(place_name)
            wiki_details_truncated = wiki_details[:500] + "..." if len(wiki_details) > 500 else wiki_details

            # Fetch the ticket price for the place
            # ticket_price = get_ticket_price_rapidapi(place_name)
            ticket_price = get_ticket_price_rapidapi(place_name,content_id)

            # Display a flip card with image and Wikipedia details
            st.markdown(f"""
                <div class="flip-card">
                  <div class="flip-card-inner">
                    <div class="flip-card-front">
                      {"<img src='data:image/png;base64," + img_str + "' class='place-image'/>" if img_str else ''}
                      <div class="place-title">{place_name}</div>
                    </div>
                    <div class="flip-card-back">
                      <div class="place-details">{wiki_details_truncated}</div>
                    </div>
                  </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # Close the card container
    else:
        st.write(f"No places found for {city}")
