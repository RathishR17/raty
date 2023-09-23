from django.contrib import admin
from .models import Cart,Payment,Customer,Product,category,OrderPlaced


#class CategoryAdmin(admin.ModelAdmin):
    #list_display = ('name','image','description')

#admin.site.register(category, CategoryAdmin)




admin.site.register(category)
admin.site.register(Product)
admin.site.register(Payment)
admin.site.register(Customer)
admin.site.register(OrderPlaced)
admin.site.register(Cart)