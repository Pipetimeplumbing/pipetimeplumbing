import SwiftUI
import WebKit

enum Brand {
    static let navy = Color(red: 0.06, green: 0.17, blue: 0.26)
    static let orange = Color(red: 0.93, green: 0.43, blue: 0.21)
    static let phone = "401-400-5521"
    static let call = URL(string: "tel:+14014005521")!
    static let payment = URL(string: "https://buy.stripe.com/28E3cngMAcbh9vY5WEgEg02")!
    static var website: URL? {
        guard let file = Bundle.main.url(forResource: "ClientConfig", withExtension: "plist"),
              let data = try? Data(contentsOf: file),
              let object = try? PropertyListSerialization.propertyList(from: data, format: nil),
              let config = object as? [String: String],
              let value = config["WebsiteURL"], let url = URL(string: value),
              url.scheme == "https", url.host != nil else { return nil }
        return url
    }
    static func page(_ path: String, fragment: String? = nil) -> URL? {
        guard let website = website,
              var parts = URLComponents(url: website, resolvingAgainstBaseURL: false) else { return nil }
        parts.path = path
        parts.fragment = fragment
        return parts.url
    }
}

@main
struct PipeTimeApp: App {
    var body: some Scene { WindowGroup { MainView().tint(Brand.orange) } }
}

struct MainView: View {
    @State private var selection = 0
    var body: some View {
        TabView(selection: $selection) {
            NavigationStack { HomeView(onBook: { selection = 1 }) }
                .tabItem { Label("Home", systemImage: "house.fill") }.tag(0)
            NavigationStack { OnlinePage(url: Brand.page("/", fragment: "book"), title: "Book a visit") }
                .tabItem { Label("Book", systemImage: "calendar") }.tag(1)
            NavigationStack { OnlinePage(url: Brand.page("/login"), title: "Client account") }
                .tabItem { Label("Account", systemImage: "person.crop.circle") }.tag(2)
            NavigationStack { ContactView() }
                .tabItem { Label("Contact", systemImage: "phone.fill") }.tag(3)
        }
    }
}

struct HomeView: View {
    let onBook: () -> Void
    @Environment(\.openURL) private var openURL
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                Text("PIPE TIME").font(.largeTitle.bold()).foregroundStyle(Brand.navy)
                Text("PLUMBING & HEATING INC.").font(.caption.bold()).foregroundStyle(.secondary)
                Text("Good plumbing.\nGreat comfort.\nRight on time.")
                    .font(.system(size: 36, weight: .bold)).foregroundStyle(Brand.navy)
                Text("Help for your home, right at your fingertips.").foregroundStyle(.secondary)
                Button(action: onBook) { Label("Book an appointment", systemImage: "calendar.badge.plus").frame(maxWidth: .infinity).padding(8) }
                    .buttonStyle(.borderedProminent)
                VStack(alignment: .leading, spacing: 12) {
                    Text("Upgrade your boiler").font(.title2.bold())
                    Text("Save $500 on a new installation. Enjoy 0% interest for one year.")
                    Text("Ask our team about a high-efficiency boiler.").font(.footnote)
                }.padding(22).frame(maxWidth: .infinity, alignment: .leading)
                    .background(Brand.navy).foregroundStyle(.white).clipShape(RoundedRectangle(cornerRadius: 18))
                Text("How can we help?").font(.title2.bold())
                ForEach([("Plumbing repairs", "wrench.and.screwdriver.fill"), ("Heating service", "sun.max.fill"), ("Boiler installation", "flame.fill")], id: \.0) { item in
                    Button(action: onBook) {
                        HStack { Image(systemName: item.1).frame(width: 30); Text(item.0); Spacer(); Image(systemName: "chevron.right") }.padding(18)
                    }.background(Color(.secondarySystemBackground)).clipShape(RoundedRectangle(cornerRadius: 12))
                }
                Button { openURL(Brand.payment) } label: { Label("Make a payment", systemImage: "creditcard.fill").frame(maxWidth: .infinity).padding(8) }.buttonStyle(.bordered)
                Text("Payments open securely in Stripe.").font(.footnote).foregroundStyle(.secondary)
                Link("Call \(Brand.phone)", destination: Brand.call).font(.headline)
            }.padding(24)
        }.navigationTitle("Pipe Time").navigationBarTitleDisplayMode(.inline)
    }
}

