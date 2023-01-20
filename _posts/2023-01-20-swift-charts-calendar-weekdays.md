---
layout: post
title: Swift Charts & Calendar Weekdays
categories: Swift Development Programming
date: 2023-01-20 16:30
image: /assets/pendulum-weekday-chart.jpeg
---

I've recently been working on adding a statistics section to [Pendulum](/pendulum/), the pen pal tracking app I develop with my friend [Alex](https://418teapot.net). This seemed like the perfect opportunity to use [Swift Charts](https://developer.apple.com/documentation/charts), Apple's new charting framework.

I ultimately wanted to end up with a graph like the following:

[![Bar chart showing the number of letters written and sent per day of the week](/assets/pendulum-weekday-chart.jpeg)](/assets/pendulum-weekday-chart.jpeg)

Swift Charts can perfectly handle multiple datasets on one graph, but the problem I ran into was that it doesn't seem to have a way to natively aggregate data per *day of the week*. If I only had seven days worth of data, it would be fine—I could display just the day name on the axis, and no days would be repeated because I wouldn't be displaying more than a week of data. However, as I want to aggregate every event, this wasn't going to work. I decided to do the grouping of the data myself, and just pass Swift Charts a pre-binned dataset for it to present, where it wouldn't have to worry about dates at all.

I had one other problem I wanted to solve: I wanted the graph to start on whatever the current locale thinks the start of the week is[^1]. For us in the UK and Europe, we generally consider Monday the beginning of the week, as reflected in the graph above. But for the US, it should probably start with Sunday.

In order to generate the seven "bins" for the chart to show, I could use the handy `Calendar.current.shortWeekdaySymbols` property, which produces an array of the shortened names of the week, properly localised to the user's current locale. However, regardless of locale, this array always starts with Sunday and ends with Saturday. There's another property of the calendar, `.firstWeekday`, that returns a number between 1 (for Sunday) and 7 (for Saturday) representing what the locale considers to be the first day of the week. Using this, I can shift the array from `shortWeekdaySymbols` to produce the output in the right order. I decided to wrap both these pieces of information up in an enum to represent each day of the week:

```swift
enum Weekday: Int, CaseIterable {
    case sun = 1
    case mon = 2
    case tue = 3
    case wed = 4
    case thu = 5
    case fri = 6
    case sat = 7
    
    var shortName: String {
        return Calendar.current.shortWeekdaySymbols[self.rawValue - 1]
    }
    
    static var orderedCases: [Weekday] {
        Self.allCases.shiftRight(by: Calendar.current.firstWeekday - 1)
    }
}
```

You'll also notice I'm using an extension to `Array` that allows me to shift an array, wrapping the values around to the end as they get popped off the front:

```swift
extension Array {
    func shiftRight(by: Int = 1) -> [Element] {
        guard count > 0 else { return self }
        var amount = by
        assert(-count...count ~= amount, "Shift amount out of bounds")
        if amount < 0 { amount += count }
        return Array(self[amount ..< count] + self[0 ..< amount])
    }
}
```

Now that I have an enum I can use to represent the days of the week correctly, and order them as defined  by the user's locale, I needed to use this somehow to generate data to pass to the chart. I started off by defining a struct to hold a single datapoint:

```swift
struct StatusCountByDay: Identifiable {
    let status: EventType
    let day: Weekday
    let count: Int
    var id: String { "\(day)-\(status.rawValue)" }
}
```

Here, `EventType` is an internal enum used by Pendulum to mark whether the event was a letter being sent, written, received, etc. What makes each data point unique in the chart is the combination of the day of the week, and the event type, so I combine those two together as the `id` for the struct.

Next, I needed to fetch the data and group it into buckets:

```swift
var days: [Weekday: [Event]] = [:]

for event in Event.fetch(withStatus: [.written, .sent]) {
    if !days.keys.contains(event.wrappedDate.weekday) {
        days[event.wrappedDate.weekday] = []
     }
     days[event.wrappedDate.weekday]?.append(event)
}
```

I start by defining a dictionary mapping weekdays to an array of events, and then looping over the events I'm interested in and adding them to the corresponding weekday key in the dictionary. This necessitated another extension to a `Foundation` object, this time on `Date`[^2]:

```swift
extension Date {
    var dayNumberOfWeek: Int? {
        return Calendar.current.dateComponents([.weekday], from: self).weekday
    }
    var weekday: Weekday {
        return Weekday(rawValue: dayNumberOfWeek ?? 0) ?? .sun
    }
}
```

This uses the `.weekday` date component from the user's current calendar, which returns the same 1–7 index as used by `.firstWeekday`, and returns the corresponding `Weekday` object.

With the data correctly bucketed, it was time to sum up the series and create the datapoints for the chart. When the data provided is not sequential (such as a series of dates) but is instead discrete (such as list of names, for example) Swift Charts will draw the bars in the order in which it first encounters them. You may think that weekdays are sequential—and you'd be right—but in this case, they're not an object that Swift Charts understands in that way. So to draw the chart as intended, we need to create a `StatusCountByDay` instance for each weekday in the order we want. We also need to include one even when the count for that day is zero, because we don't want the chart to just skip a day. I do this by looping over the weekdays ordered according to the locale, inside that looping over each event type, and calculating the sum for each:

```swift
var results: [StatusCountByDay] = []
for eventType in [EventType.written, EventType.sent] {
    for day in Weekday.orderedCases {
        let count = (days[day] ?? []).filter { $0.type == eventType }.count
        results.append(StatusCountByDay(status: eventType, day: day, count: count))
    }
}
```

Ultimately, we end up with a series of data like the following:

```swift
[
    StatusCountByDay(status: .sent, day: .sun, count: 2),
    StatusCountByDay(status: .sent, day: .mon, count: 0),
    StatusCountByDay(status: .sent, day: .tue, count: 1),
    StatusCountByDay(status: .sent, day: .wed, count: 5),
    StatusCountByDay(status: .sent, day: .thu, count: 12),
    StatusCountByDay(status: .sent, day: .fri, count: 5),
    StatusCountByDay(status: .sent, day: .sat, count: 1),
    StatusCountByDay(status: .written, day: .sun, count: 3),
    StatusCountByDay(status: .written, day: .mon, count: 2),
    StatusCountByDay(status: .written, day: .tue, count: 2),
    StatusCountByDay(status: .written, day: .wed, count: 1),
    StatusCountByDay(status: .written, day: .thu, count: 2),
    StatusCountByDay(status: .written, day: .fri, count: 1),
    StatusCountByDay(status: .written, day: .sat, count: 10)
]
```

All that's left is to pass that to Swift Charts, for which I'll break down each section after I show the code:

```swift
Chart(results) { data in
    BarMark(
        x: .value("Day", data.day.shortName),
        y: .value("Count", data.count)
    )
    .annotation(position: .top, alignment: .top) {
        if data.count != 0 {
            Text("\(data.count)")
                .font(.footnote)
                .bold()
                .foregroundColor(data.status.color)
                .opacity(0.5)
        }
    }
    .foregroundStyle(by: .value("event", data.status.actionableTextShort))
    .position(by: .value("event", data.status.actionableTextShort))
}
.chartForegroundStyleScale([
    EventType.sent.actionableTextShort: EventType.sent.color,
    EventType.written.actionableTextShort: EventType.written.color,
])
```

Firstly, we want a bar chart, so the correct type of mark to use is a `BarMark`. The `x` axis is the short name of the weekday ("Mon", "Tue", etc), and the `y` axis is the count.

The `.annotation` section puts the little figures above each bar, and isn't particularly necessary but I liked the way it looked.

The two `BarMark` modifiers `.foregroundStyle(by:)` and `.position(by:)` both tell Swift Charts how to define and handle each series independently; otherwise, they'd be a single bar, stacked on top of each other within each day. Grouping them by event type, the first modifier tells them to be different colours, and the second puts them as independent bars side by side instead of on top of each other. I use `data.status.actionableTextShort` as the value to distinguish the data by, because that is what I want shown in the legend beneath the chart ("Sent" vs "Written", etc).

You can see below the results of the chart without the `.position(by:)` modifier, and without the `.foregroundStyle(by:)` modifier, respectively.

![The chart without each modifier](/assets/pendulum-chart-modifiers.png)

Finally, the `.chartForegroundStyleScale` modifier defines the colours to be used for each series, which is a dictionary mapping the name of the series to its colour. In this case, I use want them using the colour defined for the event type, to keep it consistent with the rest of the app.

---

I'm quite impressed with Swift Charts and how easy it makes drawing a good looking chart, but there are definitely some things that could be more obvious about it. The lack of decent documentation *with plenty of examples and screenshots* being a very clear area for improvement!

---

[^1]: Yes, I realise none of the rest of the app is localised. Baby steps, though!
[^2]: As you may have realised by now, I'm quite a fan of writing extensions to standard types for common functions that could end up being performed regularly. They make the rest of the code a lot cleaner. It's one of my favourite features of Swift.
