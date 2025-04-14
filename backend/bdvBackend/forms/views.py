from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone

from django.db.models import F


from.models import Question, Option, Response


def index(request):
    recent_question_list = Question.objects.order_by("-created_date")[:5]
    template = loader.get_template('forms/index.html')
    context = {'recent_question_list':recent_question_list}
    return HttpResponse(template.render(context, request))

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "forms/detail.html", {"question": question})

def respond(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_option = question.option_set.get(pk=request.POST['option'])
    except(KeyError, Option.DoesNotExist):
        return render(request, 'forms/detail.html',
                    {'question':question, 'error_message':'You did not select a response.'},)
    else:
        response = Response(option=selected_option, response_date=timezone.now())
        response.save()
        return HttpResponseRedirect(reverse("forms:responses", args=(question.id,)))

def responses(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "forms/responses.html", {"question": question})