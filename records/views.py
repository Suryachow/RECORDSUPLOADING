import pandas as pd
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import StudentRecord
from .forms import StudentForm
from django.utils.dateparse import parse_datetime


# ---------------- HOME ----------------
def upload_home(request):
    return render(request, 'records/upload_home.html')


# ---------------- LIST ----------------
import csv
from django.db.models import Q
from django.http import HttpResponse

# ---------------- LIST ----------------
def record_list(request):
    records = StudentRecord.objects.all().order_by('-id')

    # --- SEARCH ---
    query = request.GET.get('q')
    if query:
        query = query.strip()
        # search_terms = query.split() # Split by spaces to handle "First Last"
        # However, to be safe against single complex strings, let's just use the query first, 
        # but the request is likely "search bar not working" because of exact phrase matching failing on split fields.
        
        # Better approach: Filter for EACH term (AND logic for terms, OR logic for fields)
        # This finds "John Doe" in a record where First="John", Last="Doe"
        # It also finds "Python Delhi" where Course="Python", City="Delhi"
        
        search_terms = query.split()
        for term in search_terms:
            records = records.filter(
                Q(first_name__icontains=term) |
                Q(last_name__icontains=term) |
                Q(email__icontains=term) |
                Q(mobile__icontains=term) |
                Q(course__icontains=term) |
                Q(student_city__icontains=term) |
                Q(parent_institute__icontains=term)
            )

    # --- FILTER (Exact Match) ---
    course_filter = request.GET.get('course')
    if course_filter:
        records = records.filter(course=course_filter)

    # --- EXPORT ---
    export_fmt = request.GET.get('export')
    if export_fmt in ['csv', 'excel']:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="students.{export_fmt}"'
        
        writer = csv.writer(response)
        # Write Header
        writer.writerow([
            'ID', 'First Name', 'Last Name', 'Course', 'Email', 'Mobile', 
            'State', 'City', 'Response Type', 'Response Date'
        ])
        
        for r in records:
            writer.writerow([
                r.id, r.first_name, r.last_name, r.course, r.email, r.mobile,
                r.student_state, r.student_city, r.response_type, r.response_date
            ])
            
        return response

    return render(request, 'records/record_list.html', {
        'records': records,
        'search_query': query,
    })


# ---------------- CREATE / UPDATE ----------------
def record_form(request, pk=None):
    instance = StudentRecord.objects.get(pk=pk) if pk else None
    form = StudentForm(request.POST or None, instance=instance)

    if form.is_valid():
        form.save()
        return redirect('record_list')

    return render(request, 'records/record_form.html', {'form': form})


# ---------------- DELETE ----------------
def record_delete(request, pk):
    record = get_object_or_404(StudentRecord, pk=pk)
    record.delete()
    return redirect('record_list')


# ---- INLINE EDIT (AJAX) ----
@require_http_methods(["POST"])
def inline_edit(request, pk, field):
    """Update a specific field via AJAX"""
    try:
        record = get_object_or_404(StudentRecord, pk=pk)
        value = request.POST.get('value', '')
        
        # Allowed fields for editing
        allowed_fields = [
            'first_name', 'last_name', 'course', 'email', 'mobile',
            'student_state', 'student_city', 'current_locality', 'city',
            'locality', 'parent_institute', 'response_type', 'isd_code',
            'is_in_ndn_list', 'exams_taken', 'student_work_experience',
            'response_to_course', 'response_to_course_program', 'response_date'
        ]
        
        if field not in allowed_fields:
            return JsonResponse({'success': False, 'error': 'Field not allowed'}, status=400)
        
        # Update the field
        setattr(record, field, value)
        record.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{field} updated successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ---------------- BULK UPLOAD ----------------
def bulk_upload(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if not file:
             return render(request, 'records/upload_bulk.html', {'error': 'No file uploaded'})

        ext = file.name.split('.')[-1].lower()

        try:
            # Read file with specific options to treat all columns as text initially to interpret them safely
            # or rely on pandas inference and clean up later.
            if ext in ['xlsx', 'xls']:
                # dtype=str prevents pandas from auto-converting '00123' to 123
                df = pd.read_excel(file, dtype=str)
            elif ext == 'csv':
                df = pd.read_csv(file, dtype=str)
            elif ext == 'json':
                df = pd.DataFrame(json.loads(file.read().decode('utf-8')))
            else:
                return render(request, 'records/upload_bulk.html', {
                    'error': 'Unsupported file format'
                })
        except Exception as e:
            return render(request, 'records/upload_bulk.html', {
                'error': f'Error reading file: {str(e)}'
            })
        
        # Replace NaN with empty string
        df = df.fillna('')

        # --- Enhanced Column Mapping ---
        # Normalize a string: remove special chars, lowercase
        def normalize_key(k):
             return ''.join(c for c in str(k).lower() if c.isalnum())

        # Map normalized keys to model fields
        # Define specific manual overrides first
        base_mapping = {
            'firstname': 'first_name',
            'lastname': 'last_name',
            'fname': 'first_name',
            'lname': 'last_name',
            'coursename': 'course',
            'parentinstitute': 'parent_institute',
            'institutename': 'parent_institute',
            'responsetocourse': 'response_to_course',
            'responsetype': 'response_type',
            'currentlocality': 'current_locality',
            'responsedate': 'response_date',
            'emailaddress': 'email',
            'phonenumber': 'mobile',
            'mobilenumber': 'mobile',
            'phone': 'mobile',
            'state': 'student_state',
            'isd': 'isd_code',
            'countrycode': 'isd_code',
            'isinndnlist': 'is_in_ndn_list',
            'ndn': 'is_in_ndn_list',
            'examstaken': 'exams_taken',
            'workexperience': 'student_work_experience',
            'experience': 'student_work_experience',
            
            # Specific fixes for user's file
            'courseparentinstitute': 'parent_institute',
            'isinndnclist': 'is_in_ndn_list',
            'isindndlist': 'is_in_ndn_list',
            'totalresponsestocourseparentinstitute': 'total_responses_course_parent',
            'totalresponsestocourseprogram': 'total_responses_course_program',
            'totalresponsestocourse': 'total_responses_course',
        }

        # Add model fields themselves to the mapping
        model_fields = [f.name for f in StudentRecord._meta.get_fields()]
        target_field_map = {}
        
        # Populate target map with standard fields
        for f in model_fields:
            target_field_map[normalize_key(f)] = f
        
        # Overlay manual overrides
        for k, v in base_mapping.items():
            target_field_map[normalize_key(k)] = v

        # Identify columns
        df_columns = {}
        unmapped_columns = []
        
        for col in df.columns:
            files_col_norm = normalize_key(col)
            if files_col_norm in target_field_map:
                df_columns[col] = target_field_map[files_col_norm]
            else:
                unmapped_columns.append(col)

        # Build records
        success_count = 0
        error_count = 0
        error_details = []
        
        cleaned_records = []

        for idx, (_, row) in enumerate(df.iterrows()):
            try:
                create_data = {}
                
                for df_col, model_field in df_columns.items():
                    raw_val = row.get(df_col, '')
                    final_val = ''

                    # --- Data Cleaning ---
                    
                    # 1. Date Fields
                    if model_field == 'response_date':
                        if raw_val:
                            try:
                                # Use pandas which handles most formats (ISO, DD-MM-YYYY, etc)
                                # dayfirst=True handles generic DD/MM/YY common in Excel
                                dt_val = pd.to_datetime(raw_val, dayfirst=True, errors='coerce')
                                if not pd.isna(dt_val):
                                    final_val = dt_val
                                else:
                                    final_val = None 
                            except:
                                final_val = None
                        else:
                            final_val = None

                    # 2. String Fields (General)
                    else:
                        # Convert to string
                        s_val = str(raw_val).strip()
                        
                        # Handle "Float strings" e.g. "9876543210.0" -> "9876543210"
                        if s_val.endswith('.0'):
                            s_val = s_val[:-2]
                        
                        final_val = s_val

                    create_data[model_field] = final_val
                
                # Default "Unknown" for required fields to prevent crash, but only if fully missing
                if not create_data.get('first_name'): create_data['first_name'] = 'Unknown'
                # last_name is optional in some contexts but let's keep it safe
                # course is required
                
                StudentRecord.objects.create(**create_data)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                error_details.append({
                    'row': idx + 2,
                    'message': str(e)
                })

        return render(request, 'records/upload_result.html', {
            'total': len(df),
            'success': success_count,
            'errors': error_count,
            'unmapped_columns': unmapped_columns,
            'error_details': error_details[:50]
        })

    return render(request, 'records/upload_bulk.html')
