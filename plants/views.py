from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from .models import Plant, PlantPhoto
from .forms import PlantForm, PlantPhotoForm


class PlantListView(LoginRequiredMixin, ListView):
    model = Plant
    template_name = 'plants/list.html'
    context_object_name = 'plants'
    paginate_by = 9

    def get_queryset(self):
        qs = Plant.objects.filter(owner=self.request.user, is_active=True)

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(scientific_name__icontains=q) |
                Q(location__icontains=q) |
                Q(category__icontains=q)
            )

        status = self.request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)

        return qs


class PlantDetailView(LoginRequiredMixin, DetailView):
    model = Plant
    template_name = 'plants/detail.html'
    context_object_name = 'plant'

    def get_queryset(self):
        return Plant.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['schedules'] = self.object.schedules.filter(is_active=True)
        ctx['logs'] = self.object.care_logs.all()[:20]
        ctx['photos'] = self.object.photos.all()
        ctx['qr_codes'] = self.object.qr_codes.filter(status='active')
        return ctx


class PlantCreateView(LoginRequiredMixin, CreateView):
    model = Plant
    form_class = PlantForm
    template_name = 'plants/form.html'
    success_url = reverse_lazy('plants:list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['mode'] = 'create'
        return ctx

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class PlantUpdateView(LoginRequiredMixin, UpdateView):
    model = Plant
    form_class = PlantForm
    template_name = 'plants/form.html'

    def get_queryset(self):
        return Plant.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['mode'] = 'update'
        return ctx

    def get_success_url(self):
        return reverse_lazy('plants:detail', kwargs={'pk': self.object.pk})


class PlantDeleteView(LoginRequiredMixin, DeleteView):
    model = Plant
    template_name = 'plants/confirm_delete.html'
    success_url = reverse_lazy('plants:list')

    def get_queryset(self):
        return Plant.objects.filter(owner=self.request.user)








class PlantPhotoUploadView(LoginRequiredMixin, CreateView):
    model = PlantPhoto
    form_class = PlantPhotoForm
    template_name = 'plants/photo_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.plant = get_object_or_404(Plant, pk=kwargs['plant_pk'], owner=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['plant'] = self.plant
        return ctx

    def form_valid(self, form):
        form.instance.plant = self.plant
        messages.success(self.request, 'تصویر اضافه شد.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('plants:detail', kwargs={'pk': self.plant.pk}) + '#tab-photos'


class PlantPhotoDeleteView(LoginRequiredMixin, DeleteView):
    model = PlantPhoto

    def get_queryset(self):
        return PlantPhoto.objects.filter(plant__owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('plants:detail', kwargs={'pk': self.object.plant.pk}) + '#tab-photos'