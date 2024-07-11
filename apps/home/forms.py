
from django import forms
from .models import Folder, ProfileChannel,Voice_language,Font_Text,syle_voice
import requests
import json

class ProfileChannelForm(forms.Form):   
    input_folder_name = forms.CharField(widget=forms.TextInput(attrs={
                                                'id' : "input_folder_name",
                                                "class": "form-control",
                                                'placeholder': 'Nhập tên folder',
                                            }),required=False)
    
    input_channel_name = forms.CharField(widget=forms.TextInput(attrs={
                                                'id' : "input_channel_name",
                                                "class": "form-control",
                                                'placeholder': 'Nhập tên Profile Channel'
                                            }),required=False) 
    
    folder_name = forms.ModelChoiceField(queryset=Folder.objects.none(),
                                        widget=forms.Select(attrs={
                                                    'id' : "folder_name",
                                                    "class": "form-select",
                                                }),required=False)
    
    folder_name_seting = forms.ModelChoiceField(queryset=Folder.objects.none(),
                                        widget=forms.Select(attrs={
                                                    'id' : "folder_name_seting",
                                                    "class": "form-select",
                                                }),required=False) 
    
    channel_name = forms.ModelChoiceField(queryset=ProfileChannel.objects.none(),
                                          widget=forms.Select(attrs={
                                              'id': "channel_name",
                                              "class": "form-select"
                                          }), required=False)
    
    forder_setting = forms.ModelChoiceField(queryset=Folder.objects.none(),
                                        widget=forms.Select(attrs={
                                                    'id' : "forder_setting",
                                                    "class": "form-select",
                                                }),required=False) 
    
    channel_forder_name_setting = forms.ModelChoiceField(queryset=Folder.objects.none(),
                                          widget=forms.Select(attrs={
                                              'id': "channel_forder_name_setting",
                                              "class": "form-select"
                                          }), required=False)
    
    channel_name_setting = forms.ModelChoiceField(queryset=ProfileChannel.objects.none(),
                                          widget=forms.Select(attrs={
                                              'id': "channel_name_setting",
                                              "class": "form-select"
                                          }), required=False)
    

    channel_intro_active = forms.BooleanField(widget=forms.CheckboxInput(attrs={
                                                'id' : "channel_intro_active",
                                                'class': 'form-check-input mt-0',
                                            }),required=False)
    
    
    channel_intro_url = forms.URLField(widget=forms.URLInput(attrs={
                                                'id' : "channel_intro_url",
                                                "class": "form-control",
                                                'readonly': 'readonly'
                                            }),required=False)
    
    
    channel_intro_input_file = forms.FileField(widget=forms.FileInput(attrs={
                                                'id' : "channel_intro_input_file",
                                                "class": "form-control",
                                                'aria-describedby': 'inputGroupFileAddon03',
                                                'aria-label': 'Upload',
                                                'accept': 'video/mp4',
                                            }),required=False)
    
    channel_outro_active = forms.BooleanField(widget=forms.CheckboxInput(attrs={
                                                'id' : "channel_outro_active",
                                                'class': 'form-check-input mt-0',
                                            }),required=False)
    
    channel_outro_url = forms.URLField(widget=forms.URLInput(attrs={
                                                'id' : "channel_outro_url",
                                                "class": "form-control",
                                                'readonly': 'readonly'
                                            }),required=False)
    
    channel_outro_input_file = forms.FileField(widget=forms.FileInput(attrs={
                                                'id' : "channel_outro_input_file",
                                                "class": "form-control",
                                                'aria-describedby': 'inputGroupFileAddon03',
                                                'aria-label': 'Upload',
                                                'accept': 'video/mp4',
                                            }),required=False)
    

    channel_logo_active = forms.BooleanField(widget=forms.CheckboxInput(attrs={
                                                'id' : "channel_logo_active",
                                                'class': 'form-check-input mt-0', 
                                            }),required=False)
    
    channel_logo_url = forms.URLField(widget=forms.URLInput(attrs={
                                                'id' : "channel_logo_url",
                                                "class": "form-control",
                                                'readonly': 'readonly'
                                            }),required=False) 

    channel_logo_position = forms.ChoiceField(choices=[('left', 'Bên Trái'), ('right', 'Bên Phải')],
                                           widget=forms.RadioSelect(attrs={'class': 'form-check-input'}))


    channel_logo_input_file = forms.FileField(widget=forms.FileInput(attrs={
                                                'id' : "channel_logo_input_file",
                                                "class": "form-control",
                                                'aria-describedby': 'inputGroupFileAddon03',
                                                'aria-label': 'Upload',
                                                'accept': 'image/*', 
                                            }),required=False)  
    
    channel_font_text = forms.ModelChoiceField(queryset=Font_Text.objects.all(),
                                          widget=forms.Select(attrs={
                                              'id': "channel_font_text",
                                              "class": "form-select",
                                          }), required=False)
    

    channel_font_text_setting = forms.ModelChoiceField(queryset=Font_Text.objects.all(),
                                          widget=forms.Select(attrs={
                                              'id': "channel_font_text_setting",
                                              "class": "form-select",
                                          }), required=False)
    

    channel_voice  = forms.ModelChoiceField(queryset=Voice_language.objects.all(),
                                                        widget=forms.Select(attrs={
                                                            'id': 'channel_voice',
                                                            'class': 'form-control',
                                                        }),
                                                        required=False
                                                    )
    
    channel_title = forms.CharField(widget=forms.TextInput(attrs={
                                                'id' : "channel_title",
                                                "class": "form-control",
                                                'placeholder': 'Nhập title'
                                            }),required=False)

    channel_description = forms.CharField(widget=forms.Textarea(attrs={
                                                'id' : "channel_description",
                                                "class": "form-control",
                                                'placeholder': 'Nhập description',
                                                'rows':"3",
                                            }),required=False)
    channel_keywords = forms.CharField(widget=forms.TextInput(attrs={
                                                'id' : "channel_keywords",
                                                "class": "form-control",
                                                'placeholder': 'Nhập keywords'
                                            }),required=False)
    channel_time_upload = forms.CharField(widget=forms.TextInput(attrs={
                                                'id' : "channel_time_upload",
                                                "class": "form-control",
                                                'placeholder': 'Nhập time upload'
                                            }),required=False)
    channel_url = forms.CharField(widget=forms.TextInput(attrs={
                                                'id' : "channel_url",
                                                "class": "form-control",
                                                'placeholder': 'Nhập url'
                                            }),required=False)
    channel_email_login = forms.CharField(widget=forms.TextInput(attrs={
                                                'id' : "channel_email_login",
                                                "class": "form-control",
                                                'placeholder': 'Nhập email login'
                                            }),required=False)
    
    channel_vps_upload = forms.CharField(widget=forms.TextInput(attrs={
                                                'id' : "channel_vps_upload",
                                                "class": "form-control",
                                                'placeholder': 'Nhập vps upload'
                                            }),required=False)

    
    channel_font_size = forms.CharField(widget=forms.NumberInput(attrs={
                                                'id' : "channel_font_size",
                                                "class": "form-control",
                                                'min': '0',
                                                'max': '100',
                                                'value': '30'
                                            }),required=False)

    channel_font_bold = forms.BooleanField(widget=forms.CheckboxInput(attrs={
                                                'id' : "channel_font_bold",
                                                'class': 'form-check-input',
                                            }),required=False)
    
    channel_font_italic = forms.BooleanField(widget=forms.CheckboxInput(attrs={
                                                'id' : "channel_font_italic",
                                                'class': 'form-check-input',
                                            }),required=False)
    
    channel_font_underline = forms.BooleanField(widget=forms.CheckboxInput(attrs={
                                                'id' : "channel_font_underline",
                                                'class': 'form-check-input',
                                            }),required=False)
    
    channel_font_strikeout = forms.BooleanField(widget=forms.CheckboxInput(attrs={
                                                'id' : "channel_font_strikeout",
                                                'class': 'form-check-input',
                                            }),required=False)

    
    channel_font_color = forms.CharField(widget=forms.TextInput(attrs={
                                                'id' : "channel_font_color",
                                                'class': 'form-control form-control-color',
                                                'type': 'color',
                                                'value': '#563d7c'
                                            }),required=False)
    
    channel_font_color_opacity = forms.CharField(widget=forms.NumberInput(attrs={
                                                'id' : "channel_font_color_opacity",
                                                'class': 'form-control',
                                                'min': '0',
                                                'max': '100',
                                                'value': '100'
                                            }),required=False)
    
    
    
    channel_font_color_troke = forms.CharField(widget=forms.TextInput(attrs={
                                                'id' : "channel_font_color_troke",
                                                'class': 'form-control form-control-color',
                                                'type': 'color',
                                                'value': '#563d7c'
                                            }),required=False)  
    
    channel_font_color_troke_opacity = forms.CharField(widget=forms.NumberInput(attrs={
                                                'id' : "channel_font_color_troke_opacity",
                                                'class': 'form-control',
                                                'min': '0',
                                                'max': '100',
                                                'value': '100'
                                            }),required=False)
    
    
    channel_font_background = forms.CharField(widget=forms.TextInput(attrs={
                                                'id' : "channel_font_background",
                                                'class': 'form-control form-control-color',
                                                'type': 'color',
                                                'value': '#563d7c'
                                            }),required=False)
    
    channel_font_background_opacity = forms.CharField(widget=forms.NumberInput(attrs={
                                                'id' : "channel_font_background_opacity",
                                                'class': 'form-control',
                                                'min': '0',
                                                'max': '100',
                                                'value': '100'
                                            }),required=False)
    

    channel_stroke_text = forms.CharField(widget=forms.NumberInput(attrs={
                                                'id' : "channel_stroke_text",
                                                'class': 'form-control',
                                                'min': '0',
                                                'max': '100',
                                                'value': '1',
                                                'step': '0.1',
                                            }),required=False)
    

    
    channel_subtitle_text = forms.CharField(widget=forms.Textarea(attrs={
                                                'id' : "channel_subtitle_text",
                                                "class": "form-control",
                                                'placeholder': 'Nhập subtitle',
                                                'rows':"3",
                                            }),required=False)
    


    channel_voice_setting  = forms.ModelChoiceField(queryset=Voice_language.objects.all(),
                                                    widget=forms.Select(attrs={
                                                        'id': 'channel_voice_setting',
                                                        'class': 'form-control'
                                                    }),
                                                    required=False
                                                )


    channel_voice_style = forms.ChoiceField(choices=[],
                                                  widget=forms.Select(attrs={
                                                            'id': 'channel_voice_style',
                                                            'class': 'form-control'}),
                                                            required=False)
    

    
    channel_voice_speed = forms.CharField(widget=forms.NumberInput(attrs={     
                                                'id' : "channel_voice_speed",
                                                "class": "form-range",
                                                'type':"range",
                                                'min': '0',
                                                'max': '100',
                                                'value': '50'
                                            }),required=False)
    


    channel_voice_pitch = forms.CharField(widget=forms.NumberInput(attrs={
                                                'id' : "channel_voice_pitch",
                                                "class": "form-range",
                                                'type':"range",
                                                'min': '0',
                                                'max': '100',
                                                'value': '50'
                                            }),required=False)
    
    channel_voice_volume = forms.CharField(widget=forms.NumberInput(attrs={
                                                'id' : "channel_voice_volume",
                                                "class": "form-range",
                                                'type':"range",
                                                'min': '0',
                                                'max': '100',
                                                'value': '50'
                                            }),required=False)
    
    channel_text_voice = forms.CharField(widget=forms.Textarea(attrs={
                                                'id' : "channel_text_voice",
                                                "class": "form-control",
                                                'placeholder': 'Nhập text voice',
                                                'rows':"3",
                                            }),required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    