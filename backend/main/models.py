from django.db import models


class DataFormat(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    xstate_json = models.JSONField()
    generated_parser = models.TextField()
    journal = models.TextField()
    # latest_version = models.ForeignKey("DataFormat", models.CASCADE)
    build_uuid = models.UUIDField()
    check_uuid = models.UUIDField()
