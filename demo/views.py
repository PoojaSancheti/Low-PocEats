from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import Meal, UserProfile, HealthConditions, EmailVerificationCode, Feedback
from .forms import SignUpForm, UserProfileForm, FeedbackForm
from .utils import generate_otp, send_otp_email

def signup_view(request):
    print(f"DEBUG: Request method: {request.method}")
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        print(f"DEBUG: Received POST data - username: {username}, email: {email}")
        print(f"DEBUG: Password1: {password1}, Password2: {password2}")
        
        # Validate required fields
        if not username or not email or not password1 or not password2:
            print("DEBUG: Missing required fields")
            messages.error(request, "All fields are required!")
            return render(request, 'demo/signup.html')

        # Check if passwords match
        if password1 != password2:
            print("DEBUG: Passwords don't match")
            messages.error(request, "Passwords do not match!")
            return render(request, 'demo/signup.html')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            print("DEBUG: Username already exists")
            messages.error(request, "Username is already taken!")
            print("DEBUG: Error message set, rendering template")
            return render(request, 'demo/signup.html')

        # Check if the email is already in use
        if User.objects.filter(email=email).exists():
            print("DEBUG: Email already exists")
            messages.error(request, "Email is already registered!")
            return render(request, 'demo/signup.html')

        print("DEBUG: All validations passed, creating user...")
        
        # Create and save user
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()
            print(f"DEBUG: User created successfully - ID: {user.id}")

            # Generate and send OTP
            otp = generate_otp()
            EmailVerificationCode.objects.create(user=user, code=otp)
            print(f"DEBUG: OTP created: {otp}")
            
            try:
                send_otp_email(user, otp)
                print("DEBUG: Email sent successfully")
            except Exception as email_error:
                print(f"DEBUG: Email failed: {email_error}")
            
            request.session['user_id'] = user.id
            print(f"DEBUG: Session user_id set to: {user.id}")
            messages.success(request, "Account created! Please check your email for verification code.")
            print("DEBUG: About to redirect to verify_otp")
            return redirect('verify_otp')
            
        except Exception as e:
            print(f"DEBUG: User creation failed: {e}")
            messages.error(request, f"Account creation failed: {str(e)}")
            return render(request, 'demo/signup.html')
    
    print("DEBUG: Rendering signup.html")
    return render(request, 'demo/signup.html')

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        user_id = request.session.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            otp_obj = EmailVerificationCode.objects.get(user=user)
            
            if otp_obj.code == otp and not otp_obj.is_expired():
                user.is_active = True
                user.save()
                otp_obj.is_valid = False
                otp_obj.save()
                messages.success(request, "Your email has been verified. Please log in.")
                return redirect('login')
            else:
                messages.error(request, "Invalid or expired OTP.")
        except (User.DoesNotExist, EmailVerificationCode.DoesNotExist):
            messages.error(request, "Invalid verification session. Please try signing up again.")
            return redirect('signup')
        
    return render(request, 'demo/verify_otp.html')

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")  # Optional: welcome message
            return redirect('home')  # Redirect to the home page after successful login
        else:
            messages.error(request, "Invalid credentials!")
            return redirect('login')

    return render(request, 'demo/login.html')

# Home View
@login_required
def home_view(request):
    return render(request, 'demo/home.html', {'username': request.user.username})

# User profile view (form submission)
@login_required
def user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user_profile, created = UserProfile.objects.update_or_create(
                user=request.user,  # Associate the form data with the logged-in user
                defaults={
                    'name': form.cleaned_data['name'],
                    'age': form.cleaned_data['age'],
                    'height': form.cleaned_data['height'],
                    'weight': form.cleaned_data['weight'],
                    'diet_pref': form.cleaned_data['diet_pref'],
                    'food_allergies': form.cleaned_data['food_allergies'],
                }
            )
            # Use the set() method to update the many-to-many relationship
            user_profile.health_con.set(form.cleaned_data['health_con'])
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile_success')  # Redirect to the success page
        else:
            messages.error(request, "There was an error with your submission.")
    else:
        user_profile = UserProfile.objects.filter(user=request.user).first()
        if user_profile:
            form = UserProfileForm(instance=user_profile)
        else:
            form = UserProfileForm()
    return render(request, 'demo/userprofile.html', {'form': form})

# Profile success view
def profile_success(request):
    return render(request, 'demo/profilesuc.html')

