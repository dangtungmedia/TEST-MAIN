from django import forms
class VideoForm(forms.Form):
    thumbnail = forms.FileField(widget=forms.FileInput(attrs={
                                                "class": "form-control",
                                                'accept': 'image/*',
                                                'id': 'input-Thumnail'
                                            }),required=False)
    

    title = forms.CharField(widget=forms.TextInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Nhập tiêu đề',
                                    'id': 'input-title'
                                }))
    
    
    description = forms.CharField(
                                widget=forms.Textarea(
                                    attrs={
                                        'class': 'form-control',
                                        'id': 'input-description',
                                        'rows':'5'}
                                        ))
    
    keyword = forms.CharField(
                                widget=forms.TextInput(
                                        attrs={'class': 'form-control',
                                                'id': 'input-keyword'
                                                }
                                        ))
    
    date_upload = forms.DateField(
                                widget=forms.DateInput(
                                        attrs={'class': 'form-control', 
                                               'id': 'input-date-upload',
                                               'type': 'date'}
                                        ))
    time_upload = forms.TimeField(
                                    widget=forms.TimeInput(
                                        attrs={
                                            'class': 'form-control', 
                                            'type': 'time',
                                            'id': 'input-time-upload',
                                            'placeholder': 'HH/MM',
                                        }
                                    )
                                )
    
    content = forms.CharField(widget=forms.Textarea(attrs={
                                                'id': 'input-text-content',
                                                "class": "form-control",
                                                'rows':"10",
                                            }),required=False)
    
   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    