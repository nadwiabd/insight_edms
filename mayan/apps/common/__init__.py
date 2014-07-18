from __future__ import absolute_import

import tempfile

from django.contrib.auth import models as auth_models
from django.contrib.auth.management import create_superuser
from django.contrib.auth.models import User
from django.db import transaction, DatabaseError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from south.signals import post_migrate

from navigation.api import register_links, register_top_menu

from .conf import settings as common_settings
from .conf.settings import (AUTO_ADMIN_USERNAME, AUTO_ADMIN_PASSWORD,
                            AUTO_CREATE_ADMIN, TEMPORARY_DIRECTORY)
from .links import (link_about, link_current_user_details,
                    link_current_user_edit, link_license,
                    link_password_change)
from .models import AutoAdminSingleton
from .utils import validate_path

register_links(['current_user_details', 'current_user_edit', 'password_change_view'], [link_current_user_details, link_current_user_edit, link_password_change], menu_name='secondary_menu')
register_links(['about_view', 'license_view', 'form_view'], [link_about, link_license], menu_name='secondary_menu')

register_top_menu('about', link={'text': _(u'about'), 'view': 'about_view', 'famfam': 'information'}, position=-1)


@receiver(post_migrate, dispatch_uid='create_superuser')
def create_superuser(sender, **kwargs):
    """
    From https://github.com/lambdalisue/django-qwert/blob/master/qwert/autoscript/__init__.py
    From http://stackoverflow.com/questions/1466827/ --

    Prevent interactive question about wanting a superuser created. (This code
    has to go in this otherwise empty "models" module so that it gets processed by
    the "syncdb" command during database creation.)

    Create our own admin super user automatically.
    """

    if AUTO_CREATE_ADMIN and kwargs['app'] == 'common':
        try:
            auth_models.User.objects.get(username=AUTO_ADMIN_USERNAME)
        except auth_models.User.DoesNotExist:
            print '*' * 80
            print 'Creating super admin user -- login: %s, password: %s' % (AUTO_ADMIN_USERNAME, AUTO_ADMIN_PASSWORD)
            print '*' * 80
            assert auth_models.User.objects.create_superuser(AUTO_ADMIN_USERNAME, 'autoadmin@autoadmin.com', AUTO_ADMIN_PASSWORD)
            admin = auth_models.User.objects.get(username=AUTO_ADMIN_USERNAME)
            # Store the auto admin password properties to display the first login message
            auto_admin_properties, created = AutoAdminSingleton.objects.get_or_create()
            auto_admin_properties.account = admin
            auto_admin_properties.password = AUTO_ADMIN_PASSWORD
            auto_admin_properties.password_hash = admin.password
            auto_admin_properties.save()
        else:
            print 'Super admin user already exists. -- login: %s' % AUTO_ADMIN_USERNAME


@receiver(post_save, dispatch_uid='auto_admin_account_passwd_change', sender=User)
def auto_admin_account_passwd_change(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            auto_admin_properties, created = AutoAdminSingleton.objects.get_or_create()
            if instance == auto_admin_properties.account and instance.password != auto_admin_properties.password_hash:
                # Only delete the auto admin properties when the password has been changed
                auto_admin_properties.delete(force=True)
    except DatabaseError:
        pass


if (not validate_path(TEMPORARY_DIRECTORY)) or (not TEMPORARY_DIRECTORY):
    setattr(common_settings, 'TEMPORARY_DIRECTORY', tempfile.mkdtemp())
