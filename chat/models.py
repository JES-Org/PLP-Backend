
# #user app models

# from django.db import models
# class User(AbstractBaseUser, PermissionsMixin):

#     email = models.EmailField(unique=True)
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.email} ({self.role})"

# class ProfileBase(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     dob = models.DateField(null=True, blank=True)
#     phone = models.CharField(max_length=20)
#     join_date = models.DateField(auto_now_add=True)
#     image = models.ImageField(upload_to="avatars/", null=True, blank=True)
#     is_verified = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


# class Teacher(ProfileBase):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
#     department = models.CharField(max_length=100)
   

# class Student(ProfileBase):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
#     student_id = models.CharField(max_length=50, unique=True)
#     batch = models.ForeignKey(
#         'classrooms.Batch',
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='students'
#     )
  



# class Otp(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     code = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)



# #class room modles


# class Department(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
#     updated_at = models.DateTimeField(auto_now=True)



#     def __str__(self):
#         return self.name

# class Batch(models.Model):
#     section = models.CharField(max_length=10)
#     year = models.PositiveIntegerField()
#     department = models.ForeignKey(Department, on_delete=models.CASCADE)

    
# class Classroom(models.Model):
#     name = models.CharField(max_length=255)
#     courseNo = models.CharField(max_length=50)
#     description = models.TextField()
#     teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='created_classrooms')
#     batches = models.ManyToManyField(Batch, related_name='classrooms', blank=True)
#     is_archived = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


# class Announcement(models.Model):
#     title = models.CharField(max_length=255)
#     content = models.TextField()
#     class_room = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='announcements')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

# class Attachment(models.Model):
#     announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='attachments')
#     file = models.FileField(upload_to='announcements/')
#     created_at = models.DateTimeField(auto_now_add=True ,blank=True, null=True)
#     updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
  
# # assessment models



# class Assessment(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     tag = models.CharField(max_length=100)
#     classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='assessments')
#     is_published = models.BooleanField(default=False)
#     deadline = models.DateTimeField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

 

# class Question(models.Model):
#     QUESTION_TYPES = [
#         ('multiple_choice', 'Multiple Choice'),
#         ('short_answer', 'Short Answer'),
#     ]

#     text = models.TextField()
#     weight = models.FloatField(default=1.0)
#     assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
#     question_type = models.CharField(
#         max_length=20,
#         choices=QUESTION_TYPES,
#         default='multiple_choice'
#     )
#     model_answer = models.TextField(blank=True, null=True)
#     tags = models.JSONField(default=list, blank=True)  # List of strings
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

 

# class Answer(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
#     text = models.CharField(max_length=255)
#     is_correct = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

  

# class Submission(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
#     assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='submissions')
#     answers = models.JSONField()
#     score = models.FloatField(default=0)
#     graded_details = models.JSONField(null=True, blank=True, default=dict)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

  



# #forum

# class ForumMessage(models.Model):
#     classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='forum_messages')
#     sender = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     updatedAt = models.DateTimeField(auto_now=True)


# # learnign path


# class LearningPath(models.Model):
#     student = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=200)
#     content = models.TextField()
#     deadline= models.DateTimeField(null=True, blank=True)
#     isCompleted = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

# class ChatHistory(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     message = models.TextField()
#     is_ai_response = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

    

#     #notification


#     class Notification(models.Model):
#     recipients = models.ManyToManyField(User, related_name="notifications")
#     sender = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='sent_notifications')
#     message = models.TextField()
#     url = models.URLField(blank=True, null=True)
#     is_read_by = models.ManyToManyField(User, related_name="read_notifications", blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)


