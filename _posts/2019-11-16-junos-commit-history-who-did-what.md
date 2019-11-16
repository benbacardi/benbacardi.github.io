---
layout: post
title: "Junos commit history: who did what?"
link: https://www.juniper.net/documentation/en_US/junos/topics/reference/command-summary/show-system-rollback.html
categories: Junos, Networking
---

Junos has always had one fantastic advantage over Cisco's IOS: the ability to stage a pending commit, and see a history of changes, rather than each command immediately being executed on the running config a soon as you hit Enter. 

The `show | compare rollback X` command has always been able to show you the difference between your current config and what the config was like _X_ commits ago. However, I've always found it difficult to figure out what exactly was done in a single commit (or batch of commits) if they weren't the most recent. That is, until I learnt of this command: `show system rollback compare X Y`! This lets you see the changes that were introduced just between the _X_ and _Y_ commits. 

Here's a real life example. Below is the commit history for a device at work. You can see there were a number of batches of commits going back in time where different individuals have done sole changes on the device:

```bash
ben@switch> show system commit
0   2019-11-13 15:06:51 GMT by katerina via cli
1   2019-11-13 14:49:19 GMT by katerina via cli
2   2019-11-13 14:43:01 GMT by katerina via cli
3   2019-11-13 14:42:11 GMT by katerina via cli
4   2019-11-13 14:41:01 GMT by katerina via cli
5   2019-11-13 14:03:53 GMT by katerina via cli
6   2019-11-13 12:28:33 GMT by katerina via cli
7   2019-11-13 12:25:44 GMT by katerina via cli
8   2019-11-13 12:24:53 GMT by katerina via cli
9   2019-11-13 12:23:28 GMT by katerina via cli
… output truncated … 
20  2019-09-13 14:16:43 BST by ben via cli
21  2019-09-13 14:15:27 BST by ben via cli
22  2019-09-13 14:13:48 BST by ben via cli
23  2019-09-13 14:13:06 BST by ben via cli
24  2019-09-13 14:08:43 BST by ben via cli
25  2019-09-13 14:08:13 BST by ben via cli
26  2019-09-13 14:06:50 BST by ben via cli
27  2019-09-13 14:06:12 BST by ben via cli
28  2019-08-07 14:21:33 BST by stuart via cli
29  2019-08-07 14:21:08 BST by stuart via cli
30  2019-08-07 14:18:43 BST by stuart via cli
31  2019-08-05 09:06:28 BST by stuart via cli
32  2019-06-19 13:04:54 BST by lewis via cli
33  2019-06-19 13:02:34 BST by lewis via cli
34  2019-06-19 13:01:31 BST by lewis via cli commit confirmed, rollback in 3mins
35  2019-06-19 12:59:30 BST by lewis via cli
36  2019-06-19 12:58:39 BST by lewis via cli
37  2019-06-19 12:58:03 BST by lewis via cli commit confirmed, rollback in 3mins
38  2019-06-07 13:58:39 BST by bart via cli
39  2019-06-07 13:07:17 BST by bart via cli commit confirmed, rollback in 1mins
40  2019-06-06 12:27:51 BST by bart via cli
41  2019-05-15 13:07:07 BST by chris via cli
42  2019-05-09 14:14:43 BST by chris via cli
```

I needed to find what Stuart and Lewis had each introduced in their batches of changes back in August and June, respectively. This new command makes that trivially easy. 

Stuart's batches of changes were in commits 28–31. Running the following command, I was able to easily extract just what those commits introduced:


```bash
ben@switch> show system rollback compare 32 28
[edit interfaces interface-range ir_stp_edge]
     member ge-0/0/10 { ... }
+    member ge-0/0/6;
+    member ge-0/0/7;
+    member ge-0/0/8;
… more changes …
```

Note that you need to put the higher (older) commit number first, followed by the lower (more recent). Additionally, you need to increase the higher commits number by one, as you want to know what was introduced between those commits, _including the oldest one_. 

Likewise, to see what Lewis introduced in his commits, we can run the following:

```bash
ben@switch> show system rollback compare 38 32
… some changes ...
```

This will definitely save me some time in future!