struct ContactView: View {
    @AppStorage("savedHomeAddress") private var address = ""
    @Environment(\.openURL) private var openURL
    var body: some View {
        Form {
            Section("Pipe Time Plumbing & Heating Inc.") {
                Link(destination: Brand.call) { Label(Brand.phone, systemImage: "phone.fill") }
                ShareLink(item: "Pipe Time Plumbing & Heating Inc.\nCall 401-400-5521") {
                    Label("Share our contact", systemImage: "square.and.arrow.up")
                }
                NavigationLink { OnlinePage(url: Brand.page("/", fragment: "message"), title: "Message us") } label: {
                    Label("Send a message", systemImage: "message.fill")
                }
                Button { openURL(Brand.payment) } label: { Label("Make a payment", systemImage: "creditcard.fill") }
            }
            Section {
                TextField("Your home address", text: $address, axis: .vertical)
                    .textContentType(.fullStreetAddress)
                if !address.isEmpty {
                    ShareLink(item: address) { Label("Share my address", systemImage: "square.and.arrow.up") }
                    Button("Clear saved address", role: .destructive) { address = "" }
                }
            } header: { Text("My home") } footer: {
                Text("Saved on this device for your convenience. It is not sent to Pipe Time or added to a booking automatically.")
            }
            Section { Text("For urgent service, please call directly.") }
        }.navigationTitle("Contact & my home")
    }
}

struct OnlinePage: View {
    let url: URL?
    let title: String
    @State private var failed = false
    @State private var loading = true
    @State private var reloadID = UUID()
    var body: some View {
        Group {
            if let url = url {
                ZStack {
                    WebsiteView(url: url, failed: $failed, loading: $loading).id(reloadID)
                    if loading { ProgressView("Loading…").padding().background(.regularMaterial).clipShape(RoundedRectangle(cornerRadius: 12)) }
                    if failed {
                        VStack(spacing: 18) {
                            Image(systemName: "wifi.exclamationmark").font(.largeTitle)
                            Text("Unable to connect").font(.title2.bold())
                            Text("Check your internet connection and try again.").multilineTextAlignment(.center)
                            Button("Try again") { failed = false; loading = true; reloadID = UUID() }.buttonStyle(.borderedProminent)
                            Link("Call \(Brand.phone)", destination: Brand.call)
                        }.padding(30).frame(maxWidth: .infinity, maxHeight: .infinity).background(Color(.systemBackground))
                    }
                }
            } else {
                VStack(spacing: 18) {
                    Text("Online services aren't connected yet.").font(.headline)
                    Text("You can still call our team for help.")
                    Link("Call \(Brand.phone)", destination: Brand.call)
                }.padding()
            }
        }.navigationTitle(title).navigationBarTitleDisplayMode(.inline)
    }
}

struct WebsiteView: UIViewRepresentable {
    let url: URL
    @Binding var failed: Bool
    @Binding var loading: Bool
    func makeCoordinator() -> Coordinator { Coordinator(self) }
    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.websiteDataStore = .default()
        let view = WKWebView(frame: .zero, configuration: config)
        view.navigationDelegate = context.coordinator
        view.uiDelegate = context.coordinator
        view.allowsBackForwardNavigationGestures = true
        view.load(URLRequest(url: url))
        return view
    }
    func updateUIView(_ view: WKWebView, context: Context) { context.coordinator.parent = self }
    final class Coordinator: NSObject, WKNavigationDelegate, WKUIDelegate {
        var parent: WebsiteView
        init(_ parent: WebsiteView) { self.parent = parent }
        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) { parent.loading = false }
        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            if (error as NSError).code != NSURLErrorCancelled { parent.failed = true; parent.loading = false }
        }
        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            if (error as NSError).code != NSURLErrorCancelled { parent.failed = true; parent.loading = false }
        }
        func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let target = action.request.url else { decisionHandler(.cancel); return }
            if target.scheme == "tel" {
                UIApplication.shared.open(target); decisionHandler(.cancel); return
            }
            if target.absoluteString == "about:blank" { decisionHandler(.allow); return }
            guard target.scheme == "https" else { decisionHandler(.cancel); return }
            let external = target.host != parent.url.host && action.targetFrame?.isMainFrame != false
            if external || action.targetFrame == nil {
                UIApplication.shared.open(target); decisionHandler(.cancel)
            } else { decisionHandler(.allow) }
        }
        func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration, for navigationAction: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
            if let target = navigationAction.request.url, target.scheme == "https" { UIApplication.shared.open(target) }
            return nil
        }
    }
}
