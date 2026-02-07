from django.http import HttpResponse,HttpResponseForbidden
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .models import Profile,Quiz,Question,Result
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='login')
def dashboard(request):
    profile = Profile.objects.get(user=request.user)
    return render(request,'quiz/dashboard.html',{'profile':profile})


@login_required(login_url='login')
def create_quiz(request):
    profile = Profile.objects.get(user=request.user)
    if not profile.is_teacher:
        return HttpResponseForbidden("You are not allowed here.")
    
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        time_limit = request.POST['time_limit']

        quiz = Quiz.objects.create(
            title = title,
            description = description,
            time_limit = time_limit,
            created_by = request.user,
        )
        return redirect('add_question',quiz_id = quiz.id)
    

    return render(request,'quiz/create_quiz.html')


@login_required(login_url='login')
def add_question(request,quiz_id):
    profile = Profile.objects.get(user=request.user)
    if not profile.is_teacher:
        return HttpResponseForbidden("Your not allowed here.")
    
    quiz = Quiz(id=quiz_id)

    if request.method == 'POST':
        text = request.POST['text']
        o1 = request.POST['option1']
        o2 = request.POST['option2']
        o3 = request.POST['option3']
        o4 = request.POST['option4']
        correct = request.POST['correct_option']

        Question.objects.create(
            quiz=quiz,
            text=text,
            option1=o1,
            option2=o2,
            option3=o3,
            option4=o4,
            correct_option=correct
        )
        return redirect('add_question', quiz_id=quiz.id)

    questions = quiz.questions.all()
    context = {
        'quiz': quiz,
        'questions': questions
    }
    return render(request,'quiz/add_question.html',context)



@login_required(login_url='login')
def quiz_list(request):
    profile = Profile.objects.get(user=request.user)
    if profile.is_teacher:
        return HttpResponseForbidden("Teachers cannot take quizzes.")

    quizzes = Quiz.objects.all()
    attempted = Result.objects.filter(user=request.user).values_list('quiz_id', flat=True)

    context = {
        'quizzes': quizzes,
        'attempted':attempted
    }
    return render(request, 'quiz/quiz_list.html', context)


@login_required(login_url='login')
def take_quiz(request, quiz_id):
    profile = Profile.objects.get(user=request.user)
    if profile.is_teacher:
        return HttpResponseForbidden("Teachers cannot take quizzes.")

    quiz = Quiz.objects.get(id=quiz_id)
    
    if Result.objects.filter(user=request.user, quiz=quiz).exists():
        messages.warning(request, "You have already attempted this quiz.")
        return redirect('quiz_result', quiz_id=quiz.id)

    questions = quiz.questions.all()

    if request.method == 'POST':
        score = 0
        for q in questions:
            selected = request.POST.get(str(q.id))
            if selected and int(selected) == q.correct_option:
                score += 1

        Result.objects.create(
            user=request.user,
            quiz=quiz,
            score=score
        )
        return redirect('quiz_result', quiz_id=quiz.id)
    context = {
        'quiz': quiz,
        'questions': questions
    }
    return render(request, 'quiz/take_quiz.html', context)


@login_required(login_url='login')
def quiz_result(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    result = Result.objects.filter(user=request.user, quiz=quiz).last()
    context = {
        'quiz': quiz,
        'result': result
    }
    return render(request, 'quiz/quiz_result.html', context)


@login_required(login_url='login')
def my_results(request):
    profile = Profile.objects.get(user=request.user)
    if profile.is_teacher:
        return HttpResponseForbidden("Teachers cannot view this page.")

    results = Result.objects.filter(user=request.user).select_related('quiz').order_by('-taken_at')
    return render(request, 'quiz/my_results.html', {'results': results})


@login_required(login_url='login')
def teacher_results(request):
    profile = Profile.objects.get(user=request.user)
    if not profile.is_teacher:
        return HttpResponseForbidden("Only teachers can view this page.")

    results = Result.objects.filter(quiz__created_by=request.user).select_related('user', 'quiz').order_by('-taken_at')

    return render(request, 'quiz/teacher_results.html', {
        'results': results
    })


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        is_teacher = request.POST.get('is_teacher') == 'on'

        if User.objects.filter(username = username).exists():
            messages.error(request,'Username already exists..')
            return redirect('signup')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        Profile.objects.create(user=user,is_teacher=is_teacher)
        messages.success(request, "Account created! Please login.")
        return redirect('login')
    
    return render(request,'quiz/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')
    return render(request,'quiz/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')