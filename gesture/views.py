from collections import OrderedDict

from django.shortcuts import render, redirect
from django.http import HttpResponse, StreamingHttpResponse

# from .forms import NewUserForm
from django.contrib.auth import login, authenticate,logout
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm,LoginForm

from django.contrib.auth.decorators import login_required

# Create your views here.
from django.urls import reverse

from gesture.camera import VideoCamera
from gesture.models import GestureImage
from .fusioncharts import FusionCharts

ANSWERS = {
    'A': 5,
    'B': 4,
    'C': 3,
    'D': 2,
    'E': 1,
}

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'design/signup.html', {'form': form})

def login_page(request):
    forms = LoginForm()
    if request.method == 'POST':
        forms = LoginForm(request.POST)
        if forms.is_valid():
            username = forms.cleaned_data['username']
            password1 = forms.cleaned_data['password']
            user = authenticate(username=username, password=password1)
            if user:
                login(request, user)
                return redirect('home')
    context = {'form': forms}
    return render(request, 'design/login.html', context)

def logout_request(request):
    logout(request)
    # messages.info(request, "Logged out successfully!")
    return redirect("home")


@login_required(login_url='login')
def home(request):
    gesture_images = GestureImage.objects.all()
    return render(request, 'design/home.html', {'gesture_images': gesture_images})

@login_required(login_url='login')
def sign(request, id=None):
    gesture_image = GestureImage.objects.all()
    return render(request, 'design/sign.html', {'gesture_image': gesture_image})

@login_required(login_url='login')
def before_question(request):
    if "point" in request.session.keys():
        del request.session["point"]
    if "actual_time" in request.session.keys():
        del request.session["actual_time"]
    if "taken_time" in request.session.keys():
        del request.session["taken_time"]
    if "taken_seconds" in request.session.keys():
        del request.session["taken_seconds"]

    if request.method == "POST" and request.POST.get('type', '') == 'gesture':
        data = request.POST
        request.session['actual_time'] = data['actual_time']
        request.session['taken_time'] = data['taken_time']
        request.session['taken_seconds'] = data['taken_seconds']

    return redirect(reverse('question'))

@login_required(login_url='login')
def question(request):
    if request.method == "POST" and request.POST.get('type', '') == 'answers':
        data = request.POST
        point = ANSWERS[data['question-1-answers']]
        point += ANSWERS[data['question-2-answers']]
        point += ANSWERS[data['question-3-answers']]
        point += ANSWERS[data['question-4-answers']]
        point += ANSWERS[data['question-5-answers']]
        request.session['point'] = point

        return redirect(reverse('result'))
    return render(request, 'design/question.html')


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request):
    return StreamingHttpResponse(gen(VideoCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

@login_required(login_url='login')
def result(request):
    if "point" not in request.session.keys() and "actual_time" not in request.session.keys() and "taken_time" not in request.session.keys():
        return redirect(reverse('home'))

    dialValues = [str(request.session.get('point', 0))]

    # widget data is passed to the `dataSource` parameter, as dict, in the form of key-value pairs.
    dataSource = OrderedDict()

    # The `widgetConfig` dict contains key-value pairs of data for widget attribute
    widgetConfig = OrderedDict()
    widgetConfig["caption"] = "Gesture result chart"
    widgetConfig["lowerLimit"] = "0"
    widgetConfig["upperLimit"] = "25"
    widgetConfig["showValue"] = "1"
    widgetConfig["numberSuffix"] = "%"
    widgetConfig["theme"] = "fusion"
    widgetConfig["showToolTip"] = "0"
    widgetConfig["valueBelowPivot"] = "1"

    # The `colorData` dict contains key-value pairs of data for ColorRange of dial
    colorRangeData = OrderedDict()
    colorRangeData["color"] = [
       
        {
            "minValue": "0",
            "maxValue": "15",
            "code": "#62B58F"
        }, 
        
         {
            "minValue": "16",
            "maxValue": "25",
            "code": "#F2726F"
        },
        
    ]

    # Convert the data in the `dialData` array into a format that can be consumed by FusionCharts.
    dialData = OrderedDict()
    dialData["dial"] = []

    dataSource["chart"] = widgetConfig
    dataSource["colorRange"] = colorRangeData
    dataSource["dials"] = dialData

    # Iterate through the data in `dialValues` and insert into the `dialData["dial"]` list.
    # The data for the `dial`should be in an array wherein each element of the
    # array is a JSON object# having the `value` as keys.
    for i in range(len(dialValues)):
        dialData["dial"].append({
            "value": dialValues[i]
        })
    # Create an object for the angular-gauge using the FusionCharts class constructor
    # The widget data is passed to the `dataSource` parameter.

    angulargaugeWidget = FusionCharts("angulargauge", "myFirstWidget", "100%", "400", "myFirstwidget-container", "json", dataSource)
    context = {
        'point': request.session.get('point', 0),
        'actual_time': request.session.get('actual_time', 0),
        'taken_time': request.session.get('taken_time', "00:00:00"),
        'taken_seconds': request.session.get('taken_seconds', 0),
        'output': angulargaugeWidget.render()
    }
    return render(request, "design/result.html", context)
