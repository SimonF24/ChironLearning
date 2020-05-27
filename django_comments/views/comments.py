from __future__ import absolute_import

from django import http
from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.html import escape
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

import django_comments
from django_comments import signals
from django_comments.views.utils import next_redirect, confirmation_view
from django_comments.models import Comment


class CommentPostBadRequest(http.HttpResponseBadRequest):
    """
    Response returned when a comment post is invalid. If ``DEBUG`` is on a
    nice-ish error message will be displayed (for debugging purposes), but in
    production mode a simple opaque 400 page will be displayed.
    """

    def __init__(self, why):
        super(CommentPostBadRequest, self).__init__()
        if settings.DEBUG:
            self.content = render_to_string("comments/400-debug.html", {"why": why})


@csrf_protect
@require_POST
def post_comment(request, next=None, using=None):
    """
    Post a comment.

    HTTP POST is required. If ``POST['submit'] == "preview"`` or if there are
    errors a preview template, ``comments/preview.html``, will be rendered.
    """
    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()
    if request.user.is_authenticated:
        if not data.get('name', ''):
            data["name"] = request.user.username #request.user.get_full_name() or request.user.get_username()
        if not data.get('email', ''):
           data["email"] = request.user.email

    # Look up the object we're trying to comment about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    if ctype is None or object_pk is None:
        return CommentPostBadRequest("Missing content_type or object_pk field.")
    try:
        model = apps.get_model(*ctype.split(".", 1))
        target = model._default_manager.using(using).get(pk=object_pk)
    except TypeError:
        return CommentPostBadRequest(
            "Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return CommentPostBadRequest(
            "The given content-type %r does not resolve to a valid model." % escape(ctype))
    except ObjectDoesNotExist:
        return CommentPostBadRequest(
            "No object matching content-type %r and object PK %r exists." % (
                escape(ctype), escape(object_pk)))
    except (ValueError, ValidationError) as e:
        return CommentPostBadRequest(
            "Attempting go get content-type %r and object PK %r exists raised %s" % (
                escape(ctype), escape(object_pk), e.__class__.__name__))

    # Do we want to preview the comment?
    preview = "preview" in data

    # Construct the comment form
    form = django_comments.get_form()(target, data=data)

    # Check security information
    if form.security_errors():
        return CommentPostBadRequest(
            "The comment form failed security verification: %s" % escape(str(form.security_errors())))

    # If there are errors or if we requested a preview show the comment
    if form.errors or preview:
        template_list = [
            # These first two exist for purely historical reasons.
            # Django v1.0 and v1.1 allowed the underscore format for
            # preview templates, so we have to preserve that format.
            "comments/%s_%s_preview.html" % (model._meta.app_label, model._meta.model_name),
            "comments/%s_preview.html" % model._meta.app_label,
            # Now the usual directory based template hierarchy.
            "comments/%s/%s/preview.html" % (model._meta.app_label, model._meta.model_name),
            "comments/%s/preview.html" % model._meta.app_label,
            "comments/preview.html",
        ]
        return render(request, template_list, {
                "comment": form.data.get("comment", ""),
                "form": form,
                "next": data.get("next", next),
            },
        )

    # Otherwise create the comment
    comment = form.get_comment_object(site_id=get_current_site(request).id)
    comment.ip_address = request.META.get("REMOTE_ADDR", None) or None
    if request.user.is_authenticated:
        comment.user = request.user

    # Assign the parent comment if this comment is reply to another comment
    parent_comment_id = request.POST.get("parent_comment_id")
    if parent_comment_id:
        parent_comment_object = get_object_or_404(django_comments.get_model(),
                                pk=parent_comment_id,
                                site__pk=get_current_site(request).pk)
        comment.parent_comment = parent_comment_object

    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender=comment.__class__,
        comment=comment,
        request=request
    )

    for (receiver, response) in responses:
        if response is False:
            return CommentPostBadRequest(
                "comment_will_be_posted receiver %r killed the comment" % receiver.__name__)

    # Save the comment and signal that it was saved
    comment.save()
    signals.comment_was_posted.send(
        sender=comment.__class__,
        comment=comment,
        request=request
    )

    return next_redirect(request, fallback=next or 'comments-comment-done',
                         ) #c=comment._get_pk_val()) This is what was originally there


comment_done = confirmation_view(
    template="comments/posted.html",
    doc="""Display a "comment was posted" success page."""
)

@login_required
def comment_upvote(request, comment_id, next=None):
    comment = get_object_or_404(django_comments.get_model(),
                                pk=comment_id,
                                site__pk=get_current_site(request).pk)
    if comment.has_upvoted.filter(email=request.user.email).exists():
        # The user has already upvoted this comment
        pass
    elif comment.has_downvoted.filter(email=request.user.email).exists():
        # The user previously downvoted this comment
        comment.votes += 2
        comment.has_downvoted.remove(request.user)
        comment.has_upvoted.add(request.user)
    else:
        # The user has not previously upvoted or downvoted this comment
        comment.votes += 1 
        comment.has_upvoted.add(request.user)
    comment.save()
    return next_redirect(request, fallback=next)

@login_required
def comment_downvote(request, comment_id, next=None):
    comment = get_object_or_404(django_comments.get_model(),
                                pk=comment_id,
                                site__pk=get_current_site(request).pk)
    if comment.has_upvoted.filter(email=request.user.email).exists():
        # The user has already upvoted this comment
        comment.votes -= 2
        comment.has_upvoted.remove(request.user)
        comment.has_downvoted.add(request.user)
    elif comment.has_downvoted.filter(email=request.user.email).exists():
        # The user previously downvoted this comment
        pass
    else:
        # The user has not previously upvoted or downvoted this comment
        comment.votes -= 1
        comment.has_downvoted.add(request.user)
    comment.save()
    return next_redirect(request, fallback=next)

@login_required
def comment_cancel_vote(request, comment_id, next=None):
    comment = get_object_or_404(django_comments.get_model(),
                                    pk=comment_id,
                                    site__pk=get_current_site(request).pk)
    if comment.has_upvoted.filter(email=request.user.email).exists():
        # The user has already upvoted this comment
        comment.votes -= 1
        comment.has_upvoted.remove(request.user)
    elif comment.has_downvoted.filter(email=request.user.email).exists():
        # The user previously downvoted this comment
        comment.votes += 1
        comment.has_downvoted.remove(request.user)
    comment.save()
    return next_redirect(request, fallback=next)