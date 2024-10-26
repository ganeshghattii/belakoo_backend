from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Campus, Subject, Grade, Proficiency, Lesson
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
import pandas as pd
import math
import os
import glob

class CampusListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        campuses = Campus.objects.all()
        data = [{
            'id': str(campus.id),
            'name': campus.name,
            'icon': campus.icon,
            'description': campus.description,
        } for campus in campuses]
        return Response(data)

class CampusDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, campus_id):
        try:
            campus = Campus.objects.get(id=campus_id)
            data = {
                'id': str(campus.id),
                'name': campus.name,
                'icon': campus.icon,
                'description': campus.description,
                'subjects': [{
                    'id': str(subject.id),
                    'name': subject.name,
                    'icon': subject.icon,
                    'colorcode':subject.colorcode
                } for subject in campus.subjects.all()]
            }
            return Response(data)
        except Campus.DoesNotExist:
            return Response({'error': 'Campus not found'}, status=status.HTTP_404_NOT_FOUND)

class SubjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, subject_id):
        try:
            subject = Subject.objects.get(id=subject_id)
            data = {
                'id': str(subject.id),
                'name': subject.name,
                'icon': subject.icon,
                'colorcode':subject.colorcode,
                'grades': [{
                    'id': str(grade.id),
                    'name': grade.name,
                } for grade in subject.grades.all()]
            }
            return Response(data)
        except Subject.DoesNotExist:
            return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)

class GradeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, grade_id):
        try:
            grade = Grade.objects.get(id=grade_id)
            data = {
                'id': str(grade.id),
                'name': grade.name,
                'proficiencies': [{
                    'id': str(proficiency.id),
                    'name': proficiency.name,
                    'lessons': [{
                        'id': str(lesson.id),
                        'name': lesson.name,
                        'lesson_code': lesson.lesson_code,
                        'is_done': lesson.is_done
                    } for lesson in proficiency.lessons.all()]
                } for proficiency in grade.proficiencies.all()]
            }
            return Response(data)
        except Grade.DoesNotExist:
            return Response({'error': 'Grade not found'}, status=status.HTTP_404_NOT_FOUND)

class ProficiencyLessonsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, proficiency_id):
        try:
            proficiency = Proficiency.objects.get(id=proficiency_id)
            lessons = proficiency.lessons.all()
            data = {
                'proficiency_id': str(proficiency.id),
                'proficiency_name': proficiency.name,
                'lessons': [{
                    'id': str(lesson.id),
                    'lesson_code': lesson.lesson_code,
                    'name': lesson.name,
                    'is_done': lesson.is_done
                } for lesson in lessons]
            }
            return Response(data)
        except Proficiency.DoesNotExist:
            return Response({'error': 'Proficiency not found'}, status=status.HTTP_404_NOT_FOUND)

class LessonDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, lesson_code):
        try:
            lesson = Lesson.objects.get(lesson_code=lesson_code)
            data = {
                'id': str(lesson.id),
                'lesson_code': lesson.lesson_code,
                'name': lesson.name,
                'subject': lesson.subject.name,
                'grade': lesson.grade.name,
                'proficiency': lesson.proficiency.name,
                'is_done': lesson.is_done,
                'objective': lesson.objective,
                'duration': lesson.duration,
                'specific_learning_outcome': lesson.specific_learning_outcome,
                'behavioural_outcome': lesson.behavioural_outcome,
                'materials_required': lesson.materials_required,
                'activate': lesson.activate,
                'acquire': lesson.acquire,
                'apply': lesson.apply,
                'assess': lesson.assess,
            }
            return Response(data)
        except Lesson.DoesNotExist:
            return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

class MarkLessonDoneView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_code):
        try:
            lesson = Lesson.objects.get(lesson_code=lesson_code)
            lesson.is_done = True
            lesson.save()
            return Response({'message': 'Lesson marked as done'}, status=status.HTTP_200_OK)
        except Lesson.DoesNotExist:
            return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

class MarkLessonNotDoneView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_code):
        try:
            lesson = Lesson.objects.get(lesson_code=lesson_code)
            lesson.is_done = False
            lesson.save()
            return Response({'message': 'Lesson marked as not done'}, status=status.HTTP_200_OK)
        except Lesson.DoesNotExist:
            return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

