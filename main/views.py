from datetime import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic.base import TemplateView
from django_comments.models import Comment
from djangoratings.models import Vote
import json
from moviepy.editor import VideoFileClip
import numpy as np
import os
import random
import sagemaker
from sagemaker.predictor import RealTimePredictor
import torch
from tempfile import TemporaryFile

from .forms import LoginForm, RegisterForm, UploadForm
from .models import Dashboard_Message, Concept, Resource, Subject, Topic, TemporaryFileStorage, User
from base.settings import MEDIA_ROOT, SAGEMAKER_ENDPOINT_NAME

@login_required
def AccountClose(request):
    '''
    Closes a user's account
    '''
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.is_active = False
        user.save()
        return redirect('main:account-close-success')
    else:
        return render(request, 'main/account-close.html')

class AccountCloseSuccess(TemplateView):
    '''
    Confirms that the user's account has been closed successfully
    '''

    template_name = "main/account-close-success.html"

@login_required
def AccountPageView(request):
    '''
    A page for users to view and manage their account and related info, such as 
    resources they have rated
    '''
    previously_rated_resources = {}
    for vote in request.user.votes.all():
        resource = Resource.objects.get(pk=vote.object_id)
        previously_rated_resources[resource] = vote.score
    context={
        'previous_resources':previously_rated_resources,
    }
    return render(request, "main/account-page.html", context=context)

class ConfirmLogout(TemplateView):
    '''
    Asks the user to confirm that they want to logout
    '''

    template_name = "main/confirm-logout.html"

@login_required
def ConceptView(request, subject, topic, concept, number_of_comments=10, sort_comments_by='V'):
    '''
    The bread and butter page, shows resources recommended for a certain user for a certain concept.
    Recommendations are based on sequences of resources that users have rated or default to 
    recommending by average rating if the user hasn't rating anything
    '''
    subject_object = get_object_or_404(Subject, name=subject)
    topic_object = get_object_or_404(Topic, name=topic, subject__name=subject)
    concept_object = get_object_or_404(Concept, name=concept, subject__name=subject, topic__name=topic)
    if sort_comments_by == 'V': # sort_comments_by_votes will be set to 'T' if comments should be sorted by time
        sort_comments_by_votes = True
    else:
        sort_comments_by_votes = False
    matching_resources = Resource.objects.filter(subject__name=subject, topic__name=topic, concept__name=concept)
    previously_rated_resources = {}
    resource_pks = []
    for resource in matching_resources: 
        # Separate matching resources into previously_rated_resources and resource_pks (unrated resources)
        if resource.rating.get_rating_for_user(request.user):
            previously_rated_resources[resource] = resource.rating.get_rating_for_user(request.user)
        else:
            resource_pks.append(resource.pk)
    if resource_pks: #Checks if there are matching resources left to recommend
        no_more_resources = False
        no_resources = False
        user_votes = request.user.votes.all()
        timestamps0 = []
        vote_ids = []
        for vote in user_votes: 
            # Creates a list of all vote object id's involving the user and another list of the associated timestamps
            if vote.score > 3:
                timestamps0.append(vote.date_changed)
                vote_ids.append(vote.object_id)
        timestamps1 = []
        for dt in timestamps0:
            timestamps1.append(dt.replace(tzinfo=timezone.utc).timestamp())
        order_of_timestamps = np.argsort(timestamps1)
        user_sequence = []
        for number in order_of_timestamps:
            user_sequence.append(vote_ids[number])
        if not user_sequence: 
            # The user has not rated anything above a 3, in this case, recommend the highest rated resources
            matching_resource_ratings = [] # Will hold average rating of unrated resources
            for pk in resource_pks:
                resource = matching_resources.get(pk=pk)
                if resource.rating.votes == 0: # If a resource has no votes, append a rating of 0
                    matching_resource_ratings.append(0)
                else: # Append it's average rating
                    matching_resource_ratings.append(resource.rating.score/resource.rating.votes)
            array_ratings = np.array(matching_resource_ratings)
            recommendation_order = np.argsort(-array_ratings) # Get the indices of the array by highest average rating
            recommendation_pks = []
            for number in recommendation_order: # Create a list of pks from the sorted indices
                recommendation_pks.append(resource_pks[number])
            recommendation_pks = recommendation_pks[0:5] # Take the top 5 to recommend to the user
            recommendations = [] # Create a list of objects for context
            for pk in recommendation_pks:
                recommendations.append(matching_resources.get(pk=pk))
        else: # Get recommendations from model
            for i in range(len(user_sequence)): # Remove pk's that the last trained model can't handle
                if user_sequence[i] > os.environ['Highest_safe_pk']:
                    del user_sequence[i]
            if torch.cuda.is_available(): #Load the model
                with open(os.path.join(MEDIA_ROOT, 'model'), 'rb') as f: 
                    model = torch.load(f)
            else:
                with open(os.path.join(MEDIA_ROOT, 'model'), 'rb') as f:
                    model = torch.load(f, map_location='cpu')
            scores = model.predict(user_sequence)
            score_array = np.array(scores)
            np_recommendation_pks = np.argsort(-score_array) # Sort the array by score
            recommendation_pks = list(np_recommendation_pks)
            for resource in previously_rated_resources.keys(): 
                # Remove resources that have already been rated from recommendations
                if resource.pk in recommendation_pks:
                    recommendation_pks.remove(resource.pk)
            recommendations = []
            for pk in recommendation_pks: # Take only resources that match the concept being shown
                for resource in matching_resources:
                    if resource.pk == pk:
                        recommendations.append(resource)
            recommendations = recommendations[0:5] # Take the first 5 recommendations to present to the user
    elif not matching_resources: # We don't have any resources for this concept
        no_more_resources = False
        no_resources = True
        recommendations = None
    else: # The user has already rated all resources for this concept
        no_more_resources = True
        no_resources = False
        recommendations = None
    context = {
        'concept':concept_object,
        'no_more_resources':no_more_resources,
        'no_resources':no_resources,
        'number_of_comments':number_of_comments,
        'previous_resources':previously_rated_resources,
        'recommendations':recommendations,
        'sort_comments_by_votes':sort_comments_by_votes,
        'subject':subject_object,
        'topic':topic_object,
    }
    return render(request, "main/concept.html", context=context)

