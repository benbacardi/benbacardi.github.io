title: Pendulum 1.15 Released
category: Development
tags: Swift, SwiftUI, Apps
image: /assets/pendulum-1-15.png

After quite some time without any updates, I have finally released a new version of [Pendulum](/pendulum)—version 1.15 is now available in the App Store!

![Pendulum 1.15](/assets/pendulum-1-15.png)

With the release of iOS 26 and it's new Liquid Glass design language, I wanted to update Pendulum to feel more at home on the OS, and took the opportunity to change the design somewhat more drastically—at least for the main Pen Pals list. The biggest structural change was to drop the tab bar—it makes little sense when there are only two tabs—and move Settings to a top bar button. This meant I could take advantage of the new navigation transition available in iOS 26 to [morph between the button and the presented sheet](https://nilcoalescing.com/blog/PresentingLiquidGlassSheetsInSwiftUI/) in a very pleasing manner.

Visually, the Pen Pal list has had a huge overhaul, with the standout change being the map in the background. This will centre itself on the location you most recently sent a letter to or received one from, and I love the way it turned out. I hope it'll be fun for Pendulum's users to see it pan around the world as they send and receiving their correspondence. A further update may pull the map out into its own feature, with pins for your pen pals' locations in a more interactive manner.

Given the design now focuses rather heavily on your pen pals' addresses, it was about time I addressed (pun intended) the inability for you to store an address against a pen pal if you've disabled syncing with Contacts. It's a fairly commonly-requested feature, and this was the impetus I needed to finally get it done. Both types of Pen Pals can live happily together in Pendulum—those synced with a device contact will require you to use Contacts to update their address, and those added manually can be edited directly within the app.

![Storing addresses locally in Pendulum 1.15](/assets/pendulum-1-15-addresses.png)

The final feature in this release can be seen in the screenshot above, in Amelia's contact details page, Pendulum will pull in any nicknames you have against your linked Contacts, with an option to prefer nicknames over full names in most of Pendulum's UI. Amelia will be shown as Millie in the Pen Pal list and her correspondence screen, for example.

---

It's been fun to have the motivation and impetus to work on Pendulum again, and I'm excited to keep adding features and iterating as I go.
