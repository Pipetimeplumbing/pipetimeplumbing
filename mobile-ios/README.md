# Pipe Time for iPhone and iPad

Native SwiftUI app targeting iOS 16+. Includes native service navigation, click-to-call, business contact sharing, locally saved home address, Stripe payments, and connected web screens for Housecall Pro booking, messages, and client accounts. Account and message sessions share the default WKWebView data store. No Housecall Pro appointments are synced into a native calendar.

## Build on a Mac

1. Install current Xcode and XcodeGen (`brew install xcodegen`).
2. From this directory, run `python3 configure.py https://YOUR-LIVE-SERVICE.onrender.com` using the actual deployed website URL.
3. Run `xcodegen generate`, then open `PipeTime.xcodeproj`.
4. In Signing & Capabilities, select your Apple Developer team and set an available bundle identifier (default: `com.pipetimeplumbing.client`).
5. Add a 1024×1024 opaque app icon to AppIcon in the asset catalog. The uploaded business logo is not available here as a standalone source asset; request the original before preparing final artwork.
6. Build and run on an iPhone simulator and physical device. Check all tabs, account registration/login/logout/deletion, message submission, Housecall Pro availability, payment checkout navigation, phone links, saved address, sharing, and offline retry. Verify booking popups and third-party cookie behavior on an actual device; live provider behavior is unverified.
7. Use Product → Archive with a device destination, then distribute through App Store Connect/TestFlight. No signed archive has been built in this Linux workspace.

## Before App Store submission

- Provide the live website address, Apple Developer membership, signing team, and App Store Connect app record.
- Use persistent production storage for client accounts and messages. Render's temporary filesystem is not sufficient.
- Complete a working privacy policy URL, support URL, screenshots, app description, and accurate App Privacy answers covering the app, website, Stripe, and Housecall Pro. Contact details and user messages are sent to the web backend; the optional saved home address stays on-device unless shared by the user. Do not claim that no data is collected. The included privacy manifest declares UserDefaults for app preferences and known contact/message data; verify third-party booking/payment disclosures and any financial data collection before submission.
- Finish the staff inbox/notifications, email verification, and password reset before customer launch. Account deletion is available in the web account screen; it removes app account data only, not independent Housecall Pro or Stripe records.
- Supply a review demo account and any instructions needed to access booking without creating real appointments. Do not include credentials in source control.
- Review current Apple minimum-functionality requirements. Native screens and device features are implemented, but approval is Apple's decision. This is an app source package, not an approved or published App Store app.
- Physical plumbing/heating service payments use Stripe; no digital goods are sold in this app.

No camera, location, tracking, or notification permission is requested. There is no automatic calendar sync, push notification integration, or password reset feature in this version.
