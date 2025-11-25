from django.contrib import admin
from .models import (
    Character,
    Item,
    Inventory,
    Skill,
    Quest,
    NPC,
    Guild,
    Battle,
    Transaction
)

admin.site.register(Character)
admin.site.register(Item)
admin.site.register(Inventory)
admin.site.register(Skill)
admin.site.register(Quest)
admin.site.register(NPC)
admin.site.register(Guild)
admin.site.register(Battle)
admin.site.register(Transaction)
