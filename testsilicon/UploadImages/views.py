from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from .models import User, User_Image, Image_Comment, Notification
from .forms import UserForm, UploadFileForm
from django.template import RequestContext
from django.conf import settings
import hashlib

# Allow ext file jpg, jpeg, png, ico
EXT_FILES = {'image/jpg', 'image/jpeg', 'image/png', 'image/x-ico'}

# Pagination function
def paginator(objects, page=1, num_objects=2):
    paginator = Paginator(objects,num_objects)
    try:
      objects = paginator.page(page)
    except PageNotAnInteger:
      objects = paginator.page(1)
    except EmptyPage:
      objects = []
    return objects, paginator.count

# Check user of object image with user login
def different_user(current_id, request_id):
	if current_id == request_id:
		return False
	else:
		return True

# Show all photo upload of all user
def index (request):	
	username = request.session.get('username')	
	user_id = request.session.get('user_id')
	# Is login
	if(username):
		# get param page
		page = request.GET.get('page', 1)
		# Get all feed of all user
		images = User_Image.objects.filter().order_by('-created_at')
		images,count= paginator(images, page) # Paging data

		# Count notification of user
		notif = Notification.objects.filter(user=user_id, is_view=0).order_by('-created_at').count()

		# Bind request context
		request_context = RequestContext(request)
		request_context.push({'username': username})
		request_context.push({'user_id': user_id})
		request_context.push({'images': images})
		request_context.push({'notification': notif})
		return render(request, 'index.html', request_context)
	else:		
		return redirect('login')

# Profile user
def profile (request):
	username = request.session.get('username')	
	user_id = request.session.get('user_id')
	if(username):
		# get param page
		page = request.GET.get('page', 1)
		# Get all photo upload of user login
		images = User_Image.objects.filter(user=user_id).order_by('-created_at')
		images,count= paginator(images, page) # Paging data

		request_context = RequestContext(request)
		request_context.push({'username': username})
		request_context.push({'user_id': user_id})
		request_context.push({'images': images})
		return render(request, 'profile.html', request_context)
	else:		
		return redirect('login')

# Login 
def login(request):
	if(request.method == 'POST'):
		username = request.POST.get('user_name')
		password = request.POST.get('password')
		try:
			# Secure password
			m = hashlib.md5()
			m.update(password)
			password = m.hexdigest()

			# Get user by info POST request
			# If has record then redirect to index with session save
			result = User.objects.get(user_name=username, password=password)			
			request.session['username'] = result.user_name
			request.session['user_id'] = result.id					
			url = reverse('index', args=())
			return redirect('index')
		except User.DoesNotExist:
			# Fail login
			form = UserForm()
			request_context = RequestContext(request)
			request_context.push({'form': form})
			request_context.push({'errorMessage': 'Login Failed.'})
			return render(request, 'login.html', request_context)
	else:
		form = UserForm()
		return render(request, 'login.html', {'form': form})

# Regist new user
def regist(request):
	username = request.session.get('username')
	# If has username session => is login
	if username:
		return redirect('index')
	else:
		if(request.method == 'POST'):
			username = request.POST.get('user_name')
			password = request.POST.get('password')
			if(username and password):
				# Check exsts username
				exists = User.objects.filter(user_name=username)
				if len(exists) > 0:
					form = UserForm()
					request_context = RequestContext(request)
					request_context.push({'form': form})
					request_context.push({'errorMessage': 'Username already exists.'})
					return render(request, 'regist.html', request_context)
				else: # username not already exists
					# Secure password
					m = hashlib.md5()
					m.update(password)
					password = m.hexdigest()

					# Add new user
					user = User(user_name=username, password=password)
					user.save()
					request.session['username'] = user.user_name
					request.session['user_id'] = user.id
					return redirect('index')
			else:
				# Missing param

				form = UserForm()
				request_context = RequestContext(request)
				request_context.push({'form': form})
				request_context.push({'errorMessage': 'Register Failed.'})
				return render(request, 'regist.html', request_context)
		else:
			form = UserForm()
			return render(request, 'regist.html', {'form': form})

# Upload image
def upload(request):	
	if(request.method == 'POST'):
		try:
			# File info
			file_name = request.FILES['files']
			ext = file_name.content_type # Extension file
			# If in whitelist
			if(ext in EXT_FILES):			
				file_form = UploadFileForm(request.POST, request.FILES)			
				if file_form.is_valid():
					# Save file to disk
					image = file_form.save(commit=False)				
					# image = User_Image()
					image.user_id = request.session.get('user_id')
					image.image_path = "UploadImages/" + file_name.name

					# Save info file to db
					image.save()
				else:				
					request_context = RequestContext(request)				
					request_context.push({'errorMessage': 'Upload Invalid.'})
					return render(request, 'index.html', request_context) 
			else:
				print "failed"
		except Exception,e:			
			request_context = RequestContext(request)				
			request_context.push({'errorMessage': 'Upload Invalid.'})
			return render(request, 'index.html', request_context) 
	return redirect('index')

# Logout 
def logout(request):
	# Cleart session login
	del request.session['username']
	del request.session['user_id']
	request.session.modified = True	
	form = UserForm()
	return redirect('login')

# Comment on image
def comment(request, img_id):	
	if(request.method == 'POST'):
		comment = request.POST.get('comment')
		user_id = request.session.get('user_id')
		# Get object user comment
		user = User.objects.get(id=user_id)
		# get objects User_Image bind to foreign key Image_Comment
		img = User_Image.objects.get(id=img_id)
		img_comment = Image_Comment(image=img, comment=comment, user=user)
		img_comment.save()
		# If different user then save notification
		if different_user(user_id, img.user.id):			
			user_image = User.objects.get(id=img.user.id)
			notif = Notification()
			notif.user = user_image
			notif.user_commend = img_comment
			notif.image = img
			notif.is_view = 0
			notif.save()
		# Get all comment after save new comment
		img = User_Image.objects.get(id=img_id)
		return render(request, 'comment.html', {'img': img})
	else:

		# Load info image and all comment related
		img = User_Image.objects.get(id=img_id)
		if(img):
			return render(request, 'comment.html', {'img': img})
		else:
			return redirect('index')

# Search image by hashtag
def search(request):
	keyword = request.GET.get('keyword', '').replace('#', '')
	request_context = RequestContext(request)
	if keyword :
		# get param page
		page = request.GET.get('page', 1)		
		result = User_Image.objects.filter(commentImage__comment__contains="#"+keyword).distinct('id', 'created_at')\
			.order_by('-created_at')
		notif,count= paginator(result, page)
		count = len(result)
		request_context.push({'result': result})
		request_context.push({'count': count})
		request_context.push({'keyword': keyword})
		return render(request, 'search.html', request_context)
	else:
		request_context.push({'errorMessage': "No result found."})
		request_context.push({'keyword': keyword})
		return render(request, 'search.html', request_context)

# Load list notification of user
def notification(request):
	user_id = request.session.get('user_id')
	if user_id:
		# get param page
		page = request.GET.get('page', 1)
		notif = Notification.objects.filter(user=user_id).order_by('-created_at')
		notif,count= paginator(notif, page)

		request_context = RequestContext(request)
		request_context.push({'notification': notif})
		request_context.push({'count': len(notif)})

		# Update notification to read on page		
		Notification.objects.filter(id__in=notif.object_list.values('id')).filter(is_view=0).update(is_view=1)
		
		return render(request, 'notification.html', request_context)
	else:
		redirect('login')