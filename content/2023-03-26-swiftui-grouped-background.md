title: Matching the List background colour in SwiftUI
category: Development
tags: Swift, SwiftUI
image: /assets/swiftui-secondary-background.png
date: 2023-03-26 20:00

I recently came across a situation where I wanted to match the background colour of a a header above a SwiftUI `List` (using the default `.insetGrouped` List style) to that used by the List itself. I had done no styling to the List itself, so was relying on the system-provided background colour—this is what I wanted to match.

I tried a couple of the standard constants provided by `UIColor`, and landed on [`.secondarySystemBackground`](https://developer.apple.com/documentation/uikit/uicolor/3173137-secondarysystembackground). It wasn't until I had the build running on my phone and I was using the app later in the day that I noticed something was off slightly:

![SwiftUI List background using .secondarySystemBackground in light and dark mode](/assets/swiftui-secondary-background.png)

In light mode, everything was fine; but in dark mode, the background of the header and navigation toolbar wasn't dark enough! It turns out that what I *actually* wanted was [`.systemGroupedBackground`](https://developer.apple.com/documentation/uikit/uicolor/3173145-systemgroupedbackground):

![SwiftUI List background using .systemGroupedBackground in light and dark mode](/assets/swiftui-grouped-background.png)

Now they match up as intended. Let this be a lesson to myself to test in both light mode and dark mode when developing anything that relies on colour!
