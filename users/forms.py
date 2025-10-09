#form handling for users registration
from django import forms
from users.models import CustomUser


class StudentRegistrationForm(forms.ModelForm): #for registration
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput) #gets one password
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput) #confirming that password
    department=forms.ChoiceField(choices=CustomUser.DEPARTMENT_CHOICES,initial=None,required=True) #gets department name

    class Meta:
        model = CustomUser
        fields = ('email', 'year_of_study','department') #store the details as meta data

    def clean_password2(self): #validation for password matching
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match")
        return p2

    def save(self, commit=True): #saves entire detail in db
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = 'student'
        user.pending_approval = True
        user.is_approved = False
        user.department = self.cleaned_data['department']
        if commit:
            user.save()
        return user