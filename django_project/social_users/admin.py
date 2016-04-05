# -*- coding: utf-8 -*-
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib import admin
from .models import (
    Profile,
    TrustedUser,
    Organization
)


class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'profile_picture', 'screen_name')


admin.site.register(Profile, ProfileAdmin)


class OrganizationInline(admin.TabularInline):
    model = TrustedUser.organizations.through
    extra = 0  # how many rows to show


class TrustedUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'list_organizations')
    inlines = (OrganizationInline,)

    def list_organizations(self, obj):
        return ", ".join(['<span><a href="/admin/social_users/organization/%s">%s</a></span>' % (p.id, p.name) for p in
                          obj.organizations.all()])

    list_organizations.allow_tags = True


admin.site.register(TrustedUser, TrustedUserAdmin)


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'site', 'contact', 'list_trusted_user')

    def list_trusted_user(self, obj):
        return ", ".join(
            ['<span><a href="/admin/social_users/trusteduser/%s">%s</a></span>' % (p.user.id, p.user.username) for p in
             obj.trusted_users.all()])

    list_trusted_user.allow_tags = True


admin.site.register(Organization, OrganizationAdmin)

from social.apps.django_app.default.models import UserSocialAuth
from social_users.models import Profile, TrustedUser


class UserProfileInline(admin.TabularInline):
    model = Profile
    fk_name = 'user'
    can_delete = True
    max_num = 1
    extra = 0


class SocialAuthInline(admin.TabularInline):
    model = UserSocialAuth
    fk_name = 'user'
    can_delete = True
    extra = 0


class TrustedUserInline(admin.TabularInline):
    model = TrustedUser
    readonly_fields = ('is_trusted', 'list_organizations')
    fk_name = 'user'
    can_delete = False
    max_num = 1
    extra = 0

    def is_trusted(self, obj):
            return '<a href="/admin/social_users/trusteduser/%s"><img src="/static/admin/img/icon-yes.gif" alt="True"></a>' % obj.id

    def list_organizations(self, obj):
        return ", ".join(['<span><a href="/admin/social_users/organization/%s">%s</a></span>' % (p.id, p.name) for p in
                          obj.organizations.all()])

    is_trusted.allow_tags = True
    list_organizations.allow_tags = True


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'first_name', 'last_name',
                    'email', 'is_staff', 'provider', 'profile_picture', 'is_trusted')
    inlines = (UserProfileInline, SocialAuthInline, TrustedUserInline)

    def provider(self, obj):
        try:
            return ", ".join(
                ['<span><a href="/admin/default/usersocialauth/%s">%s</a></span>' % (p.id, p.provider) for p in
                 UserSocialAuth.objects.filter(user=obj)])
        except UserSocialAuth.DoesNotExist:
            return ""

    def profile_picture(self, obj):
        try:
            return ", ".join(
                ['<span><a href="%s">%s</a></span>' % (p.profile_picture, p.profile_picture) for p in
                 Profile.objects.filter(user=obj)])
        except UserSocialAuth.DoesNotExist:
            return ""

    def is_trusted(self, obj):
        try:
            detail = TrustedUser.objects.get(user=obj)
            return '<a href="/admin/social_users/trusteduser/%s"><img src="/static/admin/img/icon-yes.gif" alt="True"></a>' % detail.id
        except TrustedUser.DoesNotExist:
            return '<img src="/static/admin/img/icon-no.gif" alt="False">'

    provider.allow_tags = True
    profile_picture.allow_tags = True
    is_trusted.allow_tags = True


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
