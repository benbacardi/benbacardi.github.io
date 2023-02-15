title: Relay FM for St. Jude
category: Development
tags: Swift, Apps
image: /assets/IMG_0929.PNG
permalink: /swift/apps/development/2022/10/02/relay-fm-for-st-jude/

September is over, and that means the end of another [Childhood Cancer Awareness Month](https://www.cclg.org.uk/ccam). For the last four years, the [Relay FM](https://www.relay.fm/) community has used the opportunity to raise money for [St. Jude Children's Research Hospital](https://www.stjude.org/about-st-jude.html?sc_icid=us-mm-missionstatement#mission), an institution dedicated to understanding, treating, and discovering new ways to defeat childhood cancer. Last year, they raised over $700,000. This year, they're set to match that amount again, taking the total raised in the last four years to over $2 million.

For Stephen, one of the founders of Relay FM, the cause is particularly important. You can read more about his story and why they fundraise over on [512pixels.net](https://512pixels.net/2022/08/relay-st-jude-2022/).

When the campaign started last year, I had been a part of the [Relay FM members Discord](https://relay.fm/membership) for a few months. People were sharing the fundraising total in the Discord in various ways, and a few enterprising individuals came up with a variety of ways to get that total into a iOS Home Screen widget, such as [this Scriptable solution by Zach Knox](https://zmknox.com/2021/08/21/building-a-donation-tracker-widget.html). At the time, I was just starting to play with iOS app development and I thought "we can do better than this. Let's make a native app and widget!"

A group of us had already gotten together and built a Discord bot for the server, so I had the perfect [group of developers](https://tildy.dev) to solicit for help. Together, we built a small app that pulled the campaign information from the Tiltify public API (reverse engineered from [their website](https://tiltify.com/@relay-fm/relay-fm-for-st-jude-2022), rather than the official APIs), displayed it in the app, and provided a widget. It could also pull in the campaign's milestones. We distributed it via TestFlight, so we didn't have to deal with full-on App Review, and it was a great success (amongst Relay FM members, at least).

It was a brilliant learning experience for me, and greatly increased my knowledge of how a iOS app is built, albeit a very simple one. I am very grateful to all the people who took the time to explain things to me, and review and comment on my code to help me become a better Swift developer.

This year, we dusted off the app and plugged in the new campaign details a few days before September started, in order to get it up and running again. However, the campaign organisers threw us a last-minute curveball—there wasn't going to be just one campaign this year, but many! Relay would still have their main one, but anybody could set up "subfundraisers", all of which would add towards the overall total. So how was the app going to handle that?

We spent some time reverse engineering the Tiltify API for the new campaign format, and reworked the app from a simple "here's a widget" to a more full-featured discovery app, showcasing not only the overall total but also each individual fundraiser and their own goals and rewards. We extended the widgets to allow you to choose which fundraiser it should show, provided a variety of appearance options, and added a share screen to let users post pictures of the fundraiser progress on social media.

![Relay FM for St. Jude iOS App Screenshots](/assets/IMG_0929.PNG)

And of course, we threw in Lock Screen widgets and donation charts for those who'd braved the iOS 16 beta, or regular people upgrading when it was released publicly half way through the month.

Throughout the project I've learned more about Swift, SwiftUI, and iOS app development than I ever would have working on my own with no real goal in mind. I've learned how to handle the various iPhone and iPad screen sizes, store data locally with GRDB, and use custom intents to provide widgets of all sizes with dynamic options.

It's been a lot of fun to have a project to work on that's reached so many people (despite never leaving TestFlight!) and helped towards raising the absolutely phenomenal amount that the Relay FM community achieved for St. Jude this year. The app is [open source](https://github.com/Lovely-Development-Team/St-Jude-Widget-App), and we will hopefully be resurrecting it next September when the community comes together once more in the fight against childhood cancer.
