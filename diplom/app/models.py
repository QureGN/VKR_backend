from django.db import models

class Folders(models.Model):
    name_folder = models.CharField(max_length=30, verbose_name="Название_папки")

    class Meta:
        managed = True
        db_table = 'folders'
        verbose_name = "Папка"
        verbose_name_plural = "Папки"


class Trees_json(models.Model):
    folder_pk = models.ForeignKey(Folders, models.CASCADE, blank=True, null=True)
    name_tree = models.CharField(max_length=30, verbose_name="Название")
    breed = models.CharField(max_length=50, verbose_name="Порода")
    age = models.IntegerField(verbose_name="Возраст")
    diameter = models.IntegerField(verbose_name="Диаметр")
    height = models.IntegerField(verbose_name="Высота")
    coordinate_X = models.IntegerField(verbose_name="Координата_X")
    coordinate_Y = models.IntegerField(verbose_name="Координата_Y")

    class Meta:
        managed = True
        db_table = 'trees_json'
        verbose_name = "Дерево"
        verbose_name_plural = "Деревья"
