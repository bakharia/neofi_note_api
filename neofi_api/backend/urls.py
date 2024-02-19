from django.urls import path
from .views import signup, signin, create_note, list_notes,get_note, share_note, update_note, get_note_version_history

urlpatterns = [
    path(
            route = 'signup/', 
            view= signup,
            name = 'signup'
        ),
    path(
            route = 'login/',
            view = signin
        ),
    path(
            route = 'notes/create/', 
            view= create_note
        ),
    path(
            route = 'notes/list/', 
            view = list_notes
        ),
    path(
            route = 'notes/<int:id>/', 
            view = get_note
        ),
    path(
            route = 'notes/share/', 
            view = share_note
        ),
    path(
            route = 'notes/version-history/<int:id>/', 
            view= get_note_version_history
        ),
    path(
        route='notes/update/<int:id>/',  # Define the route for update_note with <int:id> parameter
        view=update_note  # Assign the update_note view to the defined route
    )
]