#Management Metrics Overhaul
[001 LandingPage] #Default landing page
[002 sls] #Handles signup, logout and signin

[001 LandingPage]
  URLs:
    -url(r'^$',views.home,name="home"),
      #Landing page for the site.

  Model: none
  admin: none
  form: none

[002 sls]
  URLs: through main URLs file
    -url(r'^login/$', auth_views.login,name='login'),
      #Login handled by django template
    -url(r'^logout/$', auth_views.logout,name='logout'),
      #Logout handled by django template
    -url(r'^register/', views.signup,name='register'),
      #Register handled by altered django template

  Model:
    -Djago default
    -Profile: add in user premissions
      ~user: 121 with Auth.User
      ~job_title:
      ~region:
      ~store:
      ~section:
  Admin:Django default
  Form:Django default

  Groups for permissions
    1.Owner,sysadmin
    2.Regional Manager
    3.Store Manager
    4.Store Other

[003 OPR2]
  URLs:
    -url(r'^$',views.model_form_upload,name="home"),
      #Default page for uploading a single OPR
    -url(r'^show/$',views.show_file,name="show_file"),
      #shows list of OPRs that where uploaded via internet
    -url(r'^(?P<store>[-\w]+)/$',views.show_opr_list,name="show_opr_list"),
      #Show oprs by year for selected store.
    -url(r'^(?P<store>[-\w]+)/(?P<pk>\d+)/$',views.show_opr_dept,name="show_opr_dept"),
      #opens said OPR

  Views:
    -

  Models:
    -Document: handling OPR upload
      ~description: opr name
      ~document: opr save location
      ~uploaded_at: DateTimeField

    -StoreSave: Store meta data.
      ~store_town: store town name location
      ~store(primary_key): ID given to the store.
      ~region: default 0 set for regional managers if  needed

    -FileDate: Handles file type with corrosponding dates.
      ~store(unique_together):1-2-M(StoreSave)
      ~date(unique_together): DateField
      ~file_type(unique_together): Type of file saved.
      ~financialYear: typically year of the date field but can be offset.
      ~weeknumber: weeknumber based from financialYear

    -OPRSave:
      ~date(unique_together):1-2-m(FileDate)
      ~name(unique_together):
      ~catagory: selecting the catagory/sub-catagory
    -DateSales: Multi-table inheritance(OPRSave)
      ~sale:
      ~vat:
      ~part:
      ~margin:
    -WeekSales: Multi-table inheritance(OPRSave)
      ~sale:
      ~vat:
      ~part:
      ~margin:
    -YearSales: Multi-table inheritance(OPRSave)
      ~sale:
      ~vat:
      ~part:
      ~margin:
"# Public-Management-Metrics-Overhaul" 
"# Public-Management-Metrics-Overhaul" 
