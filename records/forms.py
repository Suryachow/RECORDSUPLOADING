from django import forms
from .models import StudentRecord

class StudentForm(forms.ModelForm):
    class Meta:
        model = StudentRecord
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        # Force ALL fields to be required in the form, even if the Model says blank=True
        for field_name, field in self.fields.items():
            field.required = True


