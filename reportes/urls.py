from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dynamic-pricing/', views.DynamicPricingReportView.as_view(), name='dynamic_pricing'),
]
