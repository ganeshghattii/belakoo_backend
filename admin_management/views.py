from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from user_management.models import User
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from content_management.models import Campus, Grade, Subject, Proficiency, Lesson
import json

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

class GradeManagementView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request):
        """Create a new grade"""
        grade_code = request.data.get('grade_code')
        name = request.data.get('name')
        campus_id = request.data.get('campus_id')

        # Validate required fields
        if not all([grade_code, name, campus_id]):
            return Response({
                'msg': 'grade_code, name, and campus_id are required fields.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify campus exists
            campus = Campus.objects.get(id=campus_id)
            
            # Check if grade_code is unique within the campus
            if Grade.objects.filter(grade_code=grade_code, campus=campus).exists():
                return Response({
                    'msg': 'grade_code must be unique within a campus.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create grade
            grade = Grade.objects.create(
                grade_code=grade_code,
                name=name,
                campus=campus
            )
            
            return Response({
                'msg': 'Grade created successfully',
                'data': {
                    'id': str(grade.id),
                    'grade_code': grade.grade_code,
                    'name': grade.name,
                    'campus_id': str(grade.campus.id),
                    'campus_name': grade.campus.name
                }
            }, status=status.HTTP_201_CREATED)

        except Campus.DoesNotExist:
            return Response({
                'msg': 'Campus not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': f'Error creating grade: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, grade_id):
        """Update an existing grade"""
        try:
            grade = Grade.objects.get(id=grade_id)
            
            grade_code = request.data.get('grade_code')
            name = request.data.get('name')
            campus_id = request.data.get('campus_id')

            if grade_code is not None:
                # Check if grade_code is unique within the campus
                if Grade.objects.filter(
                    grade_code=grade_code, 
                    campus=grade.campus
                ).exclude(id=grade.id).exists():
                    return Response({
                        'msg': 'grade_code must be unique within a campus.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                grade.grade_code = grade_code

            if name is not None:
                grade.name = name

            if campus_id is not None:
                try:
                    new_campus = Campus.objects.get(id=campus_id)
                    # Check grade_code uniqueness in new campus
                    if Grade.objects.filter(
                        grade_code=grade.grade_code, 
                        campus=new_campus
                    ).exists():
                        return Response({
                            'msg': 'grade_code must be unique within the new campus.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    grade.campus = new_campus
                except Campus.DoesNotExist:
                    return Response({
                        'msg': 'New campus not found'
                    }, status=status.HTTP_404_NOT_FOUND)

            grade.save()

            return Response({
                'msg': 'Grade updated successfully',
                'data': {
                    'id': str(grade.id),
                    'grade_code': grade.grade_code,
                    'name': grade.name,
                    'campus_id': str(grade.campus.id),
                    'campus_name': grade.campus.name
                }
            })

        except Grade.DoesNotExist:
            return Response({
                'msg': 'Grade not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': f'Error updating grade: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, grade_id):
        """Delete a grade"""
        try:
            grade = Grade.objects.get(id=grade_id)
            grade.delete()
            return Response({
                'msg': 'Grade deleted successfully'
            }, status=status.HTTP_200_OK)
        except Grade.DoesNotExist:
            return Response({
                'msg': 'Grade not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': f'Error deleting grade: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class SubjectManagementView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request):
        """Create a new subject"""
        subject_code = request.data.get('subject_code')
        name = request.data.get('name')
        grade_id = request.data.get('grade_id')
        colorcode = request.data.get('colorcode')
        icon = request.data.get('icon')

        # Validate required fields
        if not all([subject_code, name, grade_id, colorcode]):
            return Response({
                'msg': 'subject_code, name, grade_id, and colorcode are required fields.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify grade exists
            grade = Grade.objects.get(id=grade_id)
            
            # Check if subject_code is unique
            if Subject.objects.filter(subject_code=subject_code).exists():
                return Response({
                    'msg': 'subject_code must be unique.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create subject
            subject = Subject.objects.create(
                subject_code=subject_code,
                name=name,
                grade=grade,
                colorcode=colorcode,
                icon=icon
            )
            
            return Response({
                'msg': 'Subject created successfully',
                'data': {
                    'id': str(subject.id),
                    'subject_code': subject.subject_code,
                    'name': subject.name,
                    'grade_id': str(subject.grade.id),
                    'grade_name': subject.grade.name,
                    'colorcode': subject.colorcode,
                    'icon': subject.icon
                }
            }, status=status.HTTP_201_CREATED)

        except Grade.DoesNotExist:
            return Response({
                'msg': 'Grade not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': f'Error creating subject: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, subject_id):
        """Update an existing subject"""
        try:
            subject = Subject.objects.get(id=subject_id)
            
            subject_code = request.data.get('subject_code')
            name = request.data.get('name')
            grade_id = request.data.get('grade_id')
            colorcode = request.data.get('colorcode')
            icon = request.data.get('icon')
            if subject_code is not None:
                # Check if subject_code is unique
                if Subject.objects.filter(
                    subject_code=subject_code
                ).exclude(id=subject.id).exists():
                    return Response({
                        'msg': 'subject_code must be unique.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                subject.subject_code = subject_code

            if name is not None:
                subject.name = name

            if grade_id is not None:
                try:
                    new_grade = Grade.objects.get(id=grade_id)
                    subject.grade = new_grade
                except Grade.DoesNotExist:
                    return Response({
                        'msg': 'New grade not found'
                    }, status=status.HTTP_404_NOT_FOUND)

            if colorcode is not None:
                subject.colorcode = colorcode

            if icon is not None:
                subject.icon = icon

            subject.save()

            return Response({
                'msg': 'Subject updated successfully',
                'data': {
                    'id': str(subject.id),
                    'subject_code': subject.subject_code,
                    'name': subject.name,
                    'grade_id': str(subject.grade.id),
                    'grade_name': subject.grade.name,
                    'colorcode': subject.colorcode,
                    'icon': subject.icon
                }
            })

        except Subject.DoesNotExist:
            return Response({
                'msg': 'Subject not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': f'Error updating subject: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, subject_id):
        """Delete a subject"""
        try:
            subject = Subject.objects.get(id=subject_id)
            subject.delete()
            return Response({
                'msg': 'Subject deleted successfully'
            }, status=status.HTTP_200_OK)
        except Subject.DoesNotExist:
            return Response({
                'msg': 'Subject not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': f'Error deleting subject: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class ProficiencyManagementView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request):
        """Create a new proficiency"""
        proficiency_code = request.data.get('proficiency_code')
        name = request.data.get('name')
        subject_id = request.data.get('subject_id')

        # Validate required fields
        if not all([proficiency_code, name, subject_id]):
            return Response({
                'msg': 'proficiency_code, name, and subject_id are required fields.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify subject exists
            subject = Subject.objects.get(id=subject_id)
            
            # Check if proficiency_code is unique within the subject
            if Proficiency.objects.filter(proficiency_code=proficiency_code, subject=subject).exists():
                return Response({
                    'msg': 'proficiency_code must be unique within a subject.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create proficiency
            proficiency = Proficiency.objects.create(
                proficiency_code=proficiency_code,
                name=name,
                subject=subject
            )
            
            return Response({
                'msg': 'Proficiency created successfully',
                'data': {
                    'id': str(proficiency.id),
                    'proficiency_code': proficiency.proficiency_code,
                    'name': proficiency.name,
                    'subject_id': str(proficiency.subject.id),
                    'subject_name': proficiency.subject.name
                }
            }, status=status.HTTP_201_CREATED)

        except Subject.DoesNotExist:
            return Response({
                'msg': 'Subject not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': f'Error creating proficiency: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, proficiency_id):
        """Update an existing proficiency"""
        try:
            proficiency = Proficiency.objects.get(id=proficiency_id)
            
            proficiency_code = request.data.get('proficiency_code')
            name = request.data.get('name')
            subject_id = request.data.get('subject_id')

            if proficiency_code is not None:
                # Check if proficiency_code is unique within the subject
                if Proficiency.objects.filter(
                    proficiency_code=proficiency_code, 
                    subject=proficiency.subject
                ).exclude(id=proficiency.id).exists():
                    return Response({
                        'msg': 'proficiency_code must be unique within a subject.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                proficiency.proficiency_code = proficiency_code

            if name is not None:
                proficiency.name = name

            if subject_id is not None:
                try:
                    new_subject = Subject.objects.get(id=subject_id)
                    # Check proficiency_code uniqueness in new subject
                    if Proficiency.objects.filter(
                        proficiency_code=proficiency.proficiency_code, 
                        subject=new_subject
                    ).exists():
                        return Response({
                            'msg': 'proficiency_code must be unique within the new subject.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    proficiency.subject = new_subject
                except Subject.DoesNotExist:
                    return Response({
                        'msg': 'New subject not found'
                    }, status=status.HTTP_404_NOT_FOUND)

            proficiency.save()

            return Response({
                'msg': 'Proficiency updated successfully',
                'data': {
                    'id': str(proficiency.id),
                    'proficiency_code': proficiency.proficiency_code,
                    'name': proficiency.name,
                    'subject_id': str(proficiency.subject.id),
                    'subject_name': proficiency.subject.name
                }
            })

        except Proficiency.DoesNotExist:
            return Response({
                'msg': 'Proficiency not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': f'Error updating proficiency: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, proficiency_id):
        """Delete a proficiency"""
        try:
            proficiency = Proficiency.objects.get(id=proficiency_id)
            proficiency.delete()
            return Response({
                'msg': 'Proficiency deleted successfully'
            }, status=status.HTTP_200_OK)
        except Proficiency.DoesNotExist:
            return Response({
                'msg': 'Proficiency not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': f'Error deleting proficiency: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class LessonManagementView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request):
        """Create a new lesson"""
        lesson_code = request.data.get('lesson_code')
        name = request.data.get('name')
        subject_id = request.data.get('subject_id')
        grade_id = request.data.get('grade_id')
        proficiency_id = request.data.get('proficiency_id')

        # Validate required fields
        if not all([lesson_code, name, subject_id, grade_id, proficiency_id]):
            return Response({
                'msg': 'lesson_code, name, subject_id, grade_id, and proficiency_id are required fields.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify all foreign keys exist
            subject = Subject.objects.get(id=subject_id)
            grade = Grade.objects.get(id=grade_id)
            proficiency = Proficiency.objects.get(id=proficiency_id)
            
            # Check if lesson_code is unique
            if Lesson.objects.filter(lesson_code=lesson_code).exists():
                return Response({
                    'msg': 'lesson_code must be unique.'
                }, status=status.HTTP_400_BAD_REQUEST)

            lesson = Lesson.objects.create(
                lesson_code=lesson_code,
                name=name,
                subject=subject,
                grade=grade,
                proficiency=proficiency
            )
            
            return Response({
                'msg': 'Lesson created successfully',
                'data': {
                    'id': str(lesson.id),
                    'lesson_code': lesson.lesson_code,
                    'name': lesson.name,
                    'subject_id': str(lesson.subject.id),
                    'grade_id': str(lesson.grade.id),
                    'proficiency_id': str(lesson.proficiency.id),
                    'created_at': lesson.created_at,
                    'duration': lesson.duration,
                    'objective': lesson.objective,
                    'specific_learning_outcome': lesson.specific_learning_outcome,
                    'behavioral_outcome': lesson.behavioral_outcome,
                    'materials_required': lesson.materials_required,
                    'is_done': lesson.is_done,
                    'verified': lesson.verified,
                    'activate': lesson.activate,
                    'acquire': lesson.acquire,
                    'assess': lesson.assess,
                    'apply': lesson.apply
                }
            }, status=status.HTTP_201_CREATED)

        except (Subject.DoesNotExist, Grade.DoesNotExist, Proficiency.DoesNotExist) as e:
            return Response({
                'msg': f'{str(e.__class__.__name__)} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': f'Error creating lesson: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, lesson_id):
        """Update an existing lesson"""
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            
            # Update basic fields if provided
            if 'lesson_code' in request.data:
                if Lesson.objects.filter(lesson_code=request.data['lesson_code']).exclude(id=lesson_id).exists():
                    return Response({
                        'msg': 'lesson_code must be unique.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                lesson.lesson_code = request.data['lesson_code']
            
            if 'name' in request.data:
                lesson.name = request.data['name']
                
            if 'duration' in request.data:
                lesson.duration = request.data['duration']
                
            if 'objective' in request.data:
                lesson.objective = request.data['objective']
                
            if 'specific_learning_outcome' in request.data:
                lesson.specific_learning_outcome = request.data['specific_learning_outcome']
                
            if 'behavioral_outcome' in request.data:
                lesson.behavioral_outcome = request.data['behavioral_outcome']
                
            if 'materials_required' in request.data:
                lesson.materials_required = request.data['materials_required']
                
            # Handle verified status (admin only)
            if 'verified' in request.data:
                lesson.verified = request.data['verified']
                # If admin sets verified to True, automatically set is_done to True
                if request.data['verified']:
                    lesson.is_done = True
                
            # Update foreign keys if provided
            if 'subject_id' in request.data:
                try:
                    new_subject = Subject.objects.get(id=request.data['subject_id'])
                    lesson.subject = new_subject
                except Subject.DoesNotExist:
                    return Response({
                        'msg': 'New subject not found'
                    }, status=status.HTTP_404_NOT_FOUND)

            if 'grade_id' in request.data:
                try:
                    new_grade = Grade.objects.get(id=request.data['grade_id'])
                    lesson.grade = new_grade
                except Grade.DoesNotExist:
                    return Response({
                        'msg': 'New grade not found'
                    }, status=status.HTTP_404_NOT_FOUND)

            if 'proficiency_id' in request.data:
                try:
                    new_proficiency = Proficiency.objects.get(id=request.data['proficiency_id'])
                    lesson.proficiency = new_proficiency
                except Proficiency.DoesNotExist:
                    return Response({
                        'msg': 'New proficiency not found'
                    }, status=status.HTTP_404_NOT_FOUND)

            # Update JSON fields if provided
            if 'activate' in request.data:
                lesson.activate = json.dumps(request.data['activate'])
            if 'acquire' in request.data:
                lesson.acquire = json.dumps(request.data['acquire'])
            if 'assess' in request.data:
                lesson.assess = json.dumps(request.data['assess'])
            if 'apply' in request.data:
                lesson.apply = json.dumps(request.data['apply'])

            lesson.save()

            return Response({
                'msg': 'Lesson updated successfully',
                'data': {
                    'id': str(lesson.id),
                    'lesson_code': lesson.lesson_code,
                    'name': lesson.name,
                    'subject_id': str(lesson.subject.id),
                    'grade_id': str(lesson.grade.id),
                    'proficiency_id': str(lesson.proficiency.id),
                    'duration': lesson.duration,
                    'objective': lesson.objective,
                    'specific_learning_outcome': lesson.specific_learning_outcome,
                    'behavioral_outcome': lesson.behavioral_outcome,
                    'materials_required': lesson.materials_required,
                    'is_done': lesson.is_done,
                    'verified': lesson.verified,
                    'activate': lesson.activate,
                    'acquire': lesson.acquire,
                    'assess': lesson.assess,
                    'apply': lesson.apply
                }
            })

        except Lesson.DoesNotExist:
            return Response({
                'msg': 'Lesson not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': f'Error updating lesson: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, lesson_id):
        """Delete a lesson"""
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            lesson.delete()
            return Response({
                'msg': 'Lesson deleted successfully'
            }, status=status.HTTP_200_OK)
        except Lesson.DoesNotExist:
            return Response({
                'msg': 'Lesson not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': f'Error deleting lesson: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class UnverifiedCompletedLessonsView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def get(self, request):
        unverified_lessons = Lesson.objects.filter(
            is_done=True,
            verified=False
        ).select_related('completed_by', 'subject', 'grade', 'proficiency')

        data = [{
            'id': str(lesson.id),
            'lesson_code': lesson.lesson_code,
            'name': lesson.name,
            'subject': {
                'id': str(lesson.subject.id),
                'name': lesson.subject.name
            },
            'grade': {
                'id': str(lesson.grade.id),
                'name': lesson.grade.name
            },
            'proficiency': {
                'id': str(lesson.proficiency.id),
                'name': lesson.proficiency.name
            },
            'completed_by': {
                'id': str(lesson.completed_by.id),
                'email': lesson.completed_by.email,
                'name': lesson.completed_by.name
            } if lesson.completed_by else None
        } for lesson in unverified_lessons]

        return Response(data)