from django.db import models

class JuliaTest(models.Model):
    date = models.TextField()
    word = models.TextField()
    phonetics = models.TextField()
    definition = models.TextField()
    example = models.TextField()
    increment = models.IntegerField()

    def __str__(self):
        return self.word