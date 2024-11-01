from django.db import models

class BaseRepo:
    def __init__(self, model: models.Model):
        self.model = model

    def get_all(self):
        return self.model.objects.all()

    def get_by_id(self, id):
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None

    def create(self, **data):
        return self.model.objects.create(**data)

    def delete_obj(self, id):
        to_delete = self.get_by_id(id)
        if to_delete:
            return to_delete.delete()
        return None
