from django import forms

class InputForm(forms.Form):
    name = forms.CharField(label="Name", max_length=50)
    model_desc = forms.CharField(label="Model description", max_length=500)
    study_area_bbox = forms.CharField(label="Study area bounding box", max_length = 50)
    git_repo = forms.URLField(label="git repository")
    git_username = forms.CharField(label="git user name", max_length=50, required=False)
    git_password = forms.CharField(label="git password", widget=forms.PasswordInput(), required=False)
    commit_id = forms.CharField(label="git commit id", max_length=50)
    git_branch = forms.CharField(label="git branch", max_length=50)
    model_command_line_parameters = forms.CharField(label="model command line parameters", max_length=50, required=False)
    project_name = forms.CharField(label="project name", max_length=100)