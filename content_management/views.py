from django.shortcuts import render, get_object_or_404
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
from utils.notifications import notify_admins_lesson_completed
from django.utils import timezone
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

class CampusListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        campuses = Campus.objects.all()
        data = [{
            'id': str(campus.id),
            'campus_code': campus.campus_code,
            'name': campus.name,
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
                'campus_code': campus.campus_code,
                'name': campus.name,
                'description': campus.description,
                'grades': [{
                    'id': str(grade.id),
                    'name': grade.name,
                    'grade_code': grade.grade_code,
                } for grade in campus.grades.all()]
            }
            return Response(data)
        except Campus.DoesNotExist:
            return Response({'error': 'Campus not found'}, status=status.HTTP_404_NOT_FOUND)

class GradeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, grade_id):
        grade = get_object_or_404(Grade, id=grade_id)
        subjects = grade.subjects.all()
        data = {
            'id': str(grade.id),
            'name': grade.name,
            'grade_code': grade.grade_code,
            'subjects': [{
                'id': str(subject.id),
                'name': subject.name,
                'icon': subject.icon,
                'colorcode': subject.colorcode,
                'subject_code': subject.subject_code,
                'proficiencies': [{
                    'id': str(proficiency.id),
                    'name': proficiency.name,
                    'proficiency_code': proficiency.proficiency_code,
                    'lessons': [{
                        'id': str(lesson.id),
                        'lesson_code': lesson.lesson_code,
                        'name': lesson.name,
                        'is_done': lesson.is_done
                    } for lesson in proficiency.lessons.all()]
                } for proficiency in subject.proficiencies.all()]
            } for subject in subjects]
        }
        return Response(data)

class SubjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, subject_id):
        subject = get_object_or_404(Subject, id=subject_id)
        proficiencies = subject.proficiencies.all()
        data = {
            'id': str(subject.id),
            'name': subject.name,
            'icon': subject.icon,
            'colorcode': subject.colorcode,
            'proficiencies': [{
                'id': str(proficiency.id),
                'name': proficiency.name,
                'proficiency_code': proficiency.proficiency_code,
                'lessons': [{
                    'id': str(lesson.id),
                    'lesson_code': lesson.lesson_code,
                    'name': lesson.name,
                    'is_done': lesson.is_done,
                    'verified':lesson.verified,
                } for lesson in proficiency.lessons.all()]
            } for proficiency in proficiencies]
        }
        return Response(data)

class ProficiencyLessonsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, proficiency_id):
        proficiency = get_object_or_404(Proficiency, id=proficiency_id)
        lessons = proficiency.lessons.all()
        data = {
            'proficiency_id': str(proficiency.id),
            'proficiency_name': proficiency.name,
            'proficiency_code': proficiency.proficiency_code,
            'lessons': [{
                'id': str(lesson.id),
                'lesson_code': lesson.lesson_code,
                'name': lesson.name,
                'is_done': lesson.is_done,
                'verified':lesson.verified,
                'created_at':lesson.created_at
            } for lesson in lessons]
        }
        return Response(data)

class LessonDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        data = {
            'id': str(lesson.id),
            'lesson_code': lesson.lesson_code,
            'name': lesson.name,
            'subject': lesson.subject.name,
            'grade': lesson.grade.name,
            'proficiency': lesson.proficiency.name,
            'is_done': lesson.is_done,
            'verified': lesson.verified,
            'objective': lesson.objective,
            'duration': lesson.duration,
            'specific_learning_outcome': lesson.specific_learning_outcome,
            'behavioral_outcome': lesson.behavioral_outcome,
            'materials_required': lesson.materials_required,
            'resources': lesson.resources,
            'verified': lesson.verified,
            'activate': lesson.activate,
            'acquire': lesson.acquire,
            'apply': lesson.apply,
            'assess': lesson.assess,
            'created_at': lesson.created_at
        }
        return Response(data)

class MarkLessonDoneView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        lesson.is_done = True
        lesson.completed_by = request.user
        lesson.completed_at = timezone.now()
        lesson.save()
        
        # Send notification to admins
        notify_admins_lesson_completed(lesson, request.user)
        
        return Response({'message': 'Lesson marked as done'}, status=status.HTTP_200_OK)

