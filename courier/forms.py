from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import UserProfile, DeliveryBoy


class UserProfileForm(forms.ModelForm):
    """Form for creating/editing users with profiles"""

    # Basic user fields
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        help_text="Leave blank to keep current password"
    )
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    # Profile fields
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        initial='customer',
        required=True
    )
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Editing existing user
            self.fields['password'].required = False
            self.fields['password'].help_text = "Leave blank to keep current password"
            if hasattr(self.instance, 'profile'):
                self.fields['role'].initial = self.instance.profile.role
                self.fields['phone'].initial = self.instance.profile.phone
                self.fields['address'].initial = self.instance.profile.address

    def save(self, commit=True):
        user = super().save(commit=False)

        # Set password if provided
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        elif not user.pk:
            # New user without password - set unusable password
            user.set_unusable_password()

        if commit:
            user.save()
            # Create or update profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': self.cleaned_data['role'],
                    'phone': self.cleaned_data.get('phone', ''),
                    'address': self.cleaned_data.get('address', ''),
                }
            )
            if not created:
                profile.role = self.cleaned_data['role']
                profile.phone = self.cleaned_data.get('phone', '')
                profile.address = self.cleaned_data.get('address', '')
                profile.save()

        return user


class DeliveryBoyForm(forms.ModelForm):
    """Form for creating delivery boys"""

    # User fields
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    # Delivery boy fields
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea(), required=True)
    vehicle_type = forms.ChoiceField(
        choices=DeliveryBoy._meta.get_field('vehicle_type').choices,
        required=True
    )
    vehicle_number = forms.CharField(max_length=20, required=True)
    license_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = DeliveryBoy
        fields = ['vehicle_type', 'vehicle_number', 'license_number']

    def save(self, commit=True):
        # Create user first
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )

        # Create user profile
        UserProfile.objects.create(
            user=user,
            role='delivery_boy',
            phone=self.cleaned_data['phone'],
            address=self.cleaned_data['address']
        )

        # Create delivery boy profile
        delivery_boy = super().save(commit=False)
        delivery_boy.user = user
        if commit:
            delivery_boy.save()

        return delivery_boy


class UserEditForm(forms.ModelForm):
    """Form for editing user profiles"""

    # Profile fields
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['role'].initial = self.instance.profile.role
            self.fields['phone'].initial = self.instance.profile.phone
            self.fields['address'].initial = self.instance.profile.address

    def save(self, commit=True):
        user = super().save(commit=True)
        if hasattr(user, 'profile'):
            user.profile.role = self.cleaned_data['role']
            user.profile.phone = self.cleaned_data.get('phone', '')
            user.profile.address = self.cleaned_data.get('address', '')
            user.profile.save()
        return user


class DeliveryBoyEditForm(forms.ModelForm):
    """Form for editing delivery boy profiles"""

    # User fields
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    # Profile fields
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea(), required=True)

    class Meta:
        model = DeliveryBoy
        fields = [
            'vehicle_type', 'vehicle_number', 'license_number',
            'current_location', 'is_available'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            if hasattr(self.instance.user, 'profile'):
                self.fields['phone'].initial = self.instance.user.profile.phone
                self.fields['address'].initial = self.instance.user.profile.address

    def save(self, commit=True):
        delivery_boy = super().save(commit=True)

        # Update user fields
        delivery_boy.user.first_name = self.cleaned_data['first_name']
        delivery_boy.user.last_name = self.cleaned_data['last_name']
        delivery_boy.user.email = self.cleaned_data['email']
        delivery_boy.user.save()

        # Update profile fields
        if hasattr(delivery_boy.user, 'profile'):
            delivery_boy.user.profile.phone = self.cleaned_data['phone']
            delivery_boy.user.profile.address = self.cleaned_data['address']
            delivery_boy.user.profile.save()

        return delivery_boy
