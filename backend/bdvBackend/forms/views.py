from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader

from.models import Question


def index(request):
    recent_question_list = Question.objects.order_by("-created_date")[:5]
    template = loader.get_template('forms/index.html')
    context = {'recent_question_list':recent_question_list}
    return HttpResponse(template.render(context, request))

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "forms/detail.html", {"question": question})

def responses(request, question_id):
    response = "You're looking at the responses to question %s."
    return HttpResponse(response % question_id)


def respond(request, question_id):
    return HttpResponse("You're responding to question %s." % question_id)