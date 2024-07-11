from django.db import models

class Universitie(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return self.name
class Unit(models.Model):
    Unit_name = models.CharField(max_length=30)
    university_name= models.ForeignKey(Universitie, on_delete=models.CASCADE)
    def __str__(self):
        return self.Unit_name
class Room(models.Model):
    number = models.CharField(max_length=30)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    number_of_students = models.IntegerField(default=0,null=True)
    
    def __str__(self):
        return self.number
    
class UniversitySearchRequest(models.Model):
    university_name = models.CharField(max_length=100)





