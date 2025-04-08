from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect,JsonResponse
from django.urls import reverse
from .forms import UserRegisterForm, QuestionForm, AnswerForm
from .models import Question, Answer
from django.contrib.auth.models import User

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def home(request):
    user_filter = request.GET.get('user')
    if user_filter:
        questions = Question.objects.filter(author__username=user_filter)
    else:
        questions = Question.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'questions': questions})

@login_required
def ask_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            return redirect('home')
    else:
        form = QuestionForm()
    return render(request, 'question_form.html', {'form': form})

def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    answers = question.answers.all().order_by('-created_at')
    
    if request.method == 'POST':
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()
            return HttpResponseRedirect(reverse('question_detail', args=[pk]))
    else:
        answer_form = AnswerForm()
    
    return render(request, 'question_detail.html', {
        'question': question,
        'answers': answers,
        'answer_form': answer_form
    })

@login_required
def like_answer(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    
    if request.user in answer.likes.all():
        answer.likes.remove(request.user)
        liked = False
    else:
        answer.likes.add(request.user)
        liked = True
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'count': answer.likes.count(),
            'likers': [user.username for user in answer.likes.all()]
        })
    return redirect('question_detail', pk=answer.question.pk)

def user_questions(request, username):
    user = get_object_or_404(User, username=username)
    questions = Question.objects.filter(author=user)
    return render(request, 'quara/user_questions.html', {
        'profile_user': user,
        'questions': questions
    })