class ParseCSVView(APIView):
    def get(self, request):
        created_lessons = []
        not_found_content = []
        error_details = []

        try:
            import os
            import glob
            import pandas as pd
            
            # Path to the content directory
            content_dir = 'Belakoo_backend/content/'
            # Get all CSV files in the directory
            csv_files = glob.glob(os.path.join(content_dir, '*.csv'))

            # Assuming campus with code 'c1' exists
            campus = Campus.objects.get(campus_code='c1')

            for file_path in csv_files:
                print(f"Processing file: {file_path}")
                df = pd.read_csv(file_path)

                # Function to find a keyword and its value
                def find_keyword_value(keyword):
                    for i, row in df.iterrows():
                        if keyword in row.values:
                            col_index = row.tolist().index(keyword)
                            if col_index + 1 < len(row):
                                return row[col_index + 1]
                    return None

                # List of keywords to search for
                keywords = [
                    'LESSON CODE', 'OBJECTIVE', 'Duration',
                    'Specific Learning Outcome', 'Behavioural Outcome',
                    'Materials Required', 'HOOK', 'ASSESS', 'INFORM', 'ENGAGE', 'TEACH', 'GUIDED PRACTICE', 'INDEPENDENT PRACTICE', 'SHARE', 'ASSESSMENT'
                ]

                # Extract values for each keyword
                lesson_data = {}
                for keyword in keywords:
                    value = find_keyword_value(keyword)
                    if value is not None:
                        lesson_data[keyword] = value
                    else:
                        not_found_content.append(keyword)

                # Parse the LESSON CODE
                extracted_code = lesson_data.get('LESSON CODE', '').split('.')
                if len(extracted_code) != 4:
                    print(f"Invalid LESSON CODE format: {lesson_data.get('LESSON CODE')}")
                    continue  # Skip this entry if the format is invalid

                subject_code = extracted_code[0]  # First part is subject
                grade_code = extracted_code[1]     # Second part is grade
                lesson_number = extracted_code[2]  # Third part is lesson
                proficiency_code = extracted_code[3]  # Fourth part is proficiency

                # Get or create the Subject
                subject_name = find_keyword_value('SUBJECT')  # Assuming 'SUBJECT' is a keyword in the CSV
                subject, created = Subject.objects.get_or_create(
                    subject_code=subject_code,
                    defaults={'name': subject_name, 'campus': campus}
                )
                print(f"{'Created' if created else 'Found'} subject: {subject.name}")

                # Get or create the Grade
                grade, created = Grade.objects.get_or_create(
                    grade_code=grade_code,
                    defaults={'name': grade_code, 'subject': subject}
                )
                print(f"{'Created' if created else 'Found'} grade: {grade.name}")

                # Create a new Proficiency for this specific Grade
                proficiency, created = Proficiency.objects.get_or_create(
                    proficiency_code=proficiency_code,
                    grade=grade,  # Link proficiency to the specific grade
                    defaults={'name': proficiency_code}
                )
                print(f"{'Created' if created else 'Found'} proficiency: {proficiency.name}")

                # Create and save the Lesson object
                try:
                    lesson = Lesson.objects.create(
                        lesson_code=lesson_data['LESSON CODE'],
                        name=f"Lesson {lesson_number}",
                        subject=subject,
                        grade=grade,
                        proficiency=proficiency,
                        objective=lesson_data.get('OBJECTIVE', ''),
                        duration=lesson_data.get('Duration', ''),
                        specific_learning_outcome=lesson_data.get('Specific Learning Outcome', ''),
                        behavioural_outcome=lesson_data.get('Behavioural Outcome', ''),
                        materials_required=lesson_data.get('Materials Required', ''),
                        activate={"HOOK": lesson_data.get('HOOK', '')},
                        acquire={"INFORM": lesson_data.get('INFORM', ''), "ENGAGE": lesson_data.get('ENGAGE', ''), "TEACH": lesson_data.get('TEACH', '')},
                        apply={"GUIDED PRACTICE": lesson_data.get('GUIDED PRACTICE', ''), "INDEPENDENT PRACTICE": lesson_data.get('INDEPENDENT PRACTICE', ''), "SHARE": lesson_data.get('SHARE', '')},
                        assess={"ASSESSMENT": lesson_data.get('ASSESS', '')}
                    )
                    created_lessons.append(lesson.lesson_code)
                    print(f"Lesson created: {lesson.name}")

                except Exception as e:
                    error_details.append({
                        'lesson_code': lesson_data.get('LESSON CODE'),
                        'error': str(e)
                    })
                    print(f"Error creating lesson: {str(e)}")

            # Prepare the response
            response_data = {
                "message": "Lessons processed successfully",
                "created_lessons": created_lessons,
                "not_found_content": not_found_content,
                "error_details": error_details
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return Response({"error": str(e)}, status=500)
