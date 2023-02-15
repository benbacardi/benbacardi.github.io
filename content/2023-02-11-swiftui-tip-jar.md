title: Implementing a Tip Jar with Swift and SwiftUI
category: Development
tags: Swift
image:
status: draft

Pressured by friends, I recently added a tip jar to [Pendulum](/pendulum/), the pen pal tracking app I develop with my friend [Alex](https://418teapot.net). It's implemented (like the rest of the app) in pure SwiftUI, and uses the newer [StoreKit 2](https://developer.apple.com/storekit/) APIs to communicate with Apple to fetch the IAP information and make purchases. This is a write of how I muddled through the process, from start to finish.

## Defining the tip IAPs

The first step is to head into [App Store Connect](https://appstoreconnect.apple.com) and define the IAPs for each of the tips you want to offer. In my case, I knew what I wanted the tips to be called, in ascending order of price, but not exactly what price each would be. That doesn't matter for now, though. I had the following in mind, amusingly named after fountain pen nib sizes:

* Extra Fine Tip
* Fine Tip
* Medium Tip
* Broad Tip
* Stub Tip

To create these in App Store Connect, I headed to the **In-App Purchases** section under **Features** on the app's **App Store** tab. There, I could create each tip using the plus button. The initial form has three fields:

* **Type**: either *Consumable* or *Non-Consumable*. I didn't know what these are, and had to look them up: consumable IAPs are those that can be purchased multiple times by the user (for things such as in-game currency), and non-consumable IAPs can only be purchased once (for features such as unlocking a premium mode of the app). For a tip jar, I wanted the former.
* **Reference Name**: a name for the IAP, solely for your own use. It doesn't appear anywhere public; for ease, I entered the names I'd chosen for the tips above.
* **Product ID**: a unique identifier for the IAP. I wasn't sure *how* unique this was meant to be, so to be on the safe side I went for the usual Apple-style of defining them as reversed-DNS bundle identifiers. For example, `uk.co.bencardy.Pendulum.ExtraFineTip`, etc.

Once created, to complete the IAP you need to define a few extra fields that aren't present on the initial form, such as the Price Schedule (where you set the cost of the IAP, using Apple's price tiers), and the App Store Localization, where you define how the tip appears (its name and description) in the App Store for each language. I defined only "English (U.K.)" which is all the app is offered in.

## Defining the tips in Swift

StoreKit2 doesn't have an API to fetch all the IAPs associated with an app; instead, you need to request specific Product IDs known by the app ahead of time. To this end, I decided it would be best to represent the available tips in the app with an `enum`, based off their unique IDs:

```swift
enum TipJar: String, CaseIterable {
    case extraFine = "uk.co.bencardy.Pendulum.ExtraFineTip"
    case fine = "uk.co.bencardy.Pendulum.FineTip"
    case medium = "uk.co.bencardy.Pendulum.MediumTip"
    case broad = "uk.co.bencardy.Pendulum.BroadTip"
    case stub = "uk.co.bencardy.Pendulum.StubTip"
    
    var name: String {
        switch self {
        case .extraFine:
            return "Extra Fine"
        case .fine:
            return "Fine"
        case .medium:
            return "Medium"
        case .broad:
            return "Broad"
        case .stub:
            return "Stub"
        }
    }
}
```

I made the `enum` conform to `CaseIterable`, meaning I can iterate over `TipJar.allCases` to display all available tips in the SwiftUI view. This I did inside my `TipJarView`, wrapping each tip in a button and displaying some placeholder information about each one:

```swift
struct TipJarView: View {
    var body: some View {
        List {
            ForEach(TipJar.allCases, id: \.self) { tip in
                Button(action: {}) {
                    HStack {
                        Text(tip.name)
                            .foregroundColor(.primary)
                        Spacer()
                        Text("£??")
                            .foregroundColor(.accentColor)
                    }
                }
            }
        }
        .navigationTitle("Support Pendulum")
    }
}
```

This presented a list of the available tips, with a place for me to put their prices (once known), and a button to purchase the tip (functionality yet to be completed):

## Fetching IAP information with StoreKit 2

The next step was to actually fetch the prices I had defined in App Store Connect within the app, and display them. For this, I needed to use Apple's [StoreKit 2](https://developer.apple.com/storekit/) APIs. The particular one I'm interested in here is [`Product.products(for:)`](https://developer.apple.com/documentation/storekit/product/3851116-products), which returns an array of `Product` objects for each ID passed in. I decided to add a static method to the `TipJar` enum to call this with all my IAP IDs, and return a mapping of `[TipJar: Product]` that the view could use. The new StoreKit 2 APIs are all asyncronous, so my function needed to be to:

```swift
import StoreKit

extension TipJar {
    static func fetchProducts() async -> [Self: Product] {
        do {
            let products = try await Product.products(for: Self.allCases.map { $0.rawValue })
            var results: [Self: Product] = [:]
            for product in products {
                if let type = TipJar(rawValue: product.id) {
                    results[type] = product
                }
            }
            return results
        } catch {
            storeLogger.error("Could not fetch products: \(error.localizedDescription)")
            return [:]
        }
    }
}
```

(I am sure there is a more concise way to compile the dictionary, but those are the kinds of Swift tricks I am not yet proficient enough in the language to be able to come up with when I need them, so a simple for loop had to suffice here.)

With this extension in place, I can add a new `State` variable to my view, and fetch the product information when the view is loaded:

```swift
struct TipJarView: View {
    @State private var tipJarPrices: [TipJar: Product] = [:]
  
    var body: some View {
        List {
            ...
        }
        .task {
            let products = await TipJar.fetchProducts()
            DispatchQueue.main.async {
                withAnimation {
                    self.tipJarPrices = products
                }
            }
        }
    }
}
```

I can now use this information in the loop around the products. The [`Product`](https://developer.apple.com/documentation/storekit/product) object provides a `displayPrice` property, which handily returns the price of the tip in the user's local currency, with the currency symbol:

```swift
ForEach(TipJar.allCases, id: \.self) { tip in
    Button(action: {}) {
        HStack {
            Text(tip.name)
                .foregroundColor(.primary)
            Spacer()
            if let product = tipJarPrices[tip] {
                Text(product.displayPrice)
                    .foregroundColor(.accentColor)
            }
        }
    }
}
```

After a brief moment with no prices available, they suddenly all fade in:

#TKTK

We can do better than that, though. Using another state variable, we can notify the view when the product information has been loaded, and display a progress spinner until that point. We also need to handle the case that, for some reason, the products have been fetched but a particular tip isn't present. I chose to do so with a simple warning triangle.

```swift
struct TipJarView: View {
    @State private var tipJarPrices: [TipJar: Product] = [:]
    @State private var productsFetched: Bool = false
  
    var body: some View {
        List {
            ForEach(TipJar.allCases, id: \.self) { tip in
                Button(action: {}) {
                    HStack {
                        Text(tip.name)
                            .foregroundColor(.primary)
                        Spacer()
                        if let product = tipJarPrices[tip] {
                            Text(product.displayPrice)
                                .foregroundColor(.accentColor)
                        } else {
                            if productsFetched {
                                Image(systemName: "exclamationmark.triangle")
                            } else {
                                ProgressView()
                            }
                        }
                    }
                }
            }
        }
        .task {
            let products = await TipJar.fetchProducts()
            DispatchQueue.main.async {
                withAnimation {
                    self.tipJarPrices = products
                    self.productsFetched = true
                }
            }
        }
    }
}
```

## Making a purchase

To initiate the actual purchase of the IAP, we need to call the `Product`'s `.purchase()` method. This async method returns a result indicating whether the purchase was successful or not, and a few other bits of information. As is my way, I chose to wrap this up in a method on the `TipJar` enum:

```swift
extension TipJar {
    func purchase(_ product: Product) async -> Bool {
        storeLogger.debug("Attempting to purchase \(self.rawValue)")
        do {
            let purchaseResult = try await product.purchase()
            switch purchaseResult {
            case .success(let verificationResult):
                storeLogger.debug("Purchase result: success")
                switch verificationResult {
                case .verified(let transaction):
                    storeLogger.debug("Purchase success result: verified")
                    await transaction.finish()
                    return true
                default:
                    storeLogger.debug("Purchase success result: unverified")
                    return false
                }
            default:
                return false
            }
        } catch {
            storeLogger.error("Could not purchase \(self.rawValue): \(error.localizedDescription)")
            return false
        }
    }
}
```

For ease of use in the view, I convert the result into a simple true or false for whether the purchase went through successfully. In the view, I can fire this off inside a `Task` in the button's `action` method, and handle the response appropriately. In this case, I want to display an alert saying thank you on a successful purchase, and do nothing if it was cancelled:

```swift
struct TipJarView: View {
    ...
    @State private var showingSuccessAlert: Bool = false
    var body: some View {
        List {
            ForEach(TipJar.allCases, id: \.self) { tip in
                Button(action: {
                    Task {
                        storeLogger.debug("\(tip.rawValue) tapped")
                        if let product = tipJarPrices[tip] {
                            Task {
                                if await tip.purchase(product) {
                                    DispatchQueue.main.async {
                                        withAnimation {
                                            showingSuccessAlert = successful
                                        }
                                    }
                                }
                            }
                        }
                    }
                }) {
                    ...
                }
            }
        }
        .alert(isPresented: $showingSuccessAlert) {
            Alert(title: Text("Purchase Successful"), message: Text("Thank you for supporting Pendulum!"), dismissButton: .default(Text("🧡")))
        }
        ...
    }
}
```



