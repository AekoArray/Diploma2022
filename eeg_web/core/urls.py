from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from django.conf import settings
from core.views import DataFormatPageView
from core.views import HistoryView
from core.views import LoginView
from core.views import RegistrationView
from core.views import ResultPageView
from core.views import StartPageView

app_name = 'core'
urlpatterns = [
    path('', StartPageView.as_view(), name='start_page'),
    path('data-format/', DataFormatPageView.as_view(), name='data_format'),
    path('result/', ResultPageView.as_view(), name='result'),
    path('history/', HistoryView.as_view(), name='history'),
    path('register/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('core:start_page')), name='logout'),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
