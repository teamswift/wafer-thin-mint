from wafer_thin_mint import core


class Table(core.Model):
    id = core.PrimaryKey
    name = core.Charfield
    count = core.IntegerField
    spent = core.DecimalField


t = Table.objects.get(id=1)

# or

t = Table.objects.using('path.to.settings').get(name='bob')


class TableTwo(core.Model):
    table = core.ForiegnKey(Table)
    blurb = core.TextField


t2 = TableTwo.objects.get(table=t)

