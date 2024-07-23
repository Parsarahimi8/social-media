from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from .forms import UserRegistrationForm,UserLoginForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from home.models import Post
from .models import Relation

class UserRegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'account/register.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name , {'form':form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(cd['username'], cd['email'], cd['password1'])
            messages.success(request, 'you registered succcessfully','success')
            return redirect('home:home')
        return render(request, self.template_name , {'form':form})
    
    
    
class UserLoginView(View):
    
    form_class = UserLoginForm
    template_name = 'account/login.html'
    
    def setup(self, request, *args, **kwargs) :
        self.next = request.GET.get('next')
        return super().setup(request, *args, **kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = self.form_class
        return render(request, self.template_name , {'form':form})
    
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'] ,password=cd['password'])
            if user is not None :
                login(request, user)
                messages.success(request, 'you logged in successfully', 'success')
                if self.next :
                    return redirect(self.next)
                return redirect('home:home')
            messages.error(request, 'username or password is wrong','warning')
        return render(request, self.template_name , {'form':form})    
            
            
            
class UserLogoutView(LoginRequiredMixin,View):
    #login_url = '/account/login'
    
    def get(self, request):
        logout(request)
        messages.success(request,'you logged out successfully','success')
        return redirect('home:home')
    
    
class UserProfileView(LoginRequiredMixin, View):
    
    def get(self, request, user_id):
        #user = User.objects.get(id=user_id)
        is_following = False
        user = get_object_or_404(User,pk=user_id)
        posts = Post.objects.filter(user = user)
        relation = Relation.objects.filter(from_user = request.user ,to_user = user)
        if relation.exists():
            is_following = True
            
        return render(request, 'account/profile.html', {'user':user, 'posts':posts, 'is_following':is_following})
    
    
class UserFollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(from_user = request.user , to_user = user)
        if relation.exists():
            messages.error(request, 'you are already follow this user', 'danger')
        else:
            Relation.objects.create(from_user = request.user , to_user = user)
            #or Relation(from_user = request.user , to_user = user).save()
            messages.success(request, 'uou followed this user', 'success')
        return redirect('account:user_profile', user.id)
            
    
    
class UserUnfollowView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        relation = Relation.objects.filter(from_user=request.user , to_user = user)
        if relation.exists():
            relation.delete()
            messages.success(request,'you unfollowed this user','success')
        else:
            messages.error(request,'you are not following this user')
        return redirect('account:user_profile', user.id)