from django.db import models


class StudentRecord(models.Model):
    # Basic Info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    # Course / Institute Info
    # Course / Institute Info
    course = models.CharField(max_length=200, blank=True, default='')
    parent_institute = models.CharField(max_length=200, blank=True, default='')

    response_to_course = models.CharField(max_length=200, blank=True, default='')

    # Location Info
    city = models.CharField(max_length=100, blank=True, default='')
    locality = models.CharField(max_length=100, blank=True, default='')
    student_state = models.CharField(max_length=100, blank=True, default='')
    student_city = models.CharField(max_length=100, blank=True, default='')
    current_locality = models.CharField(max_length=100, blank=True, default='')

    # Response Info
    response_date = models.DateTimeField(null=True, blank=True)
    response_type = models.CharField(max_length=100, blank=True, default='')

    # Contact Info
    email = models.EmailField(blank=True, default='')
    isd_code = models.CharField(max_length=10, blank=True, default='')
    mobile = models.CharField(max_length=15, blank=True, default='')
    is_in_ndn_list = models.CharField(max_length=10, blank=True, default='')

    # Academic / Experience
    exams_taken = models.CharField(max_length=100, blank=True, default='')
    student_work_experience = models.CharField(max_length=100, blank=True, default='')
    response_to_course_program = models.CharField(max_length=200, blank=True, default='')

    # Analytics / Counts
    total_responses_course_parent = models.CharField(max_length=50, blank=True, default='0')
    total_responses_course_program = models.CharField(max_length=50, blank=True, default='0')
    total_responses_course = models.CharField(max_length=50, blank=True, default='0')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
