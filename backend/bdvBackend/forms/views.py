from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from django.db.models import F, Count


from.models import Form, FormQuestion, Question, Option, Response

class IndexView(generic.ListView):
    template_name = 'forms/index.html'
    context_object_name = 'recent_question_list'

    def get_queryset(self):
        return (
            Question.objects
            .filter(created_date__lte=timezone.now())
            .annotate(options=Count('option'))
            .filter(options__gt=0)
            .order_by('-created_date')[:5]
        )

class FormView(generic.DetailView):
    model=Form
    template_name = 'forms/form.html'

    def get_queryset(self, form_id):
        return Question.objects.filter(formqs=form_id)


class ResponsesView(generic.DetailView):
    model=Question
    template_name = 'forms/responses.html'


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