from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy # redirects to another part of a page

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Task


class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')

class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None: # if user is successfully created 
            login(self.request, user) # comes from login we imported 
        return super(RegisterPage, self).form_valid(form)
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks') #the redirect_authenticated_user=True didn't block out authenticated users from going back to the register page, we did it manually
        return super(RegisterPage, self).get(*args, **kwargs)
    
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks' # Changes name to use in context. Ex: iterating over the objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) #context is a dictionary that helps us know the context in which the template is being rendered. super() gives us access to methods and properties of a parent or sibling class
        context['tasks'] = context['tasks'].filter(user=self.request.user) # filters tasks shown by user
        context['count'] = context['tasks'].filter(complete=False).count()
        
        search_input = self.request.GET.get('search-area') or '' # if we don't submit anything, field is empty 
        if search_input:
            context['tasks'] = context['tasks'].filter(title__icontains=search_input)
        
        context['search_input'] = search_input # makes the search bar query to not dissapear allowing for easier navigation
        #icontains checks to see if it contains that input, startswith checks if it STARTS with that input
        return context

class TaskDetail(LoginRequiredMixin, DetailView): # view that shows  details of an object
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete'] # handles what fields we want to show, in this case all
    success_url = reverse_lazy('tasks') # refers back to TaskList view when task is created

    def form_valid(self, form):
        form.instance.user = self.request.user # the specific instance is set to the actual user model instance
        return super(TaskCreate, self).form_valid(form) # this returns the instance of the TaskCreate object with the additional form_valid method which sets the user
    
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
