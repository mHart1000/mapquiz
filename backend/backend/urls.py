"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from quizzes.views import (
    QuizViewSet, CityList, CityDetail,
    NeighborhoodList, QuizQuestion, QuizAnswer,
)


router = DefaultRouter()
router.register(r'quizzes', QuizViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/cities/<slug:slug>/neighborhoods/', NeighborhoodList.as_view(), name='neighborhood-list'),
    path('api/cities/<slug:slug>/quiz/question/', QuizQuestion.as_view(), name='quiz-question'),
    path('api/cities/<slug:slug>/quiz/answer/', QuizAnswer.as_view(), name='quiz-answer'),
    path('api/cities/<slug:slug>/', CityDetail.as_view(), name='city-detail'),
    path('api/cities/', CityList.as_view(), name='city-list'),
 ]
