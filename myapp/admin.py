from django.contrib import admin
from .models import Brands
from .models import Buckets
from .models import Companies
from .models import Picturetypes
from .models import Paths
from .models import Pictures
from .models import Picturetables
from .models import Tags
from .models import Users

admin.site.register(Brands)
admin.site.register(Buckets)
admin.site.register(Companies)
admin.site.register(Picturetypes)
admin.site.register(Paths)
admin.site.register(Pictures)
admin.site.register(Picturetables)
admin.site.register(Tags)
admin.site.register(Users)

