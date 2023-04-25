import openai
from django.shortcuts import render
from .forms import CropForm
import nltk
from typing import List
from geopy.geocoders import Nominatim

# Create your views here.
# This code defines a create_crop view that uses the CropForm form we defined earlier. The view checks if the form has been submitted and if it's valid, it saves the form and creates a new instance of the CropForm form. The view then renders the create_crop.html template with the form as the context.

#Get location from postal code and assign to region to make sure it's right.
def get_region(postal_code):
    geolocator = Nominatim(user_agent="FarmSOP")
    location = geolocator.geocode(postal_code)
    return location.address.split(",")[-2].strip()


def create_crop(request):
    # Create a CropForm instance and bind it to the POST data if available
    form = CropForm(request.POST or None)

    if form.is_valid():
        # Get the values of the form fields
        crop = form.cleaned_data['crop']
        postal_code = form.cleaned_data['postal_code']
        region = get_region(postal_code)
        
        # Get the optional fields from the form data, if they exist
        soil_type = form.cleaned_data.get('soil_type')
        soil_pH_level = form.cleaned_data.get('soil_pH_level')

        # Call the OpenAI API to get the SOP, including the new optional fields
        sop = get_sop(postal_code, crop, region, soil_type, soil_pH_level)
        
        # Save the form to the database
        form.save()

        # Reset the form for a new entry
        form = CropForm()

        # Create a context dictionary with the form and SOP data
        context = {'form': form, 'sop': sop}

        # Render the template with the context data
        return render(request, 'create_crop.html', context)

    # If the form is not valid, create a context dictionary with the form data only
    context = {'form': form}

    # Render the template with the context data
    return render(request, 'create_crop.html', context)



def get_sop(postal_code, crop, region, soil_type=None, soil_pH_level=None):
    # Set up the OpenAI API Client with your API Key
    openai.api_key = "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"

    # Use geocoding to extract the region from the postal code
    geolocator = Nominatim(user_agent="farmsop")
    location = geolocator.geocode(postal_code, addressdetails=True, language='en')
    region = location.raw['address']['state']

    # Use the OpenAI API to generate an SOP based on the crop, location, and optional fields
    prompt = f"Write a standard operating procedure (SOP) for growing {crop} in {postal_code}, {region}, based on publicly available data sources. "
    if soil_type:
        prompt += f"Include {soil_type} soil type and "
    if soil_pH_level:
        prompt += f"{soil_pH_level} pH level information to optimize the SOP, if available. "
    prompt += "The SOP should cover all aspects of crop growth including soil preparation, irrigation, fertilization, and pest control. "
    prompt += f"If available, include weather data and other relevant input parameters for the {postal_code} area to provide a more accurate SOP. "
    prompt += "The SOP should be available in English and Gujarati, and preferably have links to images that the app can render to assist with visualizing the steps. "
    prompt += "Please note that the final decision to use the SOP rests with the user, and a professional agronomist should be consulted if the SOP does not seem to be suitable for their specific situation."
    
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.5,
        max_tokens=1024,
        n=1,
        stop=None,
        timeout=10,
    )

    # Extract the SOP from the API response and split it into steps using a tokenizer
    sop = response.choices[0].text.strip()
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sop_steps = tokenizer.tokenize(sop)

    # Format the SOP by adding line numbers and spacing
    sop_formatted = ""
    for i, step in enumerate(sop_steps, 1):
        sop_formatted += f"{i}. {step}\n\n"

    return sop_formatted

