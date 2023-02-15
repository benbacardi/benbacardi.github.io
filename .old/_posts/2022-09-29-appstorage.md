---
layout: post
title: "UserDefaults, @AppStorage, and Data Types"
categories: Swift Apps Development
---

As I'm starting to play more seriously with iOS app development, Xcode, and Swift, I'm starting to come up with a variety of patterns I use in the various toy apps I mess around with that make working with certain APIs or frameworks easier. One of these is `UserDefaults`, which provides an easy way to store persistent data between app launches.

The basic way to interact with `UserDefaults` is to set values by assigning a data type to a particular key (which are strings), and reading that key later:

```swift
// Storing a boolean value
UserDefaults.standard.setValue(true, forKey: "hasPerformedInitialSync")

// Retrieving a boolean value
let hasPerformedInitialSync = UserDefaults.standard.bool(forKey: "hasPerformedInitialSync")
```

There are two problems with this, though:

1. Using string-based keys is error-prone; it can't be checked by the compiler, so an overlooked typo can lead to unexpected behaviour that's difficult to debug.
2. SwiftUI is based around watching state variables for changes, and redrawing views based upon this; how can we tie `UserDefaults` into that?

## A `UserDefaults` extension

The first problem is one I've started solving by creating an extension to the `UserDefaults` class. I put this in a new Swift file (usually `Extensions/UserDefaults.swift`), with code such as the following:

```swift
extension UserDefaults {
    enum Key: String {
        case hasPerformedInitialSync
    }
    var hasPerformedInitialSync: Bool {
        get { bool(forKey: Key.hasPerformedInitialSync.rawValue) }
        set { setValue(newValue, forKey: Key.hasPerformedInitialSync.rawValue) }
    }
}
```

This has promoted the previous string-based keys we were using to an `enum`: the compiler is now able to check our keys for us and produce errors at compile time if we use one we haven't defined. An additional computed property on the `UserDefaults` class hides the get and set logic from us, so in the rest of our code we need only do the following:

```swift
// Storing a boolean value
UserDefaults.standard.hasPerformedInitialSync = true

// Retrieving a boolean value
let hasPerformedInitialSync = UserDefaults.standard.hasPerformedInitialSync
```

Hurray! No more string-based keys to remember. But what about the second problem?

Up until recently, I was syncing `UserDefaults` changes with SwiftUI view state by storing a related `@State` variable, and tying it to the corresponding `UserDefaults` key using `onAppear` and `onChange(of:)`:

```swift
struct ContentView: View {
  @State private var hasPerformedInitialSync: Bool = false
  var body: some View {
		NavigationView {
      // View code
      Button(action: {
        hasPerformedInitialSync = true
      }) {
        Text("Sync Done!")
      }
    }
    .onAppear {
      hasPerformedInitialSync = UserDefaults.standard.hasPerformedInitialSync
    }
    .onChange(of: $hasPerformedInitialSync) { newValue in
      UserDefaults.standard.hasPerformedInitialSync = newValue
    }
  }
}
```

This works by fetching the value stored in `UserDefaults` when the view first appears and assigning it to the state variable, and then watching the state variable for changes, and syncing those back to the `UserDefaults` key. But there are still problems with this:

1. It's easy to forget to add the required line to `onAppear` or the `onChange` handler for a new variable.
2. The view won't react to changes that happen to the `UserDefaults` key outside of its own interaction, such as if a presented sheet changes the value.

Fortunately, SwiftUI introduced a new property wrapper similar to `@State` to help us with this.

## Introducing `@AppStorage`

Called `@AppStorage`, the new property wrapper lets you reference a `UserDefaults` key directly and bind it to a variable that will automatically sync changes between itself and `UserDefaults`. It can be used as such:

```swift
struct ContentView: View {
  @AppStorage(UserDefaults.Key.hasPerformedInitialSync) private var hasPerformedInitialSync: Bool = false
  var body: some View {
    // View code
  }
}
```

Note that there's no longer any need for the value to be read `onAppear`, or the changes to be observed using `onChange`. SwiftUI will take care of that for us, automatically syncing data back when actions within the view change the state variable's value. Very handy!

## Supported Data Types

However, there are still limitations with this approach, one of which I ran into today and was banging my head against for quite some time until I realised the issue.

`UserDefaults` supports the storage of [a variety of primitive data types](https://developer.apple.com/documentation/foundation/userdefaults):

* Boolean
* String
* Integer
* Data
* URL
* Double
* Float

It also supports storing arrays or dictionaries containing these primitive types, using the `array(forKey:)`, `stringArray(forKey:)`, and `dictionary(forKey:)` methods. `AppStorage`, however, does not support this. Apple's [documentation for `AppStorage`](https://developer.apple.com/documentation/swiftui/appstorage) lists the `init` methods available, and they can return:

* String
* Integer
* Data
* URL
* Double
* Boolean

It's missing `Float`—I didn't care about that—and the `Array` and `Dictionary` methods—I *did* care about those. I had created my `UserDefaults` extension, as normal:

```swift
extension UserDefaults {
    enum Key: String {
        case favouriteColours
    }
    var favouriteColours: [String] {
        get { stringArray(forKey: Key.favouriteColours.rawValue) ?? [] }
        set { setValue(newValue, forKey: Key.favouriteColours.rawValue) }
    }
}
```

That worked fine, as expected. But when I tried to use it with `@AppStorage`:

```swift
@AppStorage(UserDefaults.Key.favouriteColours) private var favouriteColours: [String] = []
```

the compiler threw up the error `No exact matches in call to initializer`. Helpful. It turns out that's because of the lack of support for the collection methods, and I had to resort to using my original `onAppear`/`onChange` workaround.

## It's not all bad, though!

Despite this frustrating limitation with `AppStorage` (which I hope is fixed in a future SwiftUI release), I really like the `UserDefaults` extension method for working with the API. There's two more things I want to mention about it. One, it can be used to store or return any data type, as long as you can easily convert it to or from one of the supported types. For example, storing a custom `enum` is easy. Make the `enum` inherit from `Int` or `String`, and you're off to the races:

```swift
enum Mode: Int {
  case light
  case dark
}

extension UserDefaults {
  enum Key: String {
    case preferredMode
  }
  var preferredMode: Mode {
    get { Mode(rawValue: integer(forKey: Key.preferredMode.,rawValue)) ?? .light }
    set { setValue(newValue.rawValue, forKey: Key.preferredMode.rawValue) }
  }
}
```

Secondly, if you want to be able to access the data you're storing in other targets, such as a widget, the extension is a great place to create a static property that uses a group identifier:

```swift
extension UserDefaults {
  static let shared = UserDefaults(suiteName: "group.com.myapp.AppName")!
}
```

Accessing `UserDefaults.shared` instead of `UserDefaults.standard` will allow it to be read and written from any targets that have access to the specified group identifier. Additionally, SwiftUI provides two different ways of specifying that you want to use `.shared` instead of `.standard`. It can be done on a per-variable basis by passing the `store:` parameter to `@AppStorage`:

```swift
@AppStorage(UserDefaults.Key.preferredMode.rawValue, store: UserDefaults.shared) private var preferredMode: Mode = .light)
```

Or it can be made the default for all child views within a hierarchy:

```swift
struct MyApp: App {
  var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .defaultAppStorage(UserDefaults.shared)
    }
}
```

Both of which make working with `UserDefaults` cross-application much easier.

Anyway, I'm mostly writing this down so that the next time I'm struggling with it I can prompt myself on how it works and why I've done things a certain way; but maybe it can help you, too!
