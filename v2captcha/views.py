from django.shortcuts import render
from .forms import CaptchaForm, UploadForm
from django.http import HttpResponse
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import Post
from django.core.exceptions import ObjectDoesNotExist
from skimage.util import random_noise
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import base64



# Create your views here.
def index(request):
    if request.method == 'POST':
        form = CaptchaForm(request.POST)
        if form.is_valid():

            # Handle the form submission, e.g., save data to the database
            return render(request, 'v2captcha/success.html')
    else:
        form = CaptchaForm()
    return render(request, 'v2captcha/index.html', {'form': form})



def upload_image(request):

    try:
        if request.method == "POST":
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
            
            post = Post.objects.latest('id')
            noisy = add_noise()

            return render(request=request, template_name="v2captcha/upload_image.html", context={'form':form, 'post':post, 'noisy':noisy})
        
        form = UploadForm()
        post = Post.objects.latest('id')
        noisy = add_noise()

        # print(post.values())
        return render(request=request, template_name="v2captcha/upload_image.html", context={'form':form, 'post':None})
    except ObjectDoesNotExist:
        return render(request=request, template_name="v2captcha/upload_image.html", context={'form':form, 'post':None})


def add_noise():
    
    noisy_images = []
    post = Post.objects.latest('id')

    imgpath = str(settings.BASE_DIR) + str(post.image.url)

    im = Image.open(imgpath)
    im_arr = np.array(im)


    noise_factor = 0.02


    noise_img = random_noise(im_arr, mode="s&p",clip=True, amount=noise_factor)

    noisy_images.append(["S&P", image_to_base64(noise_img)])

    noise_img = random_noise(im_arr, mode='Poisson', clip=True)

    noisy_images.append(["Poisson", image_to_base64(noise_img)])

    noise_img = random_noise(im_arr, mode='gaussian', clip=True)

    noisy_images.append(["Gaussian", image_to_base64(noise_img)])

    noise_img = random_noise(im_arr, mode='speckle', clip=True)

    noisy_images.append(["Speckle", image_to_base64(noise_img)])

    return noisy_images



def image_to_base64(image):
    image = Image.fromarray((image * 255).astype(np.uint8))
    buff = BytesIO()
    image.save(buff, format="PNG")
    img_str = base64.b64encode(buff.getvalue())
    img_str = img_str.decode("utf-8")  # convert to str and cut b'' chars
    return img_str
