from .models import JPKFile, JPKTable, JPKTag


def prepare_tags_scheme(ns):
    """process data stored in JPKFile, JPKTable, JPKTag tables
    in order to get them accessible from JPKFile instance"""
    obj = None
    for jpk_file in JPKFile.objects.all():
        if jpk_file.ns == ns:
            obj = jpk_file

    obj.tags = {}
    obj.date_fields = []
    obj.money_fields = []
    obj.quantity_fields = []

    for table in obj.tables.all():
        obj.tags[table.name] = [tag.name for tag in table.tags.all()]
        obj.date_fields = [tag.name for tag in table.tags.filter(type="date")]
        obj.money_fields = [tag.name for tag in table.tags.filter(type="value")]
        obj.quantity_fields = [tag.name for tag in table.tags.filter(type="num")]
    return obj

