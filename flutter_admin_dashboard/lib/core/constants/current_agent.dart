/// The signed-in support agent. Hardcoded because there is no auth yet (out
/// of scope for this phase per the current brief) - once Firebase Auth is
/// introduced, this becomes a read from the auth/session state instead of a
/// constant, and every call site here already takes the name as a plain
/// parameter, so nothing else needs to change.
abstract final class CurrentAgent {
  static const name = 'ياسمين علي';
}
