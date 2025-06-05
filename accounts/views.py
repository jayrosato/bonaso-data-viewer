from django.shortcuts import render, get_object_or_404
from django.views import generic, View
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, login, authenticate
from django.db.models import Q
import json

User = get_user_model()
from accounts.models import UserProfile, Message

class Settings(LoginRequiredMixin, View):
    def get(self, request):
        user = self.request.user
        userProfile = user.userprofile
        return render(request, 'accounts/settings.html', {'user':user, 'userProfile':userProfile})

class Profile(LoginRequiredMixin, generic.DetailView):
    model=User
    template_name='accounts/profile.html'
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        from forms.models import Response, Respondent, Form
        context = super().get_context_data(**kwargs)
        user_org = self.request.user.userprofile.organization
        context['user_org'] = user_org
        pk=self.kwargs['pk']
        employee = get_object_or_404(User, id=pk)
        responses = Response.objects.filter(created_by=employee.id).count()
        context['responses'] = responses
        respondents = Respondent.objects.filter(created_by=employee.id).count()
        context['respondents'] = respondents
        forms = Form.objects.filter(created_by=employee.id).count()
        context['forms'] = forms
        direct_team = UserProfile.objects.filter(supervisor=employee.id).count()
        underlings = UserProfile.objects.filter(manager=employee.id).count()
        context['direct_team'] = direct_team
        context['underlings'] = underlings

        try:
            employee_user_profile = employee.userprofile
        except UserProfile.DoesNotExist:
            employee_user_profile = None

        context['employee_user_profile'] = employee_user_profile
        return context
    
class ViewMessagesIndex(LoginRequiredMixin, generic.ListView):
    template_name = 'accounts/view-messages-index.html'
    context_object_name = 'messages'
    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(recipient=user, parent=None)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        sentMessages = Message.objects.filter(sender=user, parent=None)
        context['sent'] = sentMessages
        return context

class ViewMessageDetail(LoginRequiredMixin, generic.DetailView):
    model=Message
    template_name='accounts/view-message-detail.html'
    context_object_name = 'message'

    def get_object(self, queryset=None):
        msg = super().get_object(queryset)
        if msg.recipient == self.request.user and not msg.read:
            msg.read = True
            msg.save(update_fields=['read'])
        return msg
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        replies = Message.objects.filter(parent = pk).order_by('sent_on')
        for reply in replies:
            reply.read = True
            reply.save()
        context['replies'] = replies
        return context
    
class CreateMessage(LoginRequiredMixin, generic.CreateView):
    model=Message
    template_name = 'accounts/compose-message.html'
    fields =  ['recipient', 'subject', 'body']
            
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        user_org = user.userprofile.organization
        if user.userprofile.access_level != 'admin':
            form.fields['recipient'].queryset = User.objects.filter(Q(userprofile__organization=user_org) | Q(userprofile__access_level='admin'))
        else:
            form.fields['recipient'].queryset = User.objects.all()
        return form
    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('accounts:view-messages-index')
    
class CreateReply(LoginRequiredMixin, generic.CreateView):
    model=Message
    template_name = 'accounts/compose-message.html'
    fields =  ['body']

    def form_valid(self, form):
        pk = self.kwargs['pk']
        parent = Message.objects.filter(id=pk).first()
        if self.request.user == parent.sender:
            recipient = parent.recipient
        else:
            recipient = parent.sender
        form.instance.sender = self.request.user
        form.instance.recipient = recipient
        form.instance.parent = parent
        form.instance.subject = 'Replying to: ' + parent.subject
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('accounts:view-message-detail', kwargs={'pk': self.object.parent.id})


class UpdateMessage(LoginRequiredMixin, generic.UpdateView):
    model=Message
    template_name = 'accounts/compose-message.html'
    fields =  ['subject', 'body']

    def get_success_url(self):
        if(self.object.parent == None):
            return reverse_lazy('accounts:view-message-detail', kwargs={'pk': self.object.id})
        else:
            return reverse_lazy('accounts:view-message-detail', kwargs={'pk': self.object.parent.id})


class CompleteMessage(LoginRequiredMixin, View):
    def post(self, request, pk):
        message = Message.objects.filter(id=pk).first()
        message.completed = True
        message.save(update_fields=['completed'])

        return HttpResponseRedirect(reverse_lazy('accounts:view-message-detail', kwargs={'pk': message.id}))


class DeleteMessage(LoginRequiredMixin, generic.DeleteView):
    model=Message
    success_url = reverse_lazy('accounts:view-messages-index')



#for verifying mobile logins
from rest_framework.views import APIView
from rest_framework.response import Response as APIResponse
from rest_framework import status, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import MyTokenObtainPairSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
class MobileLoginRequest(APIView):
    def post(self, request):
        attempt = json.loads(request.body)
        print(attempt)
        username = attempt['data']['username']
        password = attempt['data']['password']
        user=authenticate(username=username, password=password)
        if user:
            login(request, user)
            response = {
                'status':'success',
                'session_id':'12345'
            }
        else:
            response = {
                'status':'Incorrect username or password.'
            }

        return APIResponse(response)
    
class CheckAPI(APIView):
    def get(self, request):
        return JsonResponse({'status':'ok'})