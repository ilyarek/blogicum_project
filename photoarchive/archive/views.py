from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
import os
from .models import Document, SearchLog
from .forms import DocumentForm, SearchForm

def is_admin(user):
    return user.is_staff or user.is_superuser

def home(request):
    """Главная страница"""
    recent_documents = Document.objects.filter(is_active=True).order_by('-upload_date')[:8]
    return render(request, 'archive/home.html', {
        'recent_documents': recent_documents,
        'search_form': SearchForm()
    })

def search_documents(request):
    """Поиск документов"""
    form = SearchForm(request.GET or None)
    documents = Document.objects.filter(is_active=True)
    search_reasons = {}
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if query:
            keywords = [kw.strip().lower() for kw in query.split(',') if kw.strip()]
            keyword_queries = Q()
            for keyword in keywords:
                keyword_queries |= (
                    Q(title__icontains=keyword) |
                    Q(description__icontains=keyword) |
                    Q(keywords__icontains=keyword)
                )
            documents = documents.filter(keyword_queries)
            
            for doc in documents:
                reasons = []
                for keyword in keywords:
                    if keyword in doc.title.lower():
                        reasons.append(f"Совпадение в названии: '{keyword}'")
                    elif keyword in doc.description.lower():
                        reasons.append(f"Совпадение в описании: '{keyword}'")
                    elif keyword in doc.keywords.lower():
                        reasons.append(f"Совпадение в ключевых словах: '{keyword}'")
                search_reasons[doc.id] = reasons
        
        if date_from:
            documents = documents.filter(original_date__gte=date_from)
        if date_to:
            documents = documents.filter(original_date__lte=date_to)
        
        if request.GET:
            SearchLog.objects.create(
                query=query or '',
                date_from=date_from,
                date_to=date_to,
                results_count=documents.count()
            )
    
    paginator = Paginator(documents, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'archive/search_results.html', {
        'form': form,
        'page_obj': page_obj,
        'search_reasons': search_reasons,
        'documents_count': documents.count()
    })

def document_detail(request, pk):
    """Детальная страница документа"""
    document = get_object_or_404(Document, pk=pk, is_active=True)
    return render(request, 'archive/document_detail.html', {
        'document': document
    })

@login_required
def add_document(request):
    """Добавление нового документа"""
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save()
            return redirect('document_detail', pk=document.pk)
    else:
        form = DocumentForm()
    
    return render(request, 'archive/add_document.html', {
        'form': form
    })

@login_required
@user_passes_test(is_admin)
def download_document(request, pk):
    """Скачивание документа"""
    document = get_object_or_404(Document, pk=pk, is_active=True)
    
    if document.document_file:
        response = HttpResponse(document.document_file, content_type='application/octet-stream')
        filename = os.path.basename(document.document_file.name)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        return HttpResponse("Файл не найден", status=404)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Админ-панель для управления архивом"""
    documents = Document.objects.all().order_by('-upload_date')
    search_logs = SearchLog.objects.all()[:10]
    
    # Рассчитываем количество неактивных документов
    total_documents = Document.objects.count()
    active_documents = Document.objects.filter(is_active=True).count()
    inactive_documents = total_documents - active_documents 
    
    return render(request, 'archive/admin_dashboard.html', {
        'documents': documents,
        'search_logs': search_logs,
        'total_documents': total_documents,
        'active_documents': active_documents,
        'inactive_documents': inactive_documents,
    })

@login_required
@user_passes_test(is_admin)
def toggle_document_status(request, pk):
    """Активация/деактивация документа"""
    document = get_object_or_404(Document, pk=pk)
    document.is_active = not document.is_active
    document.save()
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def delete_document(request, pk):
    """Удаление документа"""
    document = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        # Удаляем файлы
        if document.document_file:
            document.document_file.delete(save=False)
        if document.thumbnail:
            document.thumbnail.delete(save=False)
        document.delete()
        return redirect('admin_dashboard')
    
    total_documents = Document.objects.count()
    active_documents = Document.objects.filter(is_active=True).count()
    
    return render(request, 'archive/confirm_delete.html', {
        'document': document,
        'total_documents': total_documents,
        'active_documents': active_documents,
    })