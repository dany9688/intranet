from django import forms
from .models import Bombero

class PresentesForm(forms.ModelForm):
    presentes = forms.ModelMultipleChoiceField(
        queryset=Bombero.objects.all(),
        widget=forms.SelectMultiple,
    )

    class Meta:
        model = Bombero
        fields = []
        
    def __init__(self, *args, **kwargs):
        super(PresentesForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control duallistbox'
            visible.field.widget.attrs['style'] = ';'

class AusentesForm(forms.ModelForm):
    ausentes = forms.ModelMultipleChoiceField(
        queryset=Bombero.objects.all(),
        widget=forms.SelectMultiple,
    )

    class Meta:
        model = Bombero
        fields = []
        
    def __init__(self, *args, **kwargs):
        super(AusentesForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control duallistbox'
            visible.field.widget.attrs['style'] = 'height: 200px;'

class RefuerzosForm(forms.ModelForm):
    refuerzos = forms.ModelMultipleChoiceField(
        queryset=Bombero.objects.all(),
        widget=forms.SelectMultiple,
    )

    class Meta:
        model = Bombero
        fields = []
        
    def __init__(self, *args, **kwargs):
        super(RefuerzosForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control duallistbox'
            visible.field.widget.attrs['style'] = 'height: 200px;'