from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import generic

from .forms import RespondentForm, SelectRespondentForm

import datetime
from django.db.models import F, Count


from.models import Respondent, Form, FormQuestion, Question, Option, Response

class IndexView(generic.ListView):
    template_name = 'forms/index.html'
    context_object_name = 'active_form'

    def get_queryset(self):
        return Form.objects.filter(start_date__lte= datetime.date.today(), end_date__gte = datetime.date.today())

class FormView(generic.DetailView):
    model=Form
    template_name = 'forms/form-detail.html'
    context_object_name = 'form_questions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_instance = self.get_object()
        formQs = FormQuestion.objects.filter(form=form_instance).order_by('index')
        form_questions = [fq.question for fq in formQs]
        context['form_questions'] = form_questions
        context['form'] = SelectRespondentForm
        return context

def submitResponse(request, form_id):
    form = get_object_or_404(Form, pk=form_id)
    user = request.POST['']

    response = Response(form=form, user=user)

    question = get_object_or_404(Question, pk=form_id)
    try:
        selected_option = question.option_set.get(pk=request.POST['option'])
    except(KeyError, Option.DoesNotExist):
        return render(request, 'forms/detail.html',
                    {'question':question, 'error_message':'You did not select a response.'},)
    else:
        response = Response(option=selected_option, response_date=timezone.now())
        response.save()
        return HttpResponseRedirect(reverse("forms:responses", args=(question.id,)))







class ViewRespondents(generic.ListView):
    template_name = 'forms/respondents.html'
    context_object_name = 'respondents'
    def get_queryset(self):
        return Respondent.objects.all()

class CreateRespondent(generic.CreateView):
    model = Respondent
    template_name = 'forms/respondent.html'
    fields = [
            'id_no', 'fname', 'lname', 'dob', 'sex', 'citizenship', 'ward', 'village', 
            'district', 'email', 'contact_no'
            ]
    success_url = reverse_lazy('forms:respondents')

class UpdateRespondent(generic.UpdateView):
    model=Respondent
    template_name = 'forms/respondent.html'
    fields = [
            'id_no', 'fname', 'lname', 'dob', 'sex', 'citizenship', 'ward', 'village', 
            'district', 'email', 'contact_no'
            ]
    success_url = reverse_lazy('forms:respondents')
   
class DeleteRespondent(generic.DeleteView):
    model=Respondent
    success_url = reverse_lazy('forms:respondents')

    #logic for instance where respondent has responses would go here



#None of this here works







class ResponsesView(generic.DetailView):
    model=Question
    template_name = 'forms/responses.html'


def responses(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "forms/responses.html", {"question": question})
