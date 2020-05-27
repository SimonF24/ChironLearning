from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import ChangePasswordForm, CustomPasswordResetForm, CustomSetPasswordForm

app_name = 'main'
urlpatterns = [
  path('timed-out', views.TimeoutView, name='time-out'),
  path('update-resource/<int:resource_pk>', views.UpdateResourceView, name='update-resource'),
  path('upload', views.UploadView, name='upload'),
  # The above break alphabetical order since they have to be before the subject views or it gets read as a subject
  path('account', views.AccountPageView, name='account'),
  path('account/close', views.AccountClose, name='close-account'),
  path('account/close/success', views.AccountCloseSuccess.as_view(), name='account-close-success'),
  path('ajax/load-concepts/', views.load_concepts, name="load-concepts"),
  path('ajax/load-topics/', views.load_topics, name="load-topics"),
  path('change-password', auth_views.PasswordChangeView.as_view(
    template_name='main/change-password.html', success_url='/change-password/success', form_class=ChangePasswordForm
    ), name='change-password'),
  path('change-password/success', auth_views.PasswordChangeDoneView.as_view(
    template_name='main/change-password-success.html'
    ), name='change-password-success'),
  path('creator', views.CreatorView, name='creator'),
  path('creator/<int:creator_id>', views.CreatorPublicView, name='creator-public'),
  path('dashboard', views.DashboardView, name='dashboard'),
  path('login', views.LoginPageView, name='login'),
  path('logout', auth_views.LogoutView.as_view(), name='logout'),
  path('logout/confirm', views.ConfirmLogout.as_view(), name='confirm-logout'),
  path('logout/success', views.LogoutSuccessView, name='logout-success'),
  path('logout-then-login', auth_views.logout_then_login, name='logout-then-login'),
  path('mail', views.MailView, name='mail'),
  path('password-reset', auth_views.PasswordResetView.as_view(
    template_name='main/password-reset.html', form_class=CustomPasswordResetForm, email_template_name='main/password-reset-email.html', 
    subject_template_name='main/password-reset-email-subject.txt', success_url='/password-reset/success',
    ), name='password-reset'),
  path('password-reset/confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
    template_name='main/password-reset-confirm.html', form_class=CustomSetPasswordForm, success_url='/password-reset/done',
    ), name='password-reset-confirm'),
  path('password-reset/success', auth_views.PasswordResetDoneView.as_view(
    template_name='main/password-reset-success.html',
    ), name='password-reset-success'),
  path('password-reset/done', auth_views.PasswordResetCompleteView.as_view(
    template_name='main/password-reset-done.html',
    ), name='password-reset-done'),
  path('rate', views.RatingView, name='rating'),
  path('register', views.RegisterView, name='register'),
  path('<subject>', views.SubjectView, name='subject'),
  path('<subject>/<int:number_of_comments>', views.SubjectView, name='subject'),
  path('<subject>/<int:number_of_comments>/<sort_comments_by>', views.SubjectView, name='subject'),
  path('<subject>/<topic>', views.TopicView, name="topic"),
  path('<subject>/<topic>/<int:number_of_comments>', views.TopicView, name="topic"),
  path('<subject>/<topic>/<int:number_of_comments>/<sort_comments_by>', views.TopicView, name="topic"),
  path('<subject>/<topic>/<concept>', views.ConceptView, name='concept'),
  path('<subject>/<topic>/<concept>/<int:number_of_comments>', views.ConceptView, name='concept'),
  path('<subject>/<topic>/<concept>/<int:number_of_comments>/<sort_comments_by>', views.ConceptView, name='concept'),
]