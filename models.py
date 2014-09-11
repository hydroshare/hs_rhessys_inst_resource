from django.contrib.contenttypes import generic
from django.contrib.auth.models import User, Group
from django.db import models
from mezzanine.pages.models import Page, RichText
from mezzanine.core.models import Ownable
from hs_core.models import AbstractResource, resource_processor
import django.dispatch
from .forms import InputForm
from mezzanine.pages.page_processors import processor_for
from hs_core.hydroshare.resource import post_create_resource
from django.dispatch import receiver
import zipfile
import ConfigParser
import cStringIO as StringIO
import os

#
# To create a new resource, use these three super-classes. 
#

class InstResource(Page, RichText, AbstractResource):
    class Meta:
        verbose_name = 'RHESSys Instance Resource'
    name = models.CharField(max_length=50)
    git_repo = models.URLField()
    git_username = models.CharField(max_length=50)
    # later change it to use Jeff's password encode function with django SECRET_KEY
    git_password = models.CharField(max_length=50)
    commit_id = models.CharField(max_length=50)
    model_desc = models.CharField(max_length=500)
    git_branch = models.CharField(max_length=50)
    study_area_bbox = models.CharField(max_length = 50)
    model_command_line_parameters = models.CharField(max_length=500)
    project_name = models.CharField(max_length=100)

    def can_add(self, request):
        return AbstractResource.can_add(self, request)

    def can_change(self, request):
        return AbstractResource.can_change(self, request)

    def can_delete(self, request):
        return AbstractResource.can_delete(self, request)

    def can_view(self, request):
        return AbstractResource.can_view(self, request)

@receiver(post_create_resource)
def rhessys_post_trigger(sender, **kwargs):
    if sender is InstResource:
        resource = kwargs['resource']
        files = resource.files.all()
        # Assume only one file in files, and that that file is a zipfile
        infile = files[0].resource_file
        infile.open('rb')
        zfile = zipfile.ZipFile(infile)

        # Get list of files in zipfile
        zlist = zfile.namelist()
        # Assume zipfile contains a single directory
        root = zlist[0]

        # Read metadata.txt from zipfile
        metadataFilename = os.path.join(root, 'metadata.txt')

        metadata = zfile.read(metadataFilename)

        # Read metadata into ConfigParser
        md = ConfigParser.ConfigParser()
        md.readfp(StringIO.StringIO(metadata))

        resource.project_name = root

        resource.model_desc = md.get('rhessys', 'model_description')

        resource.git_repo = md.get('rhessys', 'rhessys_src')

        resource.commit_id = md.get('rhessys', 'rhessys_sha')

        resource.study_area_bbox = md.get('study_area', 'bbox_wgs84')
        resource.save()
        zfile.close()

processor_for(InstResource)(resource_processor)

@processor_for(InstResource)
def main_page(request, page):
    if(request.method == 'POST'):
        form = InputForm(request.POST)
        if(form.is_valid()):
            content_model = page.get_content_model()
            content_model.name=form.cleaned_data['name']
            content_model.model_desc = form.cleaned_data['model_desc']
            content_model.study_area_bbox = form.cleaned_data['study_area_bbox']
            content_model.git_repo = form.cleaned_data['git_repo']
            content_model.git_username = form.cleaned_data['git_username']
            content_model.git_password = form.cleaned_data['git_password']
            content_model.commit_id = form.cleaned_data['commit_id']
            content_model.git_branch = form.cleaned_data['git_branch']
            content_model.model_command_line_parameters = form.cleaned_data['model_command_line_parameters']
            content_model.project_name = form.cleaned_data['project_name']
            content_model.save()
    else:
        cm =page.get_content_model()
        form = InputForm(initial={
            'project_name' : cm.project_name,
            'model_desc' : cm.model_desc,
            'git_repo' : cm.git_repo,
            'commit_id' : cm.commit_id,
            'study_area_bbox' : cm.study_area_bbox
        })

    return  {'form': form}