@login_required
def recipe_list_view(request):
    meal_type = request.GET.get('meal_type')
    diet_suitability = request.GET.get('diet_suitability')
    health_condition = request.GET.get('health_condition')
    total_cost = request.GET.get('total_cost')

    try:
        total_cost = float(total_cost) if total_cost else None
    except (ValueError, TypeError):
        total_cost = None
    # Fetch all meals
    meals = Meal.objects.all()

    # Apply filters
    if meal_type:
        meals = meals.filter(meal_type=meal_type)
    if diet_suitability:
        meals = meals.filter(diet_suitability=diet_suitability)
    if health_condition:
        meals = meals.filter(health_condition_suitability__name=health_condition)
    if total_cost:
        meals = meals.filter(total_cost__lte=total_cost)

    health_conditions = HealthConditions.objects.all()

    return render(request, 'demo/recipe_list.html', {
        'meals': meals,
        'health_conditions': health_conditions,
        'meal_type': meal_type,
        'diet_suitability': diet_suitability,
        'health_condition': health_condition,
        'total_cost': total_cost
    })

@login_required
def recipe_detail_view(request, recipe_id):
    recipe = get_object_or_404(Meal, id=recipe_id)
    associated_health_conditions = recipe.health_condition_suitability.all()
    return render(request, 'demo/recipe_detail.html', {
        'recipe': recipe,
        'associated_health_conditions': associated_health_conditions
    })


from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

def feedback_page(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            rating = form.cleaned_data['rating']

            # Save feedback to the database
            feedback = Feedback(name=name, email=email, message=message, rating=rating)
            feedback.save()

            # Send email (adjust settings.py to enable email sending)
            try:
                send_mail(
                    subject=f"Contact Us Form Submission from {name}",
                    message=f"Name: {name}\nEmail: {email}\nRating: {rating}\n\nMessage:\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['lowpoceat@gmail.com'],  # Support email
                )
                return HttpResponse("Your message has been sent successfully. We'll get back to you shortly.")
            except Exception as e:
                return HttpResponse(f"Error: {e}")
    else:
        form = FeedbackForm()
    return render(request, 'demo/feedback.html', {'form': form})

def contact_us(request):
    """
    Handles the contact form submission.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Send email (adjust settings.py to enable email sending)
        try:
            send_mail(
                subject=f"Contact Us Form Submission from {name}",
                message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['lowpoceat@gmail.com'],  # Support email
            )
            return HttpResponse("Your message has been sent successfully. We'll get back to you shortly.")
        except Exception as e:
            return HttpResponse(f"Error: {e}")
    else:
        return HttpResponse("Invalid request.")
    
def logout_view(request):
    logout(request)
    return redirect('login')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate password reset code
            reset_code = generate_otp()
            
            # Delete existing reset codes for this user
            EmailVerificationCode.objects.filter(user=user).delete()
            
            # Create new reset code
            EmailVerificationCode.objects.create(user=user, code=reset_code)
            
            # Send reset email
            try:
                subject = 'Password Reset Code - LowPocEat'
                message = f'Your password reset code is: {reset_code}\n\nThis code will expire in 24 hours.'
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email]
                )
                
                request.session['reset_email'] = email
                messages.success(request, "Password reset code sent to your email.")
                return redirect('reset_password')
                
            except Exception as e:
                messages.error(request, f"Failed to send email: {str(e)}")
                
        except User.DoesNotExist:
            messages.error(request, "No account found with this email address.")
            
    return render(request, 'demo/forgot_password.html')

def reset_password_view(request):
    if request.method == 'POST':
        reset_code = request.POST.get('reset_code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        email = request.session.get('reset_email')
        
        if not email:
            messages.error(request, "Session expired. Please request a new reset code.")
            return redirect('forgot_password')
            
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'demo/reset_password.html')
            
        try:
            user = User.objects.get(email=email)
            verification_code = EmailVerificationCode.objects.get(user=user, code=reset_code)
            
            if verification_code.is_expired():
                messages.error(request, "Reset code has expired. Please request a new one.")
                return redirect('forgot_password')
                
            # Reset password
            user.set_password(new_password)
            user.save()
            
            # Delete the verification code
            verification_code.delete()
            
            # Clear session
            if 'reset_email' in request.session:
                del request.session['reset_email']
                
            messages.success(request, "Password reset successfully! You can now log in.")
            return redirect('login')
            
        except (User.DoesNotExist, EmailVerificationCode.DoesNotExist):
            messages.error(request, "Invalid reset code.")
            
    return render(request, 'demo/reset_password.html')
