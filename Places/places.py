import streamlit as st
import googlemaps
import requests
from PIL import Image
from io import BytesIO
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Google Places and OpenAI API keys from .env
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set up Google Maps client
gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# Function to get place details using LangChain (via Wikipedia)
def get_place_details(place_name):
    prompt_template = PromptTemplate(
        input_variables=["place_name"],
        template="Tell me about the place {place_name} in detail.",
    )
    formatted_prompt = prompt_template.format(place_name=place_name)

    # Use LangChain OpenAI LLM to generate the response
    llm = OpenAI(api_key=OPENAI_API_KEY)
    return llm(formatted_prompt)

# Function to fetch places using Google Places API
def fetch_places(city):
    places_result = gmaps.places(query=f"Top places to visit in {city}")
    return places_result.get("results", [])

# Function to fetch place image from Google Places API
def fetch_place_image(photo_reference):
    # Correctly build the photo URL using the Google Places API photo_reference
    url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_API_KEY}"

    # Make a request to fetch the image
    response = requests.get(url)

    # Return an Image object if the response is valid
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        return None  # In case the image can't be fetched

# Function to fetch static map image using Maps Static API as fallback
def fetch_static_map(place_name):
    # Use Google Maps Static API to get a static map of the location
    static_map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={place_name}&zoom=14&size=400x400&key={GOOGLE_API_KEY}"

    # Request the map image
    response = requests.get(static_map_url)

    # Return an Image object if the response is valid
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        return None  # In case the image can't be fetched

# Streamlit App Interface
st.title("Best Places to Visit")

# Input city name
city = st.text_input("Enter the city name:", placeholder="e.g., Paris")

if city:
    st.header(f"Top places to visit in {city}")

    # Fetch places from Google Places API
    places = fetch_places(city)

    # Show each place in card format
    for place in places:
        place_name = place.get("name")
        photo_reference = place.get("photos", [{}])[0].get("photo_reference")

        if place_name:
            if photo_reference:
                # Fetch the image using the photo_reference
                place_image = fetch_place_image(photo_reference)
            else:
                # Fetch a static map image as a fallback
                place_image = fetch_static_map(place_name)

            if place_image:
                # Display place image or static map and name
                st.image(place_image, caption=place_name)
            else:
                # Fallback in case image can't be fetched
                st.write(f"Image not available for {place_name}")

            # Get place details using LangChain and Wikipedia
            place_details = get_place_details(place_name)

            with st.expander(f"Details about {place_name}"):
                st.write(place_details)
