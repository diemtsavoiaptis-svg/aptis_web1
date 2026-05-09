from django import forms
from .models import ListeningQuestion


class RegisterForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "H? v? t?n h?c vi?n"
        })
    )

    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "S? ?i?n tho?i"
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "auth-input",
            "placeholder": "Email"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "auth-input",
            "placeholder": "M?t kh?u"
        })
    )


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "auth-input",
            "placeholder": "Email"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "auth-input",
            "placeholder": "M?t kh?u"
        })
    )


class ListeningQuestionAdminForm(forms.ModelForm):
    upload_audio_mp3 = forms.FileField(
        required=False,
        label="T?i file MP3 l?n Supabase",
        help_text="Ch?n file .mp3 ?? l?u tr?n Supabase Storage. N?u kh?ng ch?n file m?i, audio c? s? ???c gi? nguy?n."
    )

    class Meta:
        model = ListeningQuestion
        fields = "__all__"

    def clean_upload_audio_mp3(self):
        file_obj = self.cleaned_data.get("upload_audio_mp3")

        if not file_obj:
            return file_obj

        name = str(file_obj.name).lower()

        if not name.endswith(".mp3"):
            raise forms.ValidationError("Ch? cho ph?p upload file MP3.")

        max_size = 80 * 1024 * 1024

        if file_obj.size > max_size:
            raise forms.ValidationError("File MP3 qu? l?n. Gi?i h?n hi?n t?i l? 80MB/file.")

        return file_obj
