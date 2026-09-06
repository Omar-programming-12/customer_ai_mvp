import 'package:flutter/material.dart';

import 'app.dart';
import 'core/di/injection_container.dart';

void main() {
  initDependencies();
  runApp(const CustomerAiAdminApp());
}
