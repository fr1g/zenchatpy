from django.core.handlers.wsgi import WSGIRequest
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q
import json

from .models import Contact, UserProfile
from .serializers import ContactSerializer, UserProfileSerializer

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'register.html')
        
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Registration successful, please log in')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'register.html')
    
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have successfully logged out')
    return redirect('home')

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'userprofile') and user.userprofile.is_admin()

admin_required = user_passes_test(is_admin)

def home(request):
    return render(request, 'index.html')

@login_required
def contact_list(request):
    if is_admin(request.user):
        contacts = Contact.objects.all()
    else:
        contacts = Contact.objects.filter(user=request.user)
    
    paginator = Paginator(contacts, 10)
    page_number = request.GET.get('page')
    
    try:
        contacts_page = paginator.page(page_number)
    except PageNotAnInteger:
        contacts_page = paginator.page(1)

    except EmptyPage:
        contacts_page = paginator.page(paginator.num_pages)
    
    return render(request, 'contact_list.html', {
        'contacts': contacts_page,
        'paginator': paginator,
        'page_obj': contacts_page,
        'is_admin': is_admin(request.user)
    })

@login_required
def contact_detail(request, contact_id):
    if is_admin(request.user):
        contact = get_object_or_404(Contact, id=contact_id)
    else:
        contact = get_object_or_404(Contact, id=contact_id, user=request.user)
    return render(request, 'contact_detail.html', {'contact': contact})

@login_required
def contact_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        additional = request.POST.get('additional', '-')
        
        if name and phone and email:
            contact = Contact.objects.create(
                user=request.user,
                name=name,
                phone=phone,
                email=email,
                additional=additional
            )
            messages.success(request, f'Contact created successfully: {name}')
            return redirect('contact_detail', contact_id=contact.id)
        else:
            messages.error(request, 'Please fill in all required fields')
    
    return render(request, 'contact_create.html')

@login_required
def contact_edit(request, contact_id):
    if is_admin(request.user):
        contact = get_object_or_404(Contact, id=contact_id)
    else:
        contact = get_object_or_404(Contact, id=contact_id, user=request.user)
    
    if request.method == 'POST':
        contact.name = request.POST.get('name', contact.name)
        contact.phone = request.POST.get('phone', contact.phone)
        contact.email = request.POST.get('email', contact.email)
        contact.additional = request.POST.get('additional', contact.additional)
        
        if contact.name and contact.phone and contact.email:
            contact.save()
            messages.success(request, f'Contact updated successfully: {contact.name}')
            return redirect('contact_detail', contact_id=contact.id)
        else:
            messages.error(request, 'Please fill in all required fields')
    
    return render(request, 'contact_edit.html', {'contact': contact})

@login_required
def contact_delete(request, contact_id):
    if is_admin(request.user):
        contact = get_object_or_404(Contact, id=contact_id)
    else:
        contact = get_object_or_404(Contact, id=contact_id, user=request.user)
    
    if request.method == 'POST':
        contact_name = contact.name
        contact.delete()
        messages.success(request, f'Contact deleted successfully: {contact_name}')
        return redirect('contact_list')
    
    return render(request, 'contact_delete.html', {'contact': contact})

@login_required
def search_form(request):
    return render(request, 'search.html')

@login_required
def search_results(request):
    search_type = request.GET.get('search_type', 'name')
    keyword = request.GET.get('keyword', '')
    
    if not keyword:
        messages.warning(request, 'Please enter a search keyword')
        return redirect('search_form')
    
    if is_admin(request.user):
        base_queryset = Contact.objects.all()
    else:
        base_queryset = Contact.objects.filter(user=request.user)
    
    if search_type == 'name':
        contacts = base_queryset.filter(name__icontains=keyword)
    elif search_type == 'email':
        contacts = base_queryset.filter(email__icontains=keyword)
    elif search_type == 'both':
        contacts = base_queryset.filter(
            Q(name__icontains=keyword) | Q(email__icontains=keyword)
        )
    else:
        contacts = base_queryset.filter(name__icontains=keyword)
    
    return render(request, 'search_results.html', {
        'contacts': contacts,
        'search_type': search_type,
        'keyword': keyword
    })

