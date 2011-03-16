import copy

from django.contrib import admin
from django.contrib.admin import helpers
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from chef.rsa import SSLError

from commis.api.models import Client

class ClientAdmin(admin.ModelAdmin):
    fieldsets = [
        [None, {
            'fields': ('name', 'admin')
        }],
        ['Client Key', {
            'classes': ('collapse',),
            'fields': ('public_key',)
        }],
    ]
    readonly_fields = ('public_key', 'private_key')
    list_display = ('name', 'admin')

    def private_key(self, obj):
        try:
            return '<pre style="clear:left;">%s</pre>'%obj.key.private_export()
        except SSLError:
            return ''
    private_key.short_description = _('Private Key')
    private_key.allow_tags = True

    def public_key(self, obj):
        return '<pre style="clear:left;">%s</pre>'%obj.key_pem
    public_key.short_description = _('Public Key')
    public_key.allow_tags = True

    def get_fieldsets(self, request, obj=None, private_key=False):
        fieldsets = super(ClientAdmin, self).get_fieldsets(request, obj)
        add = obj is None or obj.pk is None
        if private_key or add:
            fieldsets = copy.deepcopy(fieldsets)
        if private_key:
            fieldsets[1][1] = {'fields': ('public_key', 'private_key')}
        elif add:
            del fieldsets[1]
        return fieldsets

    def save_model(self, request, obj, form, change):
        super(ClientAdmin, self).save_model(request, obj, form, change)
        if not change:
            obj.generate_key()

    def response_add(self, request, obj, post_url_continue='../%s/'):
        """
        Determines the HttpResponse for the add_view stage.
        """
        opts = obj._meta

        msg = _('The %(name)s "%(obj)s" was added successfully. Please copy the private key now as it will not be stored on the server.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
        self.message_user(request, msg)

        ModelForm = self.get_form(request, obj)
        formsets = []
        form = ModelForm(instance=obj)
        prefixes = {}
        for FormSet, inline in zip(self.get_formsets(request, obj), self.inline_instances):
            prefix = FormSet.get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1:
                prefix = "%s-%s" % (prefix, prefixes[prefix])
            formset = FormSet(instance=obj, prefix=prefix,
                              queryset=inline.queryset(request))
            formsets.append(formset)

        adminForm = helpers.AdminForm(form, self.get_fieldsets(request, obj, private_key=True),
            self.prepopulated_fields, self.get_readonly_fields(request, obj),
            model_admin=self)
        media = self.media + adminForm.media

        inline_admin_formsets = []
        for inline, formset in zip(self.inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                fieldsets, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
            media = media + inline_admin_formset.media

        context = {
            'title': _('Change %s') % force_unicode(opts.verbose_name),
            'adminform': adminForm,
            'object_id': obj._get_pk_val(),
            'original': obj,
            'is_popup': "_popup" in request.REQUEST,
            'media': mark_safe(media),
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
        }
        return self.render_change_form(request, context, change=True, obj=obj, form_url='../%s/'%obj._get_pk_val())


admin.site.register(Client, ClientAdmin)
