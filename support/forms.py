from django import forms

class RAGFileUploadForm(forms.Form):
    file = forms.FileField(label="Select a file for RAG")
