from django.template.defaultfilters import slugify

STATUS_CHOICES = {
    'Draft': 0,
    'Pending': 1,
    'Published': 2
}

ROLE_CHOICES = {
    'Administrator': 0,
    'Editor': 1,
    'Author': 2,
    'Contributor': 3,
    'Follower': 4
}


def has_enough_privileges(actual_level, required_group):
    return actual_level <= ROLE_CHOICES[required_group]


# Only used to set publication_date
def has_changed(instance, field):
    if not instance.pk:
        return False
    old_value = instance.__class__._default_manager.filter(
        pk=instance.pk).values(field).get()[field]
    return not getattr(instance, field) == old_value


# Should be improved
def unique_slug(string, target_class):
    slug = slugify(string)
    slug_exists = True
    counter = 1
    output = slug
    while slug_exists:
        try:
            slug_exits = target_class.objects.get(slug=slug)
            if slug_exits:
                slug = output + '_' + str(counter)
                counter += 1
        except target_class.DoesNotExist:
            output = slug
            break
    return output
