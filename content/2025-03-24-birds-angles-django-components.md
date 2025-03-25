title: Birds and Angles: Dabbling in Django Components
category: Development
tags: Python, Django

The [Django template language](https://docs.djangoproject.com/en/5.2/ref/templates/language/) is great. It's been one of the core pillars of Django's popularity since the beginning—a simple, easy-to-use templating language that tries to give you just enough power to do what you need without having to think too hard.

However, there are more modern ways of thinking about template rendering that the DTL lacks: notably, support for components—splitting templates into smaller reusable chunks, that can each take their own contexts and render just what they need to. There's always been the [`include`](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#include) tag, but it's rather limited.

A number of third-party libraries have sprung up, such as [django-bird](https://django-bird.readthedocs.io/), [django-cotton](https://django-cotton.com/), and [django-components](https://django-components.github.io/django-components/latest/), to name just a few. Until now, I've never used any of them, and made do with the `include` tag wherever I needed to reuse a snippet of a template—however, I decided to take a look and see what all the fuss was about on a small project at work.

The design of a page I was building called for some repeated boxes displaying a couple of pieces of data for different time periods, shown below:

![Statistics boxes](/assets/request-stats.png)

While this could relatively easily be done with an `include`, this seemed like the perfect opportunity to try one of the component libraries. I chose `django-bird`, as the way it functions seems to gel best with the way my brain thinks about components. I ended up with the following component:

```django
{# templates/bird/request-stats-summary-button.html #}
{% load humanize %}

{% bird:prop period %}
{% bird:prop this_period %}
{% bird:prop active_users=999 %}
{% bird:prop totals=999 %}

<div
  class="card card-hover me-sm-3 rounded border {% if props.period == props.this_period %}bg-primary text-light{% else %}card-hover-bg-primary{% endif %}"
>
  <div class="card-body pb-2 pt-2 shadow-sm">
    <h6 class="card-title {% if props.period != props.this_period %}text-muted{% endif %} text-uppercase fw-normal">
      {{ slot }}
    </h6>
    <p class="mb-0 d-flex align-items-center">
      <i class="fas fa-user {% if props.period == props.this_period %}text-light{% else %}text-primary{% endif %} fs-5"></i>
      <span class="fs-3 ms-1">{{ props.active_users|intcomma }}</span>
      <i class="fas fa-mouse-pointer ms-3 {% if props.period == props.this_period %}text-light{% else %}text-primary{% endif %} fs-5"></i>
      <span class="fs-3 ms-1">{{ props.totals|intcomma }}</span>
    </p>
  </div>
</div>
```

You'll notice the use of four "props" to pass data through, as well as the `{{ slot }}` variable to capture the contents of the component. I updated the main template to use the component:

```django
{% bird request_stats_summary_button period=period this_period="today" active_users=active_users.today totals=totals.today %}
  Today
{% endbird %}
{% bird request_stats_summary_button period=period this_period="this_week" active_users=active_users.week totals=totals.week %}
  This Week
{% endbird %}
{% bird request_stats_summary_button period=period this_period="this_month" active_users=active_users.month totals=totals.month %}
  This Month
{% endbird %}
{% bird request_stats_summary_button period=period this_period="this_year" active_users=active_users.year totals=totals.year %}
  This Year
{% endbird %}
```

And it worked great!

I originally picked `django-bird` because I liked how it used standard DTL tags, and didn't require any custom template parsers. However, in actual use, I don't like that I can't wrap DTL tags to multiple lines, which ends up with the `bird` lines quickly becoming unwieldy. There's a [forum post](https://forum.djangoproject.com/t/allow-newlines-inside-tags/36040/29) and [ticket](https://code.djangoproject.com/ticket/35899) about supporting new lines in DTL tags, but that won't happen any time soon.

This is where another new-to-me package comes in—[`dj-angles`](https://dj-angles.adamghill.com/en/stable/)! The main purpose of this package is to provide a web-component-style template tag interface to the built-in DTL template tags, as demonstrated quite neatly in their docs. This is done by adding a new template loader that parses the alternative syntax. However, what's of interest to me is that they also provide native integration with `django-bird`, allowing us to use the more compact (and new-line-compatible!) style tags with bird components.

A couple of settings later, and we can reference the above components in a way that really seems to click for me:

```html
<dj-request-stats-summary-button
  period=period
  this_period="today"
  active_users=active_users.today
  totals=totals.today
>
  Today
</dj-request-stats-summary-button>
<dj-request-stats-summary-button
  period=period
  this_period="this_week"
  active_users=active_users.week
  totals=totals.week
>
  This Week
</dj-request-stats-summary-button>
<dj-request-stats-summary-button
  period=period
  this_period="this_month"
  active_users=active_users.month
  totals=totals.month
>
  This Month
</dj-request-stats-summary-button>
<dj-request-stats-summary-button
  period=period
  this_period="this_year"
  active_users=active_users.year
  totals=totals.year
>
  This Year
</dj-request-stats-summary-button>
```

It's more verbose in number of lines, but much more readable!

Yes, I'm aware that this is the sort of thing that `django-cotton` and other template libraries provide automatically, but I've come to quite like `django-bird`. Perhaps I'll swap to one of the others one day, but for now, I'm enjoying what the combination of birds and angles can give me.

---

There's only one main issue I have with `django-bird`, and that's how it doesn't parse DTL filters in values passed as properties or attributes. For example, the following component reference:

```django
{% bird button badge_count=users|length %}Users{% endbird %}
```

will result in the `badge_count` prop inside the `button` component being set to the string `"users|length"`, which is not the desired result at all. I have an [open issue](https://github.com/joshuadavidthomas/django-bird/issues/181) and [associated draft PR](https://github.com/joshuadavidthomas/django-bird/pull/229) on the repo, so hopefully we'll be able to get the feature into the library before too long.





