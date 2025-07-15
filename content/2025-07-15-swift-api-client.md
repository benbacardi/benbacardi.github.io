title: A Swift API Client
category: Development
tags: Swift

In a new app I've been toying with the idea of developing, much of the data comes from a third-party API. This isn't uncommon nowadays, and there are multiple Swift packages out there to make interacting with a REST API easier, such as [Alamofire](https://github.com/Alamofire/Alamofire). However, I wanted to build a minimal API client that I could use without relying on a third-party dependency, code that is under my control, and that I hopefully understand!

Using `URLSession` and `URLRequest` is relatively simple, but without some form of abstraction you'll end up with a bunch of boilerplate code for each different request you need make. My goal was to build a simple, generic API client protocol that I could use for this particular API, but would also work for other use cases in the future.

So let's get started!

## The APIClient protocol

The fundamental job of an API client is to send HTTP requests to the API, and return the response. We can start by building a protocol for such a client, using the power of Swift's [Generics](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/generics/) to accept a variety of different request objects and return a variety of different responses:

```swift
protocol APIClient {
    var baseUrl: URL { get }
    func send<T: APIRequest>(_ request: T) async throws -> T.Response
}
```

I've also added a `baseUrl` parameter, to allow the client to specify a single base URL for the API calls.

You'll note that I've used a type I haven't yet defined, `APIRequest`, so let's do that now. A request needs a handful of properties:

- the resource the request relates to;
- the HTTP method to use;
- any querystring parameters;
- any request body;
- any custom headers.

We can define a protocol to handle these requirements:

```swift
protocol APIRequest: Encodable {
    associatedtype Response: Decodable
    var resourceName: String { get }
    var method: String { get }
    var parameters: [URLQueryItem] { get }
    var body: Data? { get }
    var headers: [String: String] { get }
}

extension APIRequest {
    var parameters: [URLQueryItem] { [] }
    var method: String { "GET" }
    var body: Data? { nil }
    var headers: [String: String] { [:] }
}
```

There are sensible defaults for most of these properties (such as defaulting to a `GET` request with no body, no parameters, and no custom headers), so an extension to the protocol can define these.

Here we also define an **associated type** called `Response`, which must be `Decodable`. This allows us to tie an `APIRequest` to a struct representing the response it expects, and is used as the return type in the function signature of `send` in the `APIClient` protocol above.

So what's missing? The actual functionality of the `send` method, of course!

```swift
extension APIClient {
    func send<T: APIRequest>(_ request: T) async throws -> T.Response {
        let endpointRequest = self.endpointRequest(for: request)
        let (data, _) = try await URLSession.shared.data(for: endpointRequest)
        return try JSONDecoder().decode(T.Response.self, from: data)
    }
}
```

Just three simple lines:

1. Call another method, `endpointRequest(for:)`, to generate a `URLRequest` object (more on this below).
2. Execute the request and await the response.
3. Decode that response from JSON into the request's `Response` struct.

This is a nice short method for a couple of reasons. First, it doesn't do any error handling—that's left as an exercise for the reader to decide how to handle the various possible network request errors or response decoding errors. Secondly, the conversion of the `APIRequest` object into a `URLRequest` object is handed off to another method, so let's write that now:

```swift
extension APIClient {
    func endpointRequest<T: APIRequest>(for request: T) -> URLRequest {
        guard let baseUrl = URL(string: request.resourceName, relativeTo: self.baseUrl) else {
            fatalError("Invalid URL for resource \(request.resourceName)")
        }
        var components = URLComponents(url: baseUrl, resolvingAgainstBaseURL: true)!
        components.queryItems = request.parameters
        var urlRequest = URLRequest(url: components.url!)
        urlRequest.httpMethod = request.method
        if let body = request.body {
            urlRequest.httpBody = body
        }
        for (header, value) in request.headers {
            urlRequest.setValue(value, forHTTPHeaderField: header)
        }
        return urlRequest
    }   
}
```

This does a couple of things:

1. Adds the request's `resourceName` to the API client's `baseUrl` to generate the full URL for the request.
2. Adds any parameters from the request a `URLComponents` object based on the generated URL.
3. Creates a `URLRequest` object with the full URL (that will now include any querystring parameters).
4. Sets the HTTP method, body, and headers from the `APIRequest` object.
5. Returns the fully configured `URLRequest`.

Now we're ready to actually use the API client!

## Using the APIClient protocol

First, we need to create a concrete class from the protocol, and define our API's base URL:

```swift
class MyAPIClient: APIClient {
    let baseUrl = URL(string: "https://example.com/api/v3/")!
    static let shared = MyAPIClient()
}
```

In this example API, there are two endpoints:

- `/api/v3/checkKey` - returns the status of the API key provided.
- `/api/v3/getKeyUsageStats` - returns the usage stats of the API key provided.

In both cases, the API key must be provided as a querystring parameter called `apiKey`—for example, `/api/v3/checkKey?apiKey=12345`.

We can write the `APIRequest` structs to represent both of these calls:

```swift
let API_KEY_PARAMETER = URLQueryItem(name: "apiKey", value: "MY_API_KEY")

struct ExampleCheckKeyRequest: APIRequest {
    typealias Response = ExampleCheckKeyResponse
    var resourceName: String = "checkKey"
    var parameters: [URLQueryItem] = [API_KEY_PARAMETER]
}

struct ExampleGetKeyUsageRequest: APIRequest {
    typealias Response = ExampleGetKeyUsageResponse
    var resourceName: String = "getKeyUsageStats"
    var parameters: [URLQueryItem] = [API_KEY_PARAMETER]
}
```

Note that they both specify their associated `Response` types—remember, these need to be `Decodable` structs that can be used as the destination for the returned JSON from each API call. We can write these as follows:

```swift
// checkKey returns a JSON object with a `status` string and optional `message`
struct ExampleCheckKeyResponse: Decodable {
    let status: String
    let message: String?
}

// getKeyUsage returns a JSON object with a `status` string, an optional `message`,
// and a `matches` integer with the number of times the key has been used recently
struct ExampleGetKeyUsageResponse: ExampleAPIResponse {
    let status: String
    let message: String?
    let matches: Int?
}
```

With the request and response types set up, all that's left is to add helper methods to our actual client, so that the rest of our code doesn't need to know or understand the requests themselves:

```swift
extension ExampleAPIClient {
    func checkKey() async throws -> ExampleCheckKeyResponse {
        return try await self.send(ExampleCheckKeyRequest())
    }
    func getKeyUsage() async throws -> ExampleGetKeyUsageResponse {
        return try await self.send(ExampleGetKeyUsageRequest())
    }
}
```

And finally, call them!

```swift
do {
    let checkKeyResult = try await ExampleAPIClient.shared.checkKey()
    print("\(checkKeyResult)")
    let getKeyUsageResult = try await ExampleAPIClient.shared.getKeyUsage()
    print("\(getKeyUsageResult)")
} catch {
    print("Error: \(error.localizedDescription)")
}

// Prints:
// ExampleCheckKeyResponse(status: "success", message: nil)
// ExampleGetKeyUsageResponse(status: "success", message: nil, matches: Optional(2))
```

Simples, no?

So far, these are very simple requests, and I haven't included much (if any!) error handling—but it feels like a good start to a simple API client interface I can use throughout my apps, with little code, and code that actually feels maintainable.
