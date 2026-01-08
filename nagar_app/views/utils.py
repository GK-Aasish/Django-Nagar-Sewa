def user_is_admin(user):
    return user.is_superuser or user.groups.filter(name="Admin").exists()
