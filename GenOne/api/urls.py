# urls.py
from django.urls import path
from .views import DataObjectView,AllDataObjectView,AllDependenciesView,SpecsAPIView,ReorderSpecsView,SpecsTemplateDownloadAPIView

urlpatterns = [
    # path('login/', LoginView.as_view(), name='login'),
    path("data_object", DataObjectView.as_view(), name="data_object"),
    path("data_object/<str:id>", DataObjectView.as_view(), name="data_object_id"),

    path('all_data_object',AllDataObjectView.as_view(),name='all_data_object'),
    path('dependencies',AllDependenciesView.as_view(),name='dependencies'),

    path("specs/", SpecsAPIView.as_view()),         # POST create
    path("specs/<int:id>/", SpecsAPIView.as_view()),  # GET single, PUT, DELETE

    path("specs/reorder/", ReorderSpecsView.as_view(), name="reorder-specs"),

    path("specs/download-template/", SpecsTemplateDownloadAPIView.as_view(), name="specs-download-template"),
]
# /api/specs/reorder/