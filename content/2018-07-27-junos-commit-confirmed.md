title: Junos: Confirm a commit cleanly"
link: https://www.google.com
category: Networking
tags: Junos

For years, I have loved the fact that Junos allows you to perform a `commit confirmed` to apply the configuration with an automatic rollback in a certain number of minutes.

I have always believed that the only way to confirm the commit (i.e. stop the automatic rollback) was to `commit` again. This creates two commits in the commit history, one containing the actual config diff, and an empty one purely used to stop the rollback. I've always thought that this creates a somewhat messy commit history, and confuses the use of `show | compare rollback`:

{% highlight bash %}
[edit]
ben@device> run show system commit
0   2018-07-27 08:44:26 BST by ben via cli
1   2018-07-27 08:44:07 BST by ben via cli commit confirmed, rollback in 5mins
2   2018-07-23 10:04:29 BST by ben via cli
3   2018-07-23 10:03:58 BST by ben via cli commit confirmed, rollback in 2mins

[edit]
ben@device> show | compare rollback 1

[edit]
ben@device> # Huh, it's empty?! I'm sure I did some work...

[edit]
ben@device> show | compare rollback 2
[edit system]
-   host-name old-device
+   host-name device

[edit]
ben@device> # Oh, there it is...
{% endhighlight %}

However, today I learnt that a `commit check` is enough to stop the rollback, and doesn't create an empty commit! My commit histories are now much cleaner, and `show | compare rollback` commands a lot easier to work out what you're actually looking at.

{% highlight bash %}
[edit]
ben@device> run show system commit
1   2018-07-27 08:44:07 BST by ben via cli commit confirmed, rollback in 5mins
3   2018-07-23 10:03:58 BST by ben via cli commit confirmed, rollback in 2mins

[edit]
ben@device> show | compare rollback 1
[edit system]
-   host-name old-device
+   host-name device
{% endhighlight %}

Much better!