@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def index(request):
    data = {'k': 'v'}
    return Response(data, template_name="index.html")

# @api_view(['POST'])
# @renderer_classes([JSONRenderer])

# @app.get("/list")
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def listAll(request):
    contacts = Contact.objects.all()
    if not contacts.exists():
        return Response({"message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = ContactSerializer(contacts, many=True)
    return Response({"result": serializer.data})

# @app.get("/list-page/{page}")
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def listPaged(request, page: int):
    contacts = Contact.objects.all()
    page_size = 10  
    paginator = Paginator(contacts, page_size)

    try:
        contacts_page = paginator.page(page)
    except PageNotAnInteger:
        contacts_page = paginator.page(1)
    except EmptyPage:
        contacts_page = paginator.page(paginator.num_pages)

    serializer = ContactSerializer(contacts_page, many=True)
    return Response({
        'count': paginator.count,
        'page_size': page_size,
        'current_page': contacts_page.number,
        'total_pages': paginator.num_pages,
        'next_page': contacts_page.next_page_number() if contacts_page.has_next() else None,
        'previous_page': contacts_page.previous_page_number() if contacts_page.has_previous() else None,
        'results': serializer.data
    })

# @app.get("/get/{byId}")
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def get(request, byId: int):
    try:
        contact = Contact.objects.get(id=byId)
    except Contact.DoesNotExist:
        return Response({"message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = ContactSerializer(contact)
    return Response(serializer.data)

# @app.post("/get-detail")
@api_view(['POST'])
@renderer_classes([JSONRenderer])
def getDetail(request: WSGIRequest):
    try:
        jsoned = json.loads(request.body.decode('utf-8'))
        required = int(jsoned["id"])
    except (json.JSONDecodeError, KeyError, ValueError):
        return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        contact = Contact.objects.get(id=required)
    except Contact.DoesNotExist:
        return Response({"id": required, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = ContactSerializer(contact)
    return Response(serializer.data)

# @app.put("/new")
@api_view(['PUT'])
@renderer_classes([JSONRenderer])
def create(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return Response({"message": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
    serializer = ContactSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "done"}, status=status.HTTP_201_CREATED)
    else:
        return Response({"message": "Validation error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# @app.patch("/update/{byId}")
@api_view(['PATCH'])
@renderer_classes([JSONRenderer])
def update(request: WSGIRequest, byId: int):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return Response({"message": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        contact = Contact.objects.get(id=byId)
    except Contact.DoesNotExist:
        return Response({"id": byId, "message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = ContactSerializer(contact, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"id": byId, "message": "Updated"})
    else:
        return Response({"message": "Validation error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# @app.delete("/delete/{byId}")
@api_view(['DELETE'])
@renderer_classes([JSONRenderer])
def delete(request, byId: int):
    try:
        contact = Contact.objects.get(id=byId)
        contact.delete()
        return Response({"message": "done"})
    except Contact.DoesNotExist:
        return Response({"message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

# @app.get("/search/{segment}")
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def search(request, segment: str):
    contacts = Contact.objects.filter(name__icontains=segment)
    if not contacts.exists():
        return Response({"message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = ContactSerializer(contacts, many=True)
    return Response({"results": serializer.data})

@login_required
@admin_required
def user_list(request):
    users = User.objects.all().select_related('userprofile')
    
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    
    try:
        users_page = paginator.page(page_number)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)
    
    return render(request, 'user_list.html', {
        'users': users_page,
        'paginator': paginator,
        'page_obj': users_page
    })

@login_required
@admin_required
def user_promote(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user_profile = user.userprofile
        user_profile.user_type = 'admin'
        user_profile.save()
        messages.success(request, f'User {user.username} has been promoted to administrator')
        return redirect('user_list')
    
    return render(request, 'user_promote.html', {'user': user})

@login_required
@admin_required
def user_demote(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.error(request, 'Cannot demote yourself')
        return redirect('user_list')
    
    if request.method == 'POST':
        user_profile = user.userprofile
        user_profile.user_type = 'regular'
        user_profile.save()
        messages.success(request, f'User {user.username} has been demoted to regular user')
        return redirect('user_list')
    
    return render(request, 'user_demote.html', {'user': user})
