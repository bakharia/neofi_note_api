from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from .models import Note, NoteVersion, SharedNoteUser
from .serializers import UserSerializer, NoteSerializer
from datetime import datetime

@api_view(['POST'])
def signup(request):
    """
    View to handle user registration.

    Params:
    - request: HTTP request object containing user registration data.

    Returns:
    - Response: HTTP response indicating success or failure of user registration.
    """
    try:
        # Deserialize request data
        serializer = UserSerializer(data=request.data)
        
        # Check if serializer data is valid
        if serializer.is_valid():
            # Check if the username is unique
            username = serializer.validated_data.get('username')
            if User.objects.filter(username=username).exists():
                raise ValidationError("Username already exists.")
            
            # Check if the email is unique
            email = serializer.validated_data.get('email')
            if User.objects.filter(email=email).exists():
                raise ValidationError("Email already exists.")
            
            # Save the user
            serializer.save()
            
            return Response(
                data={"message": "User created successfully"},
                status=status.HTTP_201_CREATED
            )
        else:
            # Return error response for invalid data
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
    except ValidationError as e:
        # Return error response for validation errors
        return Response(
            data={"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        # Return error response for other exceptions
        return Response(
            data={"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def signin(request):
    """
    View to handle user login.

    Params:
    - request: HTTP request object containing user login credentials.

    Returns:
    - Response: HTTP response containing authentication token or error message.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(
        request=request,
        username=username,
        password=password
    )

    if user is not None:
        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            data={
                'message': 'Login successful',
                'token': token.key,
            },
            status=status.HTTP_200_OK
        )
    
    return Response(
        data={'error': 'Invalid username or password'},
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_note(request):
    """
    View to handle creation of a new note by an authenticated user.

    Params:
    - request: HTTP request object containing note creation data.

    Returns:
    - Response: HTTP response indicating success or failure of note creation.
    """
    user = request.user

    serializer = NoteSerializer(
        data={
            'user': user.pk,
            'title': request.data['title'],
            'content': request.data['content']
        }
    )

    if serializer.is_valid():
        serializer.save(user=user)
        
        # Format and return response data
        utc_timestamp = serializer.data['created_at']
        utc_datetime = datetime.strptime(utc_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
        formatted_local_time = utc_datetime.strftime('%Y-%m-%d, %H:%M UTC')

        return Response(
            data={
                "message": "Note created successfully!",
                "id": serializer.data['id'],
                "title": serializer.data['title'],
                "created_at": formatted_local_time
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(
        data=serializer.errors, 
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notes(request):
    """
    View to list all notes accessible to the authenticated user.

    Params:
    - request: HTTP request object.

    Returns:
    - Response: HTTP response containing list of notes or appropriate error message.
    """
    try:
        user = request.user

        # Get all notes created by the authenticated user
        user_notes = Note.objects.filter(user=user)

        # Get all notes shared with the authenticated user
        shared_note_ids = SharedNoteUser.objects.filter(user=user).values_list('note_id', flat=True)

        # Combine user's own notes and shared notes
        all_notes = user_notes | Note.objects.filter(pk__in=shared_note_ids)

        # If no notes are found, return an empty list
        if not all_notes:
            return Response(
                data={'message': 'No notes found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize the notes data
        serializer = NoteSerializer(all_notes, many=True)

        # Extract id and title fields from each note
        notes_data = [{'id': note.id, 'title': note.title} for note in all_notes]

        return Response(
            data=notes_data,
            status=status.HTTP_200_OK
        )
    except Note.DoesNotExist:
        return Response(
            data={'error': 'No notes found for the user'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            data={'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_note(request, id):
    """
    View to retrieve a specific note by its ID.

    Params:
    - request: HTTP request object.
    - id: ID of the note to retrieve.

    Returns:
    - Response: HTTP response containing the requested note's details or an error message.
    """
    try:
        note = Note.objects.get(pk=id)

        if note.user == request.user or SharedNoteUser.objects.filter(note=note, user=request.user).exists():
            serializer = NoteSerializer(note)

            # Parse the UTC timestamp from serializer.data['created_at']
            created_datetime = datetime.strptime(serializer.data['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            updated_datetime = datetime.strptime(serializer.data['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')

            # Format local time as "year-month-day hours:minutes"
            frmt_created = created_datetime.strftime('%Y-%m-%d, %H:%M UTC')
            frmt_updated = updated_datetime.strftime('%Y-%m-%d, %H:%M UTC')
        
            return Response(
                data={
                    'title': serializer.data['title'],
                    'content': serializer.data['content'],
                    'created_at': frmt_created,
                    'updated_at': frmt_updated
                },
                status=status.HTTP_200_OK
            )
        
        else:
            return Response(
                data={
                    'error': 'Unauthorized access'
                },
                status=status.HTTP_403_FORBIDDEN
            )
    except Note.DoesNotExist:
        return Response(
            data={
                'error': 'Note does not exist'
            }, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def share_note(request):
    """
    View to share a note with other users.

    Params:
    - request: HTTP request object containing note ID and list of usernames to share with.

    Returns:
    - Response: HTTP response indicating success or failure of note sharing.
    """
    try:
        note_id = request.data.get('note_id')
        username_list = request.data.get('usernames')
        
        # Ensure note_id is provided and valid
        if not note_id:
            return Response(
                data={'error': 'Note ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ensure the note exists and the authenticated user has access to it
        note = Note.objects.get(pk=note_id, user=request.user)
        
        # Ensure usernames list is provided and not empty
        if not username_list:
            return Response(
                data={'error': 'List of usernames is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get users to share with
        users_to_share_with = User.objects.filter(username__in=username_list)
        
        # Share the note with each user
        for user in users_to_share_with:
            shared_user, created = SharedNoteUser.objects.get_or_create(note=note, user=user)
        
        return Response(
            data={'message': 'Note shared successfully'}, 
            status=status.HTTP_200_OK
        )
    except Note.DoesNotExist:
        return Response(
            data={'error': 'Note does not exist or you do not have permission to share it'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            data={'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_note(request, id):
    """
    View to update a note's content.

    Params:
    - request: HTTP request object containing updated note content.
    - id: ID of the note to update.

    Returns:
    - Response: HTTP response indicating success or failure of note update.
    """
    try:
        note = Note.objects.get(pk=id)
        # Check if the user is the note owner or a shared user
        if note.user == request.user or SharedNoteUser.objects.filter(note=note, user=request.user).exists():
            # Save current note version with timestamp
            NoteVersion.objects.create(note=note, user=request.user, changes=request.data.get('content'))
            # Update note content
            new_content = request.data.get('content')
            note.content += "\n" + new_content
            # Save the updated note
            note.save()
            serializer = NoteSerializer(note)

            # Parse the UTC timestamp from serializer.data['created_at']
            created_datetime = datetime.strptime(serializer.data['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            updated_datetime = datetime.strptime(serializer.data['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')

            # Format local time as "year-month-day hours:minutes"
            frmt_created = created_datetime.strftime('%Y-%m-%d, %H:%M UTC')
            frmt_updated = updated_datetime.strftime('%Y-%m-%d, %H:%M UTC')

            return Response(
                data={
                    'title': serializer.data['title'],
                    'updated_content': serializer.data['content'],
                    'created_at': frmt_created,
                    'updated_at': frmt_updated
                }, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                data={
                    'error': 'Unauthorized access'
                }, 
                status=status.HTTP_403_FORBIDDEN
            )
    except Note.DoesNotExist:
        return Response(
            data={
                'error': 'Note does not exist'
            }, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def get_note_version_history(request, id):
    """
    View to retrieve the version history of a note.

    Params:
    - request: HTTP request object.
    - id: ID of the note to retrieve version history for.

    Returns:
    - Response: HTTP response containing the version history of the note or an error message.
    """
    try:
        note = Note.objects.get(pk=id)
        if note.user == request.user or SharedNoteUser.objects.filter(note=note, user=request.user).exists():
            versions = NoteVersion.objects.filter(note=note).values('timestamp', 'user__username', 'changes')
            return Response(
                data=versions, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                data={
                    'error': 'Unauthorized access'
                }, 
                status=status.HTTP_403_FORBIDDEN
            )
    except Note.DoesNotExist:
        return Response(
            data={
                'error': 'Note does not exist'
            }, 
            status=status.HTTP_404_NOT_FOUND
        )

