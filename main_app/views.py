from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Cat, Toy, Photo
from .forms import FeedingForm
import boto3
import uuid

# Environment Variables
S3_BASE_URL = 'https://s3.us-east-1.amazonaws.com/'
BUCKET = 'cat-collector-persistence-danieljs'


# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def cats_index(request):
    cats = Cat.objects.all()
    return render(request,'cats/index.html', { 'cats': cats})

# update this view function
def cats_detail(request, cat_id):
  cat = Cat.objects.get(id=cat_id)
  # instantiate FeedingForm to be rendered in the template
  feeding_form = FeedingForm()

  # displaying unassociated toys
  toys_cat_doesnt_have = Toy.objects.exclude(id__in = cat.toys.all().values_list('id'))

  return render(request, 'cats/detail.html', {
    # include the cat and feeding_form in the context
    'cat': cat,
    'feeding_form': feeding_form,
    'toys' : toys_cat_doesnt_have,
  })

def add_feeding(request, cat_id):
    form = FeedingForm(request.POST)
    if form.is_valid():
        new_feeding = form.save(commit=False)
        new_feeding.cat_id = cat_id
        new_feeding.save()
    return redirect('detail', cat_id=cat_id)

def assoc_toy(request, cat_id, toy_id):
  # Note that you can pass a toy's id instead of the whole object
   Cat.objects.get(id=cat_id).toys.add(toy_id)
   return redirect('detail', cat_id=cat_id)










def add_photo(request, cat_id):
    # collect the file asset from the request
    photo_file = request.FILES.get('photo-file', None)
    # check if file is present
    if photo_file:
        # create a reference to the s3 service from boto3
        s3 = boto3.client('s3')
        # create a unique identifier for each photo asset
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # cute_cat.png => 3g3egg.png
        try:
            # attempt to upload image to aws
            s3.upload_fileobj(photo_file, BUCKET, key)
            # dynamically generate photo url
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            # create an in-memory reference to a photo model instance
            photo = Photo(url=url, cat_id=cat_id)
            # save the instance to the database
            photo.save()

        except Exception as error:
            print('*****************')
            print('An error has occurred with s3:')
            print(error)
            print('*****************')
    
    return redirect('detail', cat_id=cat_id)













class CatCreate(CreateView):
    model = Cat
    fields = '__all__'
    # success_url = '/cats/' 

class CatUpdate(UpdateView):
    model = Cat
    fields = ('breed', 'description', 'age')

class CatDelete(DeleteView):
    model = Cat
    success_url = '/cats/'

class ToyCreate(CreateView):
    model = Toy
    fields = ('name', 'color')

class ToyUpdate(UpdateView):
    model = Toy
    fields = ('name', 'color')

class ToyDelete(DeleteView):
    model = Toy
    success_url = '/toys/'

class ToyDetail(DetailView):
    model = Toy
    template_name = 'toys/detail.html'

class ToyList(ListView):
    model = Toy
    template_name = 'toys/index.html'