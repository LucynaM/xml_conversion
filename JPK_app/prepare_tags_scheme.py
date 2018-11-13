from .models import JPKFile, JPKTable, JPKTag


def prepare_tags_scheme(ns):
    """process data stored in JPKFile, JPKTable, JPKTag tables
    in order to get them accessible from JPKFile instance"""
    obj = None
    for jpk_file in JPKFile.objects.all():
        if jpk_file.ns == ns:
            obj = jpk_file

    # represent file content as dictionary where key is a table name and values are tags names
    obj.tags = {}
    # select all tags that should contain dates
    obj.date_fields = []
    # select all tags that should contain money value
    obj.money_fields = []
    # select all tags that should contain numbers
    obj.quantity_fields = []

    for table in obj.tables.all():
        obj.tags[table.name] = [tag.name for tag in table.tags.all()]
        [obj.date_fields.append(tag.name) for tag in table.tags.filter(type="date")]
        [obj.money_fields.append(tag.name) for tag in table.tags.filter(type="value")]
        [obj.quantity_fields.append(tag.name) for tag in table.tags.filter(type="num")]
    return obj

