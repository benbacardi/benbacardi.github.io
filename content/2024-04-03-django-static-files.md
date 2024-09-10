title: Static Files in Django: An Introduction
category: Development
tags: Python, Django

Some of the most common recurring questions in the [Django Discord](https://www.djangoproject.com/community/) revolve around static files, why they're not loading when they should, or how to configure them and what should be responsible for serving them. I thought I'd write up a bit of an introduction to static files in Django, which will hopefully be a little more approachable to beginners than the official docs (as excellent as they are), and serve as a starting point for diagnosing problems with them.

## What are static files?

Static files are files served as part of your Django application whose contents do not change from user to user or request to request—they are not *dynamic*. By far the most common examples are the stylesheets (CSS), Javascript, and images that are required for the application to look and function correctly in the browser, but they could just as easily be other things—JSON files of data that doesn't change, for example. 

Static files are *not* any files that your users upload, such as profile pictures, or other content. Those are referred to by Django as *media* files, and are handled differently. 

## Static files terminology

There are three key pieces of information to know about Django's static files:

- the directories you store them in during development of the project,
- the URL they are served under when requested by the browser, and
- the directory (note: singular) they are collecting into as part of deploying the app.

These are three distinct, but interrelated, pieces of the puzzle, and they each have different settings to adjust or define their behaviour in `settings.py`.

## Where do I put my static files?

By default, Django will look for your static files in a directory named `static` inside each app directory in `INSTALLED_APPS`, and without any additional configuration this is the *only* place it will search. For many, that's enough.

Others may wish to store some static files outside any one particular app, because they may be relevant globally to the project and there isn't a single app that fits them best. This can be done by creating a new directory somewhere (often, named `static` at the same level as `manage.py`), and adding a new setting to `settings.py`:

```python
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
```

The `STATICFILES_DIRS` setting tells Django to look for static files in those additional directories, as well as within each individual app directory.

## What URL do I use to request my static files from the browser?

The single setting, `STATIC_URL`, defines the URL prefix that Django expects the static files to be available under when the browser requests them. This is entirely independent from their actual location on the file system as discussed above.

Django suggests a perfectly reasonable default for this: `"static/"`. It must end in a slash.

When running your application, Django will expect the static files to be available under that URL. For example, a file in a directory `my_app/static/css/styles.css` would correspond to a URL of `/static/css/styles.css`.

When referencing static files in templates, such as using a `link` or `script` tag to include CSS or JavaScript in HTML, Django provides a template tag in the `static` library to automatically convert a relative static file name into its full URL path. For example, to include the above CSS file:

```django
{% load static %}
…
<link href="{% static "css/main.css" %}" rel="stylesheet">
```

This would result in the following HTML output:

```html
<link href="/static/css/main.css" rel="stylesheet">
```

## So, how does Django map the URL to the actual file on the file system?

And what's this third key point I mentioned above, the single static directory?

The answer to this differs depending on how you're running Django; in development or production. 

### Serving static files in development

During development, it's acceptable for Django to serve the static files itself. Normally, this job would be handed off to a web server or proxy, as there is no benefit to spinning up the full Django application process just to chuck some static CSS back to the browser, but during development it is really not worth having to set that all up. 

When running Django with the development server (`manage.py runserver`) and `DEBUG=True`, Django will automatically add a new URL path to your URL patterns that matches the value of `STATIC_URL`, and search the various directories mentioned above for matching files to serve whenever a request comes in. This means that by only setting a `STATIC_URL` to something sensible, Django will automatically be able to serve the CSS, JavaScript, and images stored in any `static` folder inside each `INSTALLED_APPS` directory, and any folders pointed to by `STATICFILES_DIRS`. That's usually enough for development purposes. 

### Serving static files in a production environment

However, as mentioned above, it's inefficient to have Django serve these files itself when deployed in a production environment. Instead, that responsibility is usually handed off to a web server or proxy that sits in front of Django, such as nginx. So how does this proxy know where to find the static files?

The answer is in the `STATIC_ROOT` setting. This should be pointed to a directory on the file system that, once deployed, both the Django application and the proxy can access. 

What should be in that directory? Nothing, to start with. Part of the deployment process should be to run `manage.py collectstatic`, a built-in management command which runs round all the various folders the static files live in (see the first point above) and copies them into the `STATIC_ROOT` directory, ready for the proxy to efficiently serve them.

The final part of the puzzle is to correctly configure the proxy so that requests for any path matching the prefix defined in `STATIC_URL` map onto the folder defined in `STATIC_ROOT`. This way, once `collectstatic` has been run, all the discrete parts of the application point together at a single, efficiently-served directory of static files.

## Troubleshooting missing static files

Follow these steps to help diagnose why styles may not be loading, images not showing up, or any other static files not appearing correctly in the browser.

1. Ensure the file is in either a directory named `static` under one of your `INSTALLED_APPS`, or in a directory pointed at by `STATICFILES_DIRS`.
2. Make sure `STATIC_URL` is configured and ends in a `/`.
3. Ensure you are using the `{% static "relative/path/to/file" %}` template tag wherever you reference static files in your templates. 
4. If you are developing and using `runserver`, make sure `DEBUG=True`. Restart the `runserver` to be sure it picks up any changes you may have made. 
5. If the app is deployed, make sure your `STATIC_ROOT` points to a directory on the file system, you have run `collectstatic`, and whatever proxy that fronts Django is properly configured to point `STATIC_URL` at the `STATIC_ROOT` directory. 

Note also that browsers will cache static files, so a forced refresh can help debug. This is usually done with `Ctrl-F5`, but varies from browser to browser. 

## Further reading

Hopefully this should provide a basic introduction to static files in Django, with enough information to get you up and running and help diagnose when static files aren't working as you expect. For further reading, I suggest looking at the following resources:

- Django's documentation on:
    - [Managing static files](https://docs.djangoproject.com/en/5.0/howto/static-files/)
    - [Static files settings.](https://docs.djangoproject.com/en/5.0/ref/settings/#static-files) Take note of the additional options we didn't discuss here, such as `STATICFILES_FINDERS`. 
    - [The `staticfiles` app.](https://docs.djangoproject.com/en/5.0/ref/contrib/staticfiles/#module-django.contrib.staticfiles). If this app is not included in `INSTALLED_APPS`, none of the above will work.
    - [Deploying static files]([https://docs.djangoproject.com/en/5.0/howto/static-files/deployment/](https://docs.djangoproject.com/en/5.0/howto/static-files/deployment/#staticfiles-from-cdn)), including how to deploy to a CDN rather than a local directory. 
- Libraries such as [Whitenoise](https://whitenoise.readthedocs.io/en/stable/index.html) for situations where configuring a proxy in front of Django isn't possible. 
