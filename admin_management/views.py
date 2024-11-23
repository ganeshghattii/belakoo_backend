from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from user_management.models import User
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from content_management.models import Campus

class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        # Check if user is authenticated and has admin role
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == User.Role.ADMIN
        )

    def has_object_permission(self, request, view, obj):
        # Object level permission check
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == User.Role.ADMIN
        )

class VolunteerListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AdminPermission]

    def get(self, request):
        volunteers = User.objects.filter(role=User.Role.VOLUNTEER)
        data = [{
            'id': str(volunteer.id),
            'email': volunteer.email,
            'name': volunteer.name,
            'is_active': volunteer.is_active
        } for volunteer in volunteers]
        return Response(data)

class CreateVolunteerView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request):
        email = request.data.get('email')
        name = request.data.get('name')
        password = request.data.get('password')

        if User.objects.filter(email=email).exists():
            return Response({'msg': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_volunteer = User.objects.create_user(
                email=email,
                name=name,
                password=password,
                role=User.Role.VOLUNTEER
            )
            return Response({
                'msg': 'Volunteer created successfully',
                'id': str(new_volunteer.id)
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'msg': f'Error creating volunteer: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteVolunteerView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AdminPermission]

    def delete(self, request, volunteer_id):
        try:
            volunteer = User.objects.get(id=volunteer_id, role=User.Role.VOLUNTEER)
            volunteer.delete()
            return Response({'msg': 'Volunteer deleted successfully'}, 
                          status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'msg': 'Volunteer not found'}, 
                          status=status.HTTP_404_NOT_FOUND)

class CampusManagementView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request):
        """Create a new campus"""
        campus_code = request.data.get('campus_code')
        name = request.data.get('name')
        description = request.data.get('description')

        # Validate required fields
        if not campus_code or not name or not description:
            return Response({
                'msg': 'campus_code, name, and description are required fields.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check for unique campus_code
        if Campus.objects.filter(campus_code=campus_code).exists():
            return Response({
                'msg': 'campus_code must be unique.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create campus without icon
            campus = Campus.objects.create(
                campus_code=campus_code,
                name=name,
                description=description
            )
            return Response({
                'msg': 'Campus created successfully',
                'data': {
                    'id': str(campus.id),
                    'campus_code': campus.campus_code,
                    'name': campus.name,
                    'description': campus.description
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'msg': f'Error creating campus: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, campus_id):
        """Update an existing campus"""
        try:
            campus = Campus.objects.get(id=campus_id)

            # Validate required fields
            campus_code = request.data.get('campus_code')
            name = request.data.get('name')
            description = request.data.get('description')

            if campus_code is not None:
                # Check for unique campus_code if it's being updated
                if Campus.objects.filter(campus_code=campus_code).exclude(id=campus.id).exists():
                    return Response({
                        'msg': 'campus_code must be unique.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                campus.campus_code = campus_code
            if name is not None:
                campus.name = name
            if description is not None:
                campus.description = description

            campus.save()

            return Response({
                'msg': 'Campus updated successfully',
                'data': {
                    'id': str(campus.id),
                    'campus_code': campus.campus_code,
                    'name': campus.name,
                    'description': campus.description
                }
            })
        except Campus.DoesNotExist:
            return Response({
                'msg': 'Campus not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': f'Error updating campus: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, campus_id):
        """Delete a campus"""
        try:
            campus = Campus.objects.get(id=campus_id)
            campus.delete()
            return Response({
                'msg': 'Campus deleted successfully'
            }, status=status.HTTP_200_OK)
        except Campus.DoesNotExist:
            return Response({
                'msg': 'Campus not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': f'Error deleting campus: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