@login_required
def CreatorView(request):
    '''
    A page for creators to view and manage their uploads
    '''
    if request.user.is_creator:
        user_uploads = request.user.resource_set.all()
        context = {
            'creator_page':True,
            'UploadForm':UploadForm(initial={'title':'','creator':request.user}),
            'user_uploads':user_uploads,
        }
        return render(request, "main/creator.html", context=context)
    else: # If the user is not a creator, throw an error message and return them to the account page
        messages.error(request, 'You need to be a creator to view that page')
        return redirect('main:account')

@login_required
def CreatorPublicView(request, creator_id):
    '''
    Shows a public page with all videos uploaded by a certain creator
    '''
    user = get_object_or_404(User, pk=creator_id)
    if user.is_creator:
        context = {
            'creator':user,
            'creator_uploads':user.resource_set.all().order_by('upload_date') 
            # Newest uploads will show at the top of the page
        }
        return render(request, "main/public-creator.html", context=context)
    else: # Throw a 404 if the user is not a creator
        raise Http404("That user is not a creator")

@login_required
def DashboardView(request):
    '''
    Presents a dashboard showing all subjects and topics 
    along with a message that may or may not be present
    '''
    try:
        dashboard_message = Dashboard_Message.objects.latest('created') 
        #Only one message should be expected to exist at a time but we take the latest as a precaution
    except ObjectDoesNotExist:
        dashboard_message = None
    context ={
        'dashboard_message':dashboard_message,
        'subjects':Subject.objects.order_by('name'),
        'topics':Topic.objects.order_by('name'),
    }
    return render(request, "main/dashboard.html", context=context)

def load_concepts(request): 
    '''
    Returns a list of applicable concepts after a user choices a topic 
    when uploading a resource. 
    The request will be AJAX
    '''
    topic_id = request.GET.get('topic')
    concepts = Concept.objects.filter(topic_id=topic_id).order_by('name')
    return render(request, 'main/dropdown_options.html', {'options':concepts})

def load_topics(request):
    '''
    Returns a list of applicable topics after a user choices a subject 
    when uploading a resource. 
    The request will be AJAX
    '''
    subject_id = request.GET.get('subject')
    topics = Topic.objects.filter(subject_id=subject_id).order_by('name')
    return render(request, 'main/dropdown_options.html', {'options':topics})

def LoginPageView(request):
    '''
    Present a form to login or register and processes a user logging in
    '''
    if request.method == 'POST':

        redirect_to = request.POST.get('next')

        login_form = LoginForm(request.POST)

        if login_form.is_valid():

            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']

            user = authenticate(email=email, password=password)
            if user is not None:
                #User is authenticated
                login(request, user)
                if redirect_to:
                    return redirect(redirect_to)
                else:
                    return redirect('main:dashboard')
            else:
                #User is not authenticated
                request.session['email'] = email
                messages.error(request, 'Your email or password was incorrect, please try again')
                return redirect('main:login')
        else: 
            messages.error(request, 'Form invalid, please try again')
            return redirect('main:login')
    else:
        if request.user.is_authenticated:
            messages.error(request, 
                "You're already logged in, \
                you'll need to logout if you want to login in with another account or register a new account"
                )
            if 'show_register_form_first' in request.session:
                del request.session['show_register_form_first']
            return redirect('main:confirm-logout')
        else:
            if 'email' in request.session:
                email = request.session['email']
            else:
                email = None
            context = {
                'email':email,
                'LoginForm':LoginForm,
                'RegisterForm':RegisterForm,
            }
            if 'show_register_form_first' in request.session:
                context['show_register_form_first'] = True
                del request.session['show_register_form_first']
            return render(request, 'main/login.html', context)

