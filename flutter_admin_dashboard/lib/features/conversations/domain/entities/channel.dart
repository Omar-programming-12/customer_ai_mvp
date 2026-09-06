/// The messaging channel a conversation is coming from.
///
/// Today every conversation arrives through Meta Messenger (via the existing
/// FastAPI webhook integration). This is modeled as an enum rather than a
/// hardcoded assumption so another channel (Instagram, WhatsApp) can be
/// added later without touching any entity/use case signature.
enum Channel { messenger, instagram, whatsapp }
