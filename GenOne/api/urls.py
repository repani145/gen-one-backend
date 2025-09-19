# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"rules", views.CustomRuleTemplateUIViewSet, basename="custom-rule-template")

urlpatterns = [
    # path('login/', LoginView.as_view(), name='login'),
    path("data_object", views.DataObjectView.as_view(), name="data_object"),
    path("data_object/<str:id>", views.DataObjectView.as_view(), name="data_object_id"),

    path('all_data_object',views.AllDataObjectView.as_view(),name='all_data_object'),
    path('dependencies',views.AllDependenciesView.as_view(),name='dependencies'),

    path("specs/", views.SpecsAPIView.as_view()),         # POST create
    path("specs/<int:id>/", views.SpecsAPIView.as_view()),  # GET single, PUT, DELETE

    path("specs/reorder/", views.ReorderSpecsView.as_view(), name="reorder-specs"),

    path("specs/download-template/", views.SpecsTemplateDownloadAPIView.as_view(), name="specs-download-template"),

     path("", include(router.urls)), # TRIANGLE to get form fields to render in UI

     path('all-rules',views.AllRulesView.as_view(),name='all-rules'),
     #TO GET LIST OF ALL EXSITING RULES[RILE1,RULE2,RULE3....]

     path("apply-rule/", views.RuleAppliedView.as_view(), name="rule-applied"),
     # TO ADD(POST) NEW RULE TO AN SPEC FIELD
     path("apply-rule/<int:pk>/", views.RuleAppliedView.as_view(), name="rules-detail"), # GET/PUT/DELETE

    #  path("rules/applied/", views.RuleAppliedView.as_view(), name="rules-applied-list"),

     path("rules-assigned/", views.RuleAppliedGetView.as_view(), name="rules-assigned"), # Circle 
     #FOR ALL RULES APPLIED FILTES

     path("rule_by_spec_id/<int:spec_id>/", views.RuleAppliedBySpecView.as_view(), name="rule-by-spec-id"),
        #TO GET ALL RULES APPLIED TO A PARTICULAR SPEC ID

    path("handle-file/", views.FileUploadAPIView.as_view(), name="handle-file"), #get all
    path("handle-file/<int:id>/", views.FileUploadAPIView.as_view(), name="handle-file-id"), # get single record,delete 
    # post,get(#handle-files/<int:object_id>/)

    path("file-data/<int:object_id>/",views.DataFileLatestView.as_view(),name='file-data-view'),

    path("latest_validated_file/", views.LatestValidatedFilesView.as_view(), name="latest_validated_file"),

    path("pre_validation_check/<int:data_object_id>/", views.PreValidationCheckAndValidationView.as_view(), name="file-versions"),

    path("logs-view/<str:object_name>/", views.GetLatestLogDataView.as_view(), name="view-latest-log"),
    path('download-log/<str:object_name>/',views.DownloadLatestLogAPIView.as_view(),name='download-log'),

    path("upload-status/<str:upload_id>/", views.UploadStatusView.as_view(), name="upload_status"),

    path('validation-progress/<task_id>/',views.ValidationProgressView.as_view(),name = 'validation-progress'),

    # path('specs_with_rules/<int:objectName_id>/',views.SpecWithRulesDetailView.as_view(),name='specs_with_rules'),
    # GET /api/spec_with_rules/5/?tab=General
    # path("validation-progress/<int:object_id>/", views.ValidationProgressView.as_view(), name="validation-progress"),

    # Get current validation progress for a DataObject
    # path("validation/progress/<int:object_id>/",views.ValidationProgressView.as_view(), name="validation-progress"),
    path('datafiles/<int:pk>/request-approval/',views.RequestApprovalView.as_view(),name='request-approval'),
    
    path("approval/<str:token>/", views.approval_form, name="approval-form"),
    path('approval-success/', views.approval_success_view, name='approval-success'),

    #  path("datafiles/<int:data_file_id>/comments/", views.ApprovalCommentListView.as_view(), name="approval-comments"),
    path("dataobjects/<int:data_object_id>/comments/", views.DataObjectCommentsView.as_view(), name="dataobject-comments"),

    path("specs/download-upload/", views.SpecsDownloadUploadView.as_view(), name="download-specs"),

    path("dataload/", views.DataLoad.as_view(), name="data-load"),
]


# TRIANGLE
# GET /api/rules/ — list all rules (with schema in each row)
# POST /api/rules/ — create a rule (send JSON body)
# GET /api/rules/{pk}/ — retrieve by id (PK)
# PUT/PATCH /api/rules/{pk}/ — update
# DELETE /api/rules/{pk}/
# Custom: GET /api/rules/schema/<rule_name>/ — retrieve by rule_name (returns the serializer object with schema field)


# CIRCLE
# api/rules-assigned/?objectName=Customer
# api/rules-assigned/?rule_applied=ALLOWED_ONLY_IF
# api/rules-assigned/?created_after=2025-08-01&created_before=2025-08-31
# api/rules-assigned/?search=email
# api/rules-assigned/?ordering=rule_applied
# api/rules-assigned/?ordering=-created_at