class MarkLessonNotDoneView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        lesson.is_done = False
        lesson.save()
        return Response({'message': 'Lesson marked as not done'}, status=status.HTTP_200_OK)


class ParseCSVView(APIView):
    def get(self, request):
        created_lessons = []
        not_found_content = []
        error_details = []

        try:
            # Setup Google Sheets authentication
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                'belakoo-fdc48-de4dfbe50d3e.json', 
                scope
            )
            client = gspread.authorize(creds)

            # Open the spreadsheet
            sheet_url = 'https://docs.google.com/spreadsheets/d/1jUz-Q-zjXw9tnFhxiSGeueI0uUAlA6dazyougsKX7d4'
            spreadsheet = client.open_by_url(sheet_url)

            # Get all worksheets except 'Instr & Obj'
            worksheets = [sheet for sheet in spreadsheet.worksheets() if sheet.title != 'Instr & Obj']
            if not worksheets:
                return Response({"error": "No valid worksheets found"}, status=status.HTTP_404_NOT_FOUND)
            
            print(f"Found {len(worksheets)} worksheets to process")
            
            # Get campus
            campus = Campus.objects.get(campus_code='c1')
            print(f"Found campus: {campus.name}")

            # Process each worksheet
            for worksheet in worksheets:
                try:
                    print(f"\nProcessing worksheet: {worksheet.title}")
                    
                    # Convert to DataFrame
                    data = worksheet.get_all_values()
                    df = pd.DataFrame(data)
                    print(f"Created DataFrame for {worksheet.title}")

                    # Find LESSON CODE
                    lesson_code = None
                    for i, row in df.iterrows():
                        if 'LESSON CODE' in row.values:
                            col_index = row.tolist().index('LESSON CODE')
                            if col_index + 1 < len(row):
                                lesson_code = row[col_index + 1]
                                print(f"Found LESSON CODE: {lesson_code}")
                                break

                    if not lesson_code:
                        raise Exception("LESSON CODE not found")

                    # Split lesson code
                    code_parts = lesson_code.split('.')
                    if len(code_parts) != 4:
                        raise Exception("Invalid LESSON CODE format")

                    subject_code, grade_code, lesson_number, proficiency_code = code_parts
                    print(f"Parsed codes - Subject: {subject_code}, Grade: {grade_code}, Lesson: {lesson_number}, Proficiency: {proficiency_code}")

                    # Helper functions
                    def get_field_value(field_name):
                        for i, row in df.iterrows():
                            if field_name in row.values:
                                col_index = row.tolist().index(field_name)
                                if col_index + 1 < len(row):
                                    return row[col_index + 1]
                        return ''

                    def get_structured_field_value(field_name):
                        for i, row in df.iterrows():
                            if field_name in row.values:
                                col_index = row.tolist().index(field_name)
                                if col_index + 1 < len(row):
                                    return [{
                                        "title": field_name,
                                        "desc": row[col_index + 1]
                                    }]
                        return []

                    def get_resources_value(field_name):
                        for i, row in df.iterrows():
                            if field_name in row.values:
                                col_index = row.tolist().index(field_name)
                                if col_index + 2 < len(row):
                                    return row[col_index + 2]
                        return ''

                    # Process Grade
                    grade = Grade.objects.filter(grade_code=grade_code, campus=campus).first()
                    if not grade:
                        grade = Grade.objects.create(
                            grade_code=grade_code,
                            campus=campus,
                            name=grade_code
                        )
                        print(f"Created new grade: {grade.name}")
                    else:
                        print(f"Found existing grade: {grade.name}")

                    # Process Subject
                    subject = Subject.objects.filter(subject_code=subject_code, grade=grade).first()
                    if not subject:
                        subject = Subject.objects.create(
                            subject_code=subject_code,
                            grade=grade,
                            name="Mathematics",
                            icon='https://drive.google.com/file/d/1ALzD7lJHFbQfxzHQVGrX1qlbwE9_eLQx/view?usp=drive_link',
                            colorcode='#000000'
                        )
                        print(f"Created new subject: {subject.name}")
                    else:
                        print(f"Found existing subject: {subject.name}")

                    # Process Proficiency
                    proficiency = Proficiency.objects.filter(proficiency_code=proficiency_code, subject=subject).first()
                    if not proficiency:
                        proficiency = Proficiency.objects.create(
                            proficiency_code=proficiency_code,
                            subject=subject,
                            name=proficiency_code
                        )
                        print(f"Created new proficiency: {proficiency.name}")
                    else:
                        print(f"Found existing proficiency: {proficiency.name}")

                    # Create structured JSON fields
                    activate_data = []
                    for field in ['HOOK','ASSESS','INFORM']:
                        field_data = get_structured_field_value(field)
                        if field_data:
                            activate_data.extend(field_data)
                    
                    acquire_data = []
                    for field in ['ENGAGE', 'TEACH']:
                        field_data = get_structured_field_value(field)
                        if field_data:
                            acquire_data.extend(field_data)
                    
                    apply_data = []
                    for field in ['GUIDED PRACTICE', 'INDEPENDENT PRACTICE']:
                        field_data = get_structured_field_value(field)
                        if field_data:
                            apply_data.extend(field_data)
                    
                    assess_data = []
                    for field in ['ASSESSMENT', 'SHARE']:
                        field_data = get_structured_field_value(field)
                        if field_data:
                            assess_data.extend(field_data)

                    # Create Lesson
                    try:
                        lesson = Lesson.objects.create(
                            lesson_code=lesson_code,
                            name=f"Lesson {lesson_number}",
                            subject=subject,
                            grade=grade,
                            proficiency=proficiency,
                            objective=get_field_value('OBJECTIVE'),
                            duration=get_field_value('Duration'),
                            specific_learning_outcome=get_field_value('Specific Learning Outcome '),
                            behavioral_outcome=get_field_value('Behavioural Outcome'),
                            materials_required=get_field_value('Materials Required'),
                            activate=json.dumps(activate_data),
                            acquire=json.dumps(acquire_data),
                            apply=json.dumps(apply_data),
                            assess=json.dumps(assess_data),
                            resources=get_resources_value('RESOURCES')
                        )
                        print(f"Created lesson: {lesson.name} with structured JSON fields")
                        created_lessons.append({'sheet': worksheet.title, 'lesson_code': lesson.lesson_code})

                    except Exception as e:
                        error_details.append({
                            'sheet': worksheet.title,
                            'lesson_code': lesson_code,
                            'error': str(e)
                        })
                        print(f"Error creating lesson: {str(e)}")
                        continue

                except Exception as worksheet_error:
                    error_details.append({
                        'sheet': worksheet.title,
                        'error': str(worksheet_error)
                    })
                    print(f"Error processing worksheet {worksheet.title}: {str(worksheet_error)}")
                    continue

            response_data = {
                "message": "All sheets processed",
                "total_sheets": len(worksheets),
                "created_lessons": created_lessons,
                "not_found_content": not_found_content,
                "error_details": error_details
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetAllSheetsView(APIView):
    def get(self, request):
        # Define the scope
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

        # Load the credentials from the JSON file
        creds = ServiceAccountCredentials.from_json_keyfile_name('Belakoo_backend/belakoo-fdc48-de4dfbe50d3e.json', scope)
        client = gspread.authorize(creds)

        # Open the Google Sheet by URL
        sheet_url = 'https://docs.google.com/spreadsheets/d/1jUz-Q-zjXw9tnFhxiSGeueI0uUAlA6dazyougsKX7d4'
        spreadsheet = client.open_by_url(sheet_url)

        # Get all sheet names
        sheet_names = [sheet.title for sheet in spreadsheet.worksheets()]

        # Print all sheet names
        print("Sheets present in the Google Sheet:")
        for name in sheet_names:
            print(name)

        return Response({"sheets": sheet_names}, status=status.HTTP_200_OK)
