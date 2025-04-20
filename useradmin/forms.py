from django import forms
from .models import UserRole, UserPermission, AdminUser, UserProfile
from core.models import Product, Category

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = UserRole
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class UserPermissionForm(forms.ModelForm):
    class Meta:
        model = UserPermission
        fields = ['name', 'codename', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class AdminUserForm(forms.ModelForm):
    class Meta:
        model = AdminUser
        fields = ['role', 'permissions', 'is_active']
        widgets = {
            'permissions': forms.CheckboxSelectMultiple(),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'phone', 'address', 'profile_image']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter bio'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Enter address'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

class AddProductForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter product title'
    }))
    description = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Enter product description',
        'rows': 4
    }))
    price = forms.DecimalField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter selling price'
    }))
    old_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter old price (optional)'
    }))
    type = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter product type'
    }))
    stock_count = forms.IntegerField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter stock quantity'
    }))
    life = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter product life'
    }))
    mfd = forms.DateField(widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
    }))
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter tags (comma separated, e.g. organic, natural, skincare)'
    }))
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    image = forms.ImageField(widget=forms.FileInput(attrs={
        'class': 'form-control',
        'accept': 'image/*'
    }))
    
    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        # Just return the raw input - we'll process it in the view
        return tags.strip()

    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'old_price', 'type', 'stock_count', 'life', 'mfd', 'tags', 'category', 'image'] 