from django import forms

from .models import ListeningQuestion


class RegisterForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "Họ và tên học viên",
            "autocomplete": "name",
        })
    )

    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "Số điện thoại",
            "autocomplete": "tel",
        })
    )

    email = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "Tài khoản hoặc email",
            "autocomplete": "username",
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "auth-input",
            "placeholder": "Mật khẩu",
            "autocomplete": "new-password",
        })
    )


class LoginForm(forms.Form):
    email = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "auth-input",
            "placeholder": "Tài khoản hoặc email",
            "autocomplete": "username",
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "auth-input",
            "placeholder": "Mật khẩu",
            "autocomplete": "current-password",
        })
    )


class ListeningQuestionAdminForm(forms.ModelForm):
    upload_audio_mp3 = forms.FileField(
        required=False,
        label="Tải file MP3 lên Supabase",
        help_text="Chọn file .mp3 để lưu trên Supabase Storage. Nếu không chọn file mới, audio cũ sẽ được giữ nguyên."
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
            raise forms.ValidationError("Chỉ cho phép upload file MP3.")

        max_size = 80 * 1024 * 1024

        if file_obj.size > max_size:
            raise forms.ValidationError("File MP3 quá lớn. Giới hạn hiện tại là 80MB/file.")

        return file_obj
