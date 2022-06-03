from django.db import models


class GestureImage(models.Model):
    image = models.ImageField(upload_to="gestures")
    time = models.DecimalField(max_digits=3, decimal_places=1)

    def __str__(self):
        return "Image name: {} and time: {}".format(self.image.name, str(self.time))