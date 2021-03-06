from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category, Comment


class ProductForm(forms.ModelForm):

    # Replace image field
    image = forms.ImageField(label='Image',
                             required=False,
                             widget=CustomClearableFileInput)

    # Change rendering of form to user-friendly checkboxes
    # Credit:
    # https://medium.com/swlh/django-forms-for-many-to-many-fields-d977dec4b024
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta():
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_name = [(c.id, c.get_friendly_name()) for c in categories]
        sku = Product.objects.order_by('sku').last()

        placeholders = {
            'sku': f'Greater than {sku.sku}',
        }

        for field in self.fields:
            if field == 'sku':
                placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
        self.fields['description'].required = True
        self.fields['category'].choices = friendly_name


class CommentForm(forms.ModelForm):

    class Meta():
        labels = {
            'body': 'Add your review',
        }

        model = Comment
        fields = ('body', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'body': 'Add review. Your username will be added automatically.'
        }

        for field in self.fields:
            if field == 'body':
                placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
