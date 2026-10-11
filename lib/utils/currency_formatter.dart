import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../screens/system_settings/bloc/system_settings_bloc.dart';

class CurrencyFormatter {
  /// Used when the server settings haven't loaded yet.
  static const String fallbackSymbol = 'TSh';

  /// Amount with the currency symbol from system settings, e.g. "TSh1,250,000".
  static String formatAmount(BuildContext context, dynamic amount) {
    final String symbol = context.read<SystemSettingsBloc>().currencySymbol;
    return formatAmountWithSymbol(symbol.isEmpty ? fallbackSymbol : symbol, amount);
  }

  /// Amount with the given symbol and thousands separators. Decimals are shown
  /// only when the amount has them (12.5 -> 12.50).
  static String formatAmountWithSymbol(String currencySymbol, dynamic amount) {
    if (amount == null || amount == '') {
      return '${currencySymbol}0';
    }
    final cleaned = amount.toString().replaceAll(RegExp(r'[₹$€£¥,]'), '').replaceAll(currencySymbol, '').trim();
    final num? value = num.tryParse(cleaned);
    if (value == null) return '$currencySymbol$cleaned';
    final hasFraction = value % 1 != 0;
    final formatted = NumberFormat.decimalPatternDigits(
      locale: 'en_US',
      decimalDigits: hasFraction ? 2 : 0,
    ).format(value);
    return '$currencySymbol$formatted';
  }
}
