from dpasteapp.models import *
from django import forms
from django.views.generic import *
from django.shortcuts import *
import hashlib
import datetime
from django.db.models import *
from django.utils import timezone
import jsbeautifier

class DpasteForm(forms.ModelForm):
    class Meta:
        model = DjangoPastebin
        exclude = ['id','identification','link','created']
        widgets = {
            'content':forms.Textarea(attrs={'class':'form-control'}),
            'language': forms.Select(choices=LANGUAGE_CHOICES),
            'image':forms.FileInput(attrs={'class': 'form-control'}),
            'video': forms.FileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'user': forms.TextInput(attrs={'class': 'form-control'}),
            'expiry': forms.Select(choices=EXPIRY_CHOICES),
        }


class DpasteController(CreateView):
    model = DjangoPastebin
    form_class = DpasteForm
    template_name = 'dpasteform.html'

    def post(self, request, *args, **kwargs):
        form = DpasteForm(request.POST,request.FILES)

        if form.is_valid():
            data = form.save(commit=False)
            data.created = datetime.datetime.now()
            data.identification = 0
            data.save()
            data.link = hashlib.shake_128(str(data.id).encode()).hexdigest(5)
            resp = redirect( '/' + data.link)
            if 'value' in request.COOKIES:
                data.identification = int(request.COOKIES.get('value'))

            else:
                try:
                    value = DjangoPastebin.objects.aggregate(Max("identification"))
                    resp.set_cookie('value', value["identification__max"]+1)
                    data.identification = value["identification__max"]+1
                except Exception as e:
                    resp.set_cookie('value', 1)
                    data.identification = 1

            data.save()
            return resp

        return redirect('dpasteapp:dpaste_form')

def check_link(date,expiry):
    if (date + datetime.timedelta(days=expiry)) < timezone.now():
        return True
    else:
        return False

class DpasteView(View):
    def get(self, request, link):
        try:
            data = DjangoPastebin.objects.get(link=link)
        except ObjectDoesNotExist:
            return render(
                request,
                template_name='error.html'
            )
        if check_link(data.created, data.expiry):
            return render(
                request,
                template_name='error.html'
            )

        expiry_in = data.created + datetime.timedelta(days=data.expiry) - timezone.now()
        expiry_str = ""
        if expiry_in.days > 0:
            expiry_str += str(expiry_in.days) + "Days, "
        if (expiry_in.seconds // (3600)) % 24 > 0:
            expiry_str += str((expiry_in.seconds // (3600)) % 24) + "Hours, "
        if (expiry_in.seconds // 60) % (60) > 0:
            expiry_str += str((expiry_in.seconds // (60)) % 60) + "Minutes"
        elif expiry_in.seconds > 0:
            expiry_str += str(expiry_in.seconds) + "Seconds"

        opts = jsbeautifier.default_options()
        opts.indent_size = 4
        res = jsbeautifier.beautify(data.content, opts)

        return render(
            request,
            'dpasteview.html',
            context={
                'data': res,
                'img':data.image,
                'video': data.video,
                'expiry': expiry_str,
                'form': DpasteForm,
            }
        )

class DpasteListView(ListView):
    model = DjangoPastebin
    template_name = 'dpaste_list.html'
    context_object_name = 'list'

    def get_queryset(self):
        print("value")
        if 'value' in self.request.COOKIES:
            value = int(self.request.COOKIES.get('value'))
            list = DjangoPastebin.objects.filter(identification = value).order_by('-created') if value >= 1 else []
            for s in list:
                if check_link(s.created, s.expiry):
                    s.link = None
            return list
        return []

    def get_context_data(self,**kwargs):
        context = super(DpasteListView,self).get_context_data(**kwargs)
        return context

def aboutDpaste(request):
    return render(request, "about.html")