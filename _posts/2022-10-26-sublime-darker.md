---
layout: post
title: "Darker Sublime Text Plugin"
categories: Python Development
---

[Black](https://github.com/psf/black) is a popular code formatter for Python code, known for is opinionated uncompromising stance. It's incredibly helpful for teams working on common Python code to write in the same style, and Black makes that easy, without having to maintain a common set of configuration options between the team members. After all, there aren't any.

However, adding it to an existing codebase is difficult. It wants to reformat every source file, which can be a pain with version history by creating commits that are purely formatting changes, or adding misleading diffs to commits that are intended for something else. To help overcome this, [Darker](https://github.com/akaihola/darker) was created, which runs Black but only on the parts of code that have changed since the last commit. This is perfect for running as a post-save hook in your IDE, to consistently keep your code up to style without altering the parts of the source you haven't changed.

The Darker documentation includes instructions on how to integrate the formatter with PyCharm, IntelliJ IDEA, Visual Studio Code, Vim, and Emacs—but I use Sublime Text. All it took was to write a simple Sublime Plugin, however, and we're off to the races:

```python
import sublime_plugin
import os
import subprocess


class DarkerOnSave(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        filename = view.file_name()
        if view.match_selector(0, "source.python"):
            subprocess.call(["darker", filename], cwd=os.path.dirname(filename))
```

To add this yourself, go to **Tools > Developer > New Plugin…** from the menubar, and replace the contents of the file with the above. Save the file as something like `darker-on-save.py` in the same location it was created in (the default in the save dialog box), and now every time you hit Save on a Python file, it'll ensure that every time you save, the code you added or altered is up to scratch with your style guide. Simple!