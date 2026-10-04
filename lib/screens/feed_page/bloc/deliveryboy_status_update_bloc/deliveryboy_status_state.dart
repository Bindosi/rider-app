// delivery_boy_status_state.dart

import 'package:equatable/equatable.dart';

abstract class DeliveryBoyStatusState extends Equatable {
  final bool isOnline;
  final bool isVerified;
  final String? message;

  const DeliveryBoyStatusState({
    this.isOnline = false,
    this.isVerified = true,
    this.message,
  });

  @override
  List<Object?> get props => [isOnline, isVerified, message];
}

class DeliveryBoyStatusInitial extends DeliveryBoyStatusState {
  const DeliveryBoyStatusInitial() : super(isOnline: false, isVerified: true);
}

class DeliveryBoyStatusLoading extends DeliveryBoyStatusState {
  const DeliveryBoyStatusLoading({
    bool isOnline = false,
    bool isVerified = true,
  }) : super(isOnline: isOnline, isVerified: isVerified);
}

class DeliveryBoyStatusLoaded extends DeliveryBoyStatusState {
  final double? latitude;
  final double? longitude;

  const DeliveryBoyStatusLoaded({
    bool isOnline = false,
    bool isVerified = true,
    this.latitude,
    this.longitude,
    String? message,
  }) : super(isOnline: isOnline, isVerified: isVerified, message: message);

  @override
  List<Object?> get props => [isOnline, isVerified, latitude, longitude, message];
}

class DeliveryBoyStatusError extends DeliveryBoyStatusState {
  final String errorMessage;

  const DeliveryBoyStatusError(
    this.errorMessage, {
    bool isOnline = false,
    bool isVerified = true,
  }) : super(isOnline: isOnline, isVerified: isVerified, message: errorMessage);

  @override
  List<Object?> get props => [isOnline, isVerified, errorMessage, message];
}