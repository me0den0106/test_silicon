from django import forms
from .models import User_Image	

class UserForm(forms.Form):
	user_name = forms.CharField(label='Username', max_length=100)
	password = forms.CharField(label='Password', max_length=16, widget=forms.PasswordInput())

class UploadFileForm(forms.ModelForm):
	class Meta:
		model = User_Image
		fields = ('files', 'user')

	def __init__(self, *args, **kwargs):
		super(UploadFileForm, self).__init__(*args, **kwargs)
		self.fields['user'].widget = forms.TextInput(attrs={'name': 'user_id'})

	def save(self, commit=True):
		uploadSubmit = super(UploadFileForm, self).save(commit=False)		
		if(commit):
			uploadSubmit.save()
		return uploadSubmit