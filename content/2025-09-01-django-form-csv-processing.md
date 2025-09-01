title: Django Forms and CSV Processing
category: Development
tags: Python, Django

Recently, I've found myself building a number of tools that accept input data in the form of a CSV from the user, and parse and validate it before executing whatever processing is necessary for the given tool. Django's forms provide an easy way to accept file uploads, and model forms make it trivial to store those files on disk alongside a model instance.

What I was struggling with was where to do the validation of the contents of the CSV. Forms provide some level of validation, and give the user feedback via field- or form-level errors, but in order to provide *useful* feedback via this mechanism the form needs to parse the CSV to validate each of its rows. This is easily doable in the field-specific clean method, such as the following, which validates that every row has an `identifier` field and a `date` field, with the date in the future (using [`arrow`](https://arrow.readthedocs.io/en/latest/) for date parsing):

```python
import csv
import arrow
from django import forms
from django.db import models
from django.utils import timezone

class CSVUpload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    csv_file = models.FileField(upload_to="csv_uploads")

class CSVUploadForm(forms.ModelForm):
    class Meta:
        model = CSVUpload
        fields = ["csv_file"]
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]
        try:
            for row in csv.DictReader(csv_file):
                if not row.get("identifier", "").strip():
                    raise ValueError("Missing identifier")
                if arrow.get("date") <= timezone.now():
                    raise ValueError("Date not in the future")
        except ValueError as err:
            raise forms.ValidationError(f"Could not read CSV file; please ensure it is in the correct format ({err})")
        return csv_file
```

This works fine—the form won't pass the `is_valid()` check unless the data within the CSV is valid. So what's the problem?

Well, there's a reason we're reading the CSV and validating the data—we want to *do* something with the data. The form has parsed it, but it's thrown away any results of that parsing, leaving the view to have to do it all over again, which is less than ideal. We can't simply return the parsed data from the `clean` method, because that would break Django's `FileField` handling within the model form. Instead, we can take advantage of the fact that a `Form` instance is just that—a standard Python object, nothing special—and set an attribute on the instance with the parsed data:

```python hl_lines="8 11 12 13 14 19 22 23"
class CSVUploadForm(forms.ModelForm):
    class Meta:
        model = CSVUpload
        fields = ["csv_file"]
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]
        parsed_data = []
        try:
            for row in csv.DictReader(csv_file):
                row_data = {
                    "identifier": row.get("identifier", "").strip(),
                    "date": arrow.get("date"),
                }
                if not row_data["identifier"]:
                    raise ValueError("Missing identifier")
                if row_data["date"] <= timezone.now():
                    raise ValueError("Date not in the future")
                parsed_data.append(row_data)
        except ValueError as err:
            raise forms.ValidationError(f"Could not read CSV file; please ensure it is in the correct format ({err})")
        else:
            self.parsed_data = parsed_data
        return csv_file
```

Now, within the view, we can let Django handle the model form as it should, and read the form's `parsed_data` attribute to use the data from within the CSV as necessary:

```python
class CSVUploadView(FormView):
    form_class = CSVUploadForm
    
    def is_valid(self, form):
        instance = form.save()
        for data in form.parsed_data:
            # Use the data from the CSV, already parsed
            pass
        return HttpResponseRedirect(self.get_success_url())
```

Simple!
