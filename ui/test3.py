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
import openai

GOOGLE_API_KEY = ''
OPENAI_API_KEY = ''

gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

from header import animated_text

animated_text("AI Travel Agent")

# Initialize Langchain OpenAI and Wikipedia wrappers
llm = OpenAI(temperature=0.7, openai_api_key=OPENAI_API_KEY)
wiki = WikipediaAPIWrapper()


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


# Function to get ticket prices using GPT-3.5 Turbo
def get_ticket_price_from_gpt(place_name, description):
    openai.api_key = OPENAI_API_KEY

    prompt = f"""
    Determine the ticket price for the following place. If the place is free, indicate that.
    Place: {place_name}
    Description: {description}

    Response format:
    - If the place is free: "Free"
    - If there is a ticket price: "<Price> <Currency>"
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides ticket price information."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message['content'].strip()


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

# City Input Section
city = st.text_input("Enter the city name:", placeholder="e.g., Paris")

if city:
    st.markdown(f"<h1 class='animated-title'>Top places to visit in {city}</h1>", unsafe_allow_html=True)

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
            place_description = place.get("formatted_address", "No description available")
            photo_reference = place.get("photos", [{}])[0].get("photo_reference")

            # Fetch the image of the place
            place_image = fetch_place_image(photo_reference)
            img_str = ""
            if place_image:
                img_str = image_to_base64(place_image)

            # Get Wikipedia details and truncate the content
            wiki_details = get_wikipedia_details(place_name)
            wiki_details_truncated = wiki_details[:500] + "..." if len(wiki_details) > 500 else wiki_details

            # Get ticket price using GPT-3.5 Turbo
            ticket_price = get_ticket_price_from_gpt(place_name, place_description)

            # Display a flip card with image, Wikipedia details, and ticket price
            st.markdown(f"""
                <div class="flip-card">
                  <div class="flip-card-inner">
                    <div class="flip-card-front">
                      {"<img src='data:image/png;base64," + img_str + "' class='place-image'/>" if img_str else ''}
                      <div class="place-title">{place_name}</div>
                      <div class="place-price">Ticket Price: {ticket_price}</div>
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
