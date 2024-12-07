
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from .models import SavingsGoal,RecurringSavingsGoal
from .forms import SavingsGoalForm
from django.contrib.auth import authenticate, login as auth_login
from .forms import RecurringSavingsForm
from .models import RecurringSavings
from celery import shared_task
from datetime import timedelta




@login_required 
def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')


def register(request):
    """Show the registration form"""
    
    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        #Check the password
        if password == confirm_password:
            try:
                user = User.objects.create_user(username =username, password=password)
                user.save()
                
                #Display a message
                messages.success(request,"Chambilecho wahenga.")
                return redirect('savings:login_page')
            except:
                #Display a message if the above fails
                messages.error(request,"Ina exist")
            else:
                #Display a message saying passwords don't match
                messages.error(request,"Hazimatch")
    return render(request, 'register.html')

#register 
def login_page(request):
     if request.method == 'POST':
        username = request.POST['username'] 
        password = request.POST['password'] 
        user = authenticate(request, username=username, password=password)
       
        if user is not None: 
            auth_login(request, user) 
            print("User logged in:", request.user) 
            messages.success(request, 'You are now logged in') 
            return redirect('dashboard')
    
        else: messages.error(request, 'Invalid credentials')
     context = { 
    'values': request.POST
        } 
     return render(request, 'login_page.html', context)
    


@login_required
def dashboard(request):
    user = request.user
    goals = SavingsGoal.objects.filter(user=user)
    recurring_savings = RecurringSavings.objects.filter(user=user)
    return render(request, 'dashboard.html', {'goals': goals, 'recurring_savings': recurring_savings})
    


# View to create a new savings goal
def create_goal(request):
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            # Set the user to the logged-in user
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            return redirect('savings:dashboard')  # Redirect to dashboard after saving
    else:
        form = SavingsGoalForm()
    return render(request, 'create_goal.html', {'form': form})

# View to edit an existing savings goal
def edit_goal(request, goal_id):
    goal = SavingsGoal.objects.get(id=goal_id, user=request.user)
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            return redirect('savings:dashboard')
    else:
        form = SavingsGoalForm(instance=goal)
    return render(request, 'edit_goal.html', {'form': form})


def set_recurring_savings(request):
    if request.method == 'POST':
        form = RecurringSavingsForm(request.POST)
        if form.is_valid():
            recurring_saving = form.save(commit=False)
            recurring_saving.user = request.user
            recurring_saving.next_saving_date = recurring_saving.start_date
            recurring_saving.save()
            return redirect('dashboard')
    else:
        form = RecurringSavingsForm()
    return render(request, 'set_recurring_savings.html', {'form': form})



@shared_task
def process_recurring_savings():
    today = datetime.date.today()
    schedules = RecurringSavings.objects.filter(next_saving_date=today)
    
    for schedule in schedules:
        goal = schedule.goal
        goal.current_amount += schedule.amount
        goal.save()
        
        # Update next_saving_date
        if schedule.frequency == 'daily':
            schedule.next_saving_date += timedelta(days=1)
        elif schedule.frequency == 'weekly':
            schedule.next_saving_date += timedelta(weeks=1)
        elif schedule.frequency == 'monthly':
            schedule.next_saving_date += timedelta(days=30)
        schedule.save()


def set_recurring_savings(request):
    if request.method == 'POST':
        # Get data from the form
        amount = request.POST.get('amount')
        frequency = request.POST.get('frequency')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Save the data to the database (example)
        goal = RecurringSavingsGoal(
            amount=amount,
            frequency=frequency,
            start_date=start_date,
            end_date=end_date,
            user=request.user  # assuming you have a user field
        )
        goal.save()

        return redirect('savings:dashboard')  # Redirect to dashboard or any other page
    else:
        form = RecurringSavingsForm()

    return render(request, 'set_recurring_savings.html', {'form': form})

  
def delete_goal(request, goal_id):
    if request.method == 'POST':  # Ensure it's a POST request
        try:
            goal = RecurringSavingsGoal.objects.get(id=goal_id, user=request.user)
        except RecurringSavingsGoal.DoesNotExist:
            messages.error(request, "Goal not found.")
            return redirect('savings:dashboard')
        
        goal.delete()
        messages.success(request, "The savings goal has been deleted successfully.")
        return redirect('savings:dashboard')
    else:
        return redirect('savings:dashboard')  # If not a POST request, redirect