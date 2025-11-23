from django.db import models
from django.contrib.auth.models import User

class EquipmentDataset(models.Model):
    """Model to store uploaded equipment datasets"""
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    filename = models.CharField(max_length=255)
    csv_data = models.TextField()  
    upload_date = models.DateTimeField(auto_now_add=True)
    
   
    total_count = models.IntegerField()
    avg_flowrate = models.FloatField()
    avg_pressure = models.FloatField()
    avg_temperature = models.FloatField()
    
    def __str__(self):
        return f"{self.filename} - {self.upload_date}"
    
    class Meta:
        ordering = ['-upload_date']
