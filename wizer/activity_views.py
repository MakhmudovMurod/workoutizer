import os
import logging

from django.shortcuts import render
from django.views.generic import DeleteView
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.urls import reverse

from wizer.views import MapView, get_all_form_field_ids
from wizer.models import Sport, Activity
from wizer.forms import AddActivityForm, EditActivityForm
from wizer.file_helper.gpx_exporter import save_activity_to_gpx_file
from wizer.plotting.plot_time_series import plot_time_series


log = logging.getLogger(__name__)


class ActivityView(MapView):
    template_name = "activity/activity.html"

    def get(self, request, activity_id):
        activity = Activity.objects.get(id=activity_id)
        context = super(ActivityView, self).get(request=request, list_of_activities=[activity])
        activity_context = {
            'sports': Sport.objects.all().order_by('name'),
            'activity': activity,
            'form_field_ids': get_all_form_field_ids(),
        }
        if activity.trace_file:
            script_time_series, div_time_series = plot_time_series(activity)
            activity_context['script_time_series'] = script_time_series
            activity_context['div_time_series'] = div_time_series
        return render(request, self.template_name, {**context, **activity_context})


def add_activity_view(request):
    sports = Sport.objects.all().order_by('name')
    if request.method == 'POST':
        form = AddActivityForm(request.POST)
        if form.is_valid():
            instance = form.save()
            instance.save()
            messages.success(request, f"Successfully added '{form.cleaned_data['name']}'")
            return HttpResponseRedirect(reverse('home'))
        else:
            log.warning(f"form invalid: {form.errors}")
    else:
        form = AddActivityForm()
    return render(request, 'activity/add_activity.html', {'sports': sports, 'form': form,
                                                          'form_field_ids': get_all_form_field_ids()})


def edit_activity_view(request, activity_id):
    sports = Sport.objects.all().order_by('name')
    log.debug(f"querying for activity id: {activity_id}")
    activity = Activity.objects.get(id=activity_id)
    form = EditActivityForm(request.POST or None, instance=activity)
    if request.method == 'POST':
        if form.is_valid():
            log.debug(f"got valid form: {form.cleaned_data}")
            form.save()
            messages.success(request, f"Successfully modified '{form.cleaned_data['name']}'")
            return HttpResponseRedirect(f"/activity/{activity_id}")
        else:
            log.warning(f"form invalid: {form.errors}")
    return render(request, 'activity/edit_activity.html', {'form': form, 'sports': sports, 'activity': activity,
                                                           'form_field_ids': get_all_form_field_ids()})


def download_activity(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    path = save_activity_to_gpx_file(activity=activity)
    if os.path.exists(path):
        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            return response
    raise Http404


class ActivityDeleteView(DeleteView):
    template_name = "activity/activity_confirm_delete.html"
    model = Activity
    slug_field = 'activity_id'
    success_url = "/"

    def get(self, request, *args, **kwargs):
        sports = Sport.objects.all().order_by('name')
        activity = Activity.objects.get(id=kwargs['pk'])
        return render(request, self.template_name, {'sports': sports, 'activity': activity,
                                                    'form_field_ids': get_all_form_field_ids()})


class DemoActivityDeleteView(DeleteView):
    template_name = "activity/demo_activity_confirm_delete.html"
    activities = Activity.objects.filter(is_demo_activity=True)

    def get(self, request, *args, **kwargs):
        sports = Sport.objects.all().order_by('name')
        log.debug(f"activities to be deleted: {self.activities}")
        return render(request, self.template_name, {'sports': sports, 'activities': self.activities,
                                                    'form_field_ids': get_all_form_field_ids()})

    def post(self, request, *args, **kwargs):
        log.debug(f"deleting: {self.activities}")
        for activity in self.activities:
            activity.delete()
        log.info(f"deleted demo activities")
        return HttpResponseRedirect(reverse('home'))