def LogoutSuccessView(request):
    '''
    Show a message that the user has been logged out then redirect to the login page
    '''
    if not get_messages(request): 
        # The only other message that should be present is the time out message, 
        # in which case, the user has not chosen to logout, so the message won't be shown
        messages.error(request, "You have been logged out successfully")
    return redirect('main:login')

def MailView(request):
    '''
    A shortcut to get to the Chiron Learning email account
    '''
    return redirect('https://chiron-learning.awsapps.com/mail')

class PasswordResetSuccessView(TemplateView):
    '''
    Show that the user's password has been reset successfully
    '''

    template_name = "main/password-reset-success.html"

@login_required
def RatingView(request):
    '''
    Add or change a rating for a resource
    '''
    if request.method == 'POST':

        concept = request.POST.get('concept')
        topic = request.POST.get('topic')
        subject = request.POST.get('subject')
        resource = request.POST.get('resource')

        resource_object = Resource.objects.get(
            embed_link=resource, concept__name=concept, topic__name=topic, subject__name=subject
            )

        number_of_comments = int(request.POST.get('number_of_comments')) 
        # How many comments to show after being redirected back
        sort_comments_by = request.POST.get('sort_comments_by')

        rating = request.POST.get('rating')

        if rating == '1-star':
            rating = 1
        elif rating == '2-stars':
            rating = 2
        elif rating == '3-stars':
            rating = 3
        elif rating == '4-stars':
            rating = 4
        elif rating == '5-stars':
            rating = 5
        else:
            return redirect('main:concept', 
            subject=resource_object.subject.name, 
            topic=resource_object.topic.name, 
            concept=resource_object.concept.name, 
            number_of_comments=number_of_comments,
            sort_comments_by=sort_comments_by)
        
        resource_object.rating.add(score=rating, user=request.user)
        resource_object.save()

        return redirect('main:concept', 
            subject=resource_object.subject.name, 
            topic=resource_object.topic.name, 
            concept=resource_object.concept.name, 
            number_of_comments=number_of_comments,
            sort_comments_by=sort_comments_by)
    else: # There's no reason a get request should be sent to this address so just sent them to the dashboard
        return redirect('main:dashboard')

def RegisterView(request):
    '''
    Register a new user
    '''
    if request.method == 'POST':
        
        register_form = RegisterForm(request.POST)

        if register_form.is_valid():

            password = register_form.cleaned_data['set_password']
            confirm_password = register_form.cleaned_data['confirm_password']

            # Check also done in browser before form submit
            if password == confirm_password:

                email = register_form.cleaned_data['email']
                username = register_form.cleaned_data['username']

                try: # Create the user
                    User.objects.create_user(username, email, password)
                except: # An error will be thrown if a user already exists with those credentials
                    messages.error(request, 'A user with that email or username already exists')
                    return redirect('main:register')

                user = authenticate(email=email, password=password)
                if user is not None:
                    # User is authenticated
                    login(request, user)
                    return redirect('main:dashboard')
                else: 
                    #User is not authenticated even though the user was just created so something weird happened
                    messages.error(request, "Something went wrong, please try again")
                    return redirect('main:register')
            else:
                messages.error(request, "The passwords you entered didn't match, please try again.")
                return redirect('main:register')
        else:
            messages.error(request, 'Form was not valid, please try again')
            return redirect('main:register')
    else: # Redirect to the login page, but with the registration form showing
        request.session['show_register_form_first'] = True
        return redirect('main:login')

@login_required
def SubjectView(request, subject, number_of_comments=10, sort_comments_by='V'):
    '''
    Shows all topics available for a given subject
    '''
    subject_object = get_object_or_404(Subject, name=subject)
    if sort_comments_by == 'V':
        sort_comments_by_votes = True
    else:
        sort_comments_by_votes = False
    context = {
        'number_of_comments':number_of_comments,
        'sort_comments_by_votes':sort_comments_by_votes,
        'subject':subject_object,
        'topics':subject_object.topic_set.order_by('name'),
    }
    return render(request, "main/subject.html", context=context)

def TimeoutView(request):
    '''
    Tells a user that their session has timed out then redirects to the login page
    '''
    messages.error(request, "Your session has timed out due to inactivity")
    return redirect('main:logout')

@login_required
def TopicView(request, subject, topic, number_of_comments=10,sort_comments_by='V'):
    '''
    Shows all concepts available for a given topic
    '''
    subject_object = get_object_or_404(Subject, name=subject)
    topic_object = get_object_or_404(Topic, name=topic, subject__name=subject)
    if sort_comments_by == 'V':
        sort_comments_by_votes = True
    else:
        sort_comments_by_votes = False
    context = {
        'concepts':topic_object.concept_set.order_by('name'),
        'number_of_comments':number_of_comments,
        'sort_comments_by_votes':sort_comments_by_votes,
        'subject':subject_object,
        'topic':topic_object,
    }
    return render(request, "main/topic.html", context=context)

@login_required
def UpdateResourceView(request, resource_pk):
    '''
    Updates a given resource
    '''
    if request.method == 'POST':
        context = {

        }
        return
    else:
        resource = get_object_or_404(Resource, pk=resource_pk)
        if request.user == resource.creator:
            context = {

            }
            return render(request, "main/update-resource")
        else:
            raise Http404("You can only edit resources that you uploaded")

@login_required
def UploadView(request):
    '''
    Handles uploading new resources
    '''
    if request.method == 'POST':

        if request.is_ajax():
            # Save the uploaded file to the TemporaryFileStorage object for that user
            temp_storage, created = TemporaryFileStorage.objects.get_or_create(creator=request.user)
            vid = request.FILES['upload']
            clip = VideoFileClip(vid.temporary_file_path())
            if clip.duration > 3600: # Videos should be shorter than 1 hour
                clip.close()
                messages.error(request, 'Videos must be shorter than 1 hour')
                return JsonResponse({'success':False})
            clip.close()
            if created: # Put the newly uploaded file into temporary storage
                temp_storage.upload = request.FILES['upload']
                temp_storage.save(update_fields=['upload'])
            else: # Delete the old file and upload the new
                temp_storage.upload.delete()
                temp_storage.upload = request.FILES['upload']
                temp_storage.save(update_fields=['upload'])
            request.session['temp_upload'] = created
            return JsonResponse({'success':True})
        if 'temp_upload' in request.session: # Use the temporarily saved object as the file object
            temp_file = TemporaryFileStorage.objects.get(creator=request.user)
            file_data = {
                'upload': SimpleUploadedFile(temp_file.upload.name, temp_file.upload.read())
                } 
            # The above is currently just here to pass form validation
            temp_file.upload.close() # Clean-up from calling read()
            form = UploadForm(request.POST, file_data)
            if form.is_valid(): # Save the new resource after renaming the temporarily saved file
                old_path = os.path.join(MEDIA_ROOT, temp_file.upload.name)
                new_relative_path = 'user_{0}/{1}.mp4'.format(temp_file.creator.id, form.cleaned_data['title'])
                new_path = os.path.join(MEDIA_ROOT, new_relative_path)
                os.rename(old_path, new_path) # Rename the file to match the resource syntax
                temp_file.delete()
                unsaved_resource = Resource() # Create object manually to get proper file behavior
                unsaved_resource.upload.name = new_relative_path
                unsaved_resource.title = form.cleaned_data['title']
                unsaved_resource.creator = form.cleaned_data['creator']
                unsaved_resource.subject = form.cleaned_data['subject']
                unsaved_resource.topic = form.cleaned_data['topic']
                unsaved_resource.concept = form.cleaned_data['concept']
                try: # Save the object
                    unsaved_resource.save()
                    messages.success(request, 'Your upload was successful')
                except: # Something weird happens
                    unsaved_resource.delete()
                    os.remove(new_path)
                    messages.error(request, "The upload couldn't be saved")
                return redirect('main:creator')
            else:
                messages.error(request, "We can't process that upload, make sure your title is unique")
                return redirect('main:creator')
        else: # The file will be uploaded upon submit
            form = UploadForm(request.POST, request.FILES)
        if form.is_valid(): # Files should be uploaded using ajax but we leave this here as a precaution
            unsaved_resource = form.save(commit=False)
            vid = request.FILES['upload']
            clip = VideoFileClip(vid.temporary_file_path())
            if clip.duration > 3600:
                clip.close()
                unsaved_resource.delete()
                messages.error(request, 'Videos must be shorter than 1 hour')
                return redirect('main:creator')
            else:
                clip.close()
                form.save()
                messages.success(request, 'The upload was successful')
                return redirect('main:creator')
        else:
            messages.error(request, 'The form was invalid, make sure all fields are filled out')
            return redirect('main:creator')
    else:
        return redirect('main:creator')