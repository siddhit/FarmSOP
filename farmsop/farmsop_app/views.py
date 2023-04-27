import openai
from django.shortcuts import render
from .forms import CropForm

# Create your views here.
# This code defines a create_crop view that uses the CropForm form we defined earlier. The view checks if the form has been submitted and if it's valid, it saves the form and creates a new instance of the CropForm form. The view then renders the create_crop.html template with the form as the context.


def create_crop(request):
  form = CropForm(request.POST or None)

  if form.is_valid():
    crop = form.cleaned_data['crop']
    postal_code = form.cleaned_data['postal_code']

    #Call the OpenAI API to get the SOP
    sop = get_sop(postal_code, crop)
    
    #Save the form to the database
    form.save()
    form = CropForm()

    context = {'form': form, 'sop': sop}
    return render(request, 'create_crop.html', context)

  context = {'form': form}
  return render(request, 'create_crop.html', context)

def get_sop(postal_code, crop):
  #Set up the OpenAI API Client with your API Key
  openai.api_key = "PUT KEY HERE TOMORRW"

  #Use the OpenAI API to generate an SOP based on the crop and location
  prompt = f"Generate an SOP for growing {crop} in {postal_code}"
  response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=prompt,
    temperature=0.5,
    max_tokens=1024,
    n=1,
    stop=None,
    timeout=10,
    
  )

  #Extract the SOP from the API response
  sop = response.choices[0].text.strip()

  return sop
