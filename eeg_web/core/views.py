import json

import matplotlib.pyplot as plt
import numpy as np
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.generic import TemplateView
from core.forms import RegistrationForm
from core.models import EEGCheck
from core.models import Settings
from core.utils import AnalysisHelper


class StartPageView(TemplateView):
    template_name = 'core/start.html'


class DataFormatPageView(TemplateView):
    template_name = 'core/data_format.html'


class ResultPageView(TemplateView, View):
    template_name = 'core/result.html'
    success_url = reverse_lazy('core:result')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx

    def post(self, request):
        err = None
        data_list = None
        try:
            uploaded_file = self.request.FILES['eeg_data'].read()
            uploaded_file = uploaded_file.decode("utf-8")
            data_list = uploaded_file.split(" ")
            data_list = list(map(lambda x: int(x), data_list))
        except Exception:
            err = 'Ошибка в данных. Посмотрите страницу с форматом данных'
        ctx = self.get_context_data()
        ctx['data'] = data_list
        ctx['error'] = err
        setting_id = 1
        helper = AnalysisHelper(setting_id, data_list)
        answer = helper.get_answer_from_raw_data(data_list)
        image = helper.get_image_by_answer(answer)
        ctx['image'] = image
        ctx['has_pattern'] = answer['has_pattern']
        settings = Settings.objects.get(id=setting_id)

        record = EEGCheck()
        record.user = self.request.user
        record.has_patterns = answer['has_pattern'] | False
        record.accuracy = settings.accuracy
        record.result = json.dumps(answer)
        record.uploaded_file = self.request.FILES['eeg_data']
        record.settings = settings
        record.save()

        return self.render_to_response(ctx)


class LoginView(LoginView):
    template_name = 'core/login.html'
    success_url = reverse_lazy('core:start_page')


class RegistrationView(CreateView):
    form_class = RegistrationForm
    template_name = 'core/register.html'
    success_url = reverse_lazy('core:login')


class HistoryView(ListView):
    template_name = 'core/user_list.html'
    model = EEGCheck

    def get_queryset(self):
        queryset = EEGCheck.objects.filter(user=self.request.user).order_by('-check_time')
        return queryset
