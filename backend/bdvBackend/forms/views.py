from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.template import loader
from django.urls import reverse, reverse_lazy
from django.utils import timezone
import datetime
from django.views import generic

from .forms import RespondentForm, SelectRespondentForm, ResponseForm

import datetime
from django.db.models import F, Count


from.models import Respondent, Form, FormQuestion, Question, Option, Response, Answer
now = timezone.now()

class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'forms/index.html'
    context_object_name = 'active_forms'
    
    def get_queryset(self):
        num_visits = self.request.session.get('num_visits',0)
        num_visits += 1
        self.request.session['num_visits'] = num_visits
        last_login = self.request.session.get('last_login', 0)
        last_login = now.isoformat()
        self.request.session['last_login'] = last_login

        return Form.objects.filter(start_date__lte= datetime.date.today(), end_date__gte = datetime.date.today()).order_by('organization')

class FormView(LoginRequiredMixin, generic.DetailView):
    model=Form
    template_name = 'forms/form-detail.html'
    context_object_name = 'form_questions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_instance = self.get_object()
        formQs = FormQuestion.objects.filter(form=form_instance).order_by('index')
        form_questions = [fq.question for fq in formQs]
        context['form_meta'] = form_instance
        context['form'] = ResponseForm(formQs=form_questions, formLogic=formQs)
        context['msg'] = ''
        return context

def new_response(request, pk):
    form_meta = get_object_or_404(Form, pk=pk)
    formQs = FormQuestion.objects.filter(form=form_meta).order_by('index')
    formLogic = formQs
    formQs = [fq.question for fq in formQs]
    if request.method == 'POST':
        form = ResponseForm(request.POST, formQs=formQs, formLogic=formLogic)
        test = request.POST.getlist('What will you do in response to this?')
        print(test)
        if form.is_valid():
            respondent_id = request.POST.get('Respondent')
            response = Response(form=form_meta, respondent=get_object_or_404(Respondent, pk=respondent_id))
            response.save()
            for i in range(len(formQs)):
                if formQs[i].question_type == 'Text' or formQs[i].question_type == 'Number':
                    openResponse = request.POST.get(formQs[i].question_text)
                    answer = Answer(response=response, question=formQs[i], open_answer=openResponse, option=None)
                    answer.save()
                if formQs[i].question_type == 'Yes/No':
                    yesNo = request.POST.get(formQs[i].question_text)
                    answer = Answer(response=response, question=formQs[i], open_answer=yesNo)
                    answer.save()
                if formQs[i].question_type == 'Single Selection':
                    option_id = request.POST.get(formQs[i].question_text)
                    answer = Answer(response=response, question=formQs[i], option=get_object_or_404(Option, pk=option_id), open_answer=None)
                    answer.save()
                if formQs[i].question_type == 'Multiple Selections':
                    selected_options = request.POST.getlist(formQs[i].question_text)
                    for o in range(len(selected_options)):
                        answer = Answer(response=response, question=formQs[i],  option=get_object_or_404(Option, pk=selected_options[o]), open_answer=None)
                        answer.save()
            return HttpResponseRedirect(reverse("forms:index"))
        else:
            return render(request, 'forms/form-detail.html', 
                          { 'form': ResponseForm(request.POST, formQs=formQs), 
                           'form_meta':form_meta, 
                           'msg':'Double check that all the fields are correctly filled out.' })


class ViewRespondents(LoginRequiredMixin, generic.ListView):
    template_name = 'forms/respondents.html'
    context_object_name = 'respondents'
    def get_queryset(self):
        return Respondent.objects.all()

class ViewRespondent(LoginRequiredMixin, generic.DetailView):
    model=Respondent
    template_name = 'forms/view-respondent.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        respondent = self.get_object()
        responses = Response.objects.filter(respondent=respondent).order_by('response_date')
        context['respondent'] = respondent
        context['responses'] = responses
        return context


class CreateRespondent(LoginRequiredMixin, generic.CreateView):
    model = Respondent
    template_name = 'forms/edit-respondent.html'
    fields = [
            'id_no', 'fname', 'lname', 'dob', 'sex', 'citizenship', 'ward', 'village', 
            'district', 'email', 'contact_no'
            ]
    success_url = reverse_lazy('forms:respondents')


class UpdateRespondent(LoginRequiredMixin, generic.UpdateView):
    model=Respondent
    template_name = 'forms/edit-respondent.html'
    fields = [
            'id_no', 'fname', 'lname', 'dob', 'sex', 'citizenship', 'ward', 'village', 
            'district', 'email', 'contact_no'
            ]
    success_url = reverse_lazy('forms:respondents')
   

class DeleteRespondent(LoginRequiredMixin, generic.DeleteView):
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
