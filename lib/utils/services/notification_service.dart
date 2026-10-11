// ignore_for_file: depend_on_referenced_packages

import 'package:zenjishoppazz_rider/utils/currency_formatter.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:timezone/timezone.dart' as tz;

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();
  factory NotificationService() => _instance;
  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _flutterLocalNotificationsPlugin =
      FlutterLocalNotificationsPlugin();

  Future<void> initialize() async {

    await _requestPermissions();


    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@drawable/notification');


    const DarwinInitializationSettings initializationSettingsIOS =
        DarwinInitializationSettings(
          requestAlertPermission: true,
          requestBadgePermission: true,
          requestSoundPermission: true,
        );


    const InitializationSettings initializationSettings =
        InitializationSettings(
          android: initializationSettingsAndroid,
          iOS: initializationSettingsIOS,
        );


    await _flutterLocalNotificationsPlugin.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );
  }

  Future<void> _requestPermissions() async {

    if (await Permission.notification.isDenied) {
      await Permission.notification.request();
    }
  }

  void _onNotificationTapped(NotificationResponse response) {



  }


  Future<void> showNotification({
    required int id,
    required String title,
    required String body,
    String? payload,
  }) async {
    const AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
          'zenjishoppazz_rider_channel',
          'Zenjishoppazz Rider notifications',
          channelDescription: 'Order and delivery updates for Zenjishoppazz riders',
          importance: Importance.high,
          priority: Priority.high,
          showWhen: true,
          enableVibration: true,
          playSound: true,
          sound: RawResourceAndroidNotificationSound('notification_sound'),
        );

    const DarwinNotificationDetails iOSPlatformChannelSpecifics =
        DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
        );

    const NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
      iOS: iOSPlatformChannelSpecifics,
    );

    await _flutterLocalNotificationsPlugin.show(
      id,
      title,
      body,
      platformChannelSpecifics,
      payload: payload,
    );
  }


  Future<void> showNewOrderNotification({
    required String orderId,
    required String customerName,
    required String pickupAddress,
  }) async {
    await showNotification(
      id: int.parse(orderId),
      title: 'New Order Received!',
      body: 'Order #$orderId from $customerName at $pickupAddress',
      payload: 'new_order_$orderId',
    );
  }


  Future<void> showOrderStatusNotification({
    required String orderId,
    required String status,
    required String message,
  }) async {
    await showNotification(
      id: int.parse(orderId) + 1000,
      title: 'Order #$orderId - $status',
      body: message,
      payload: 'order_status_$orderId',
    );
  }


  Future<void> showPaymentNotification({
    required String orderId,
    required double amount,
  }) async {
    await showNotification(
      id: int.parse(orderId) + 2000,
      title: 'Payment Received!',
      body:
          'Payment of ${CurrencyFormatter.formatAmountWithSymbol(CurrencyFormatter.fallbackSymbol, amount)} received for order #$orderId',
      payload: 'payment_$orderId',
    );
  }


  Future<void> showEarningsNotification({
    required String period,
    required double amount,
  }) async {
    await showNotification(
      id: 9999,
      title: 'Earnings Update',
      body: 'Your $period earnings: ${CurrencyFormatter.formatAmountWithSymbol(CurrencyFormatter.fallbackSymbol, amount)}',
      payload: 'earnings_$period',
    );
  }


  Future<void> showMaintenanceNotification({
    required String message,
    required DateTime scheduledTime,
  }) async {
    await showNotification(
      id: 8888,
      title: 'System Maintenance',
      body: message,
      payload: 'maintenance_${scheduledTime.millisecondsSinceEpoch}',
    );
  }


  Future<void> cancelNotification(int id) async {
    await _flutterLocalNotificationsPlugin.cancel(id);
  }


  Future<void> cancelAllNotifications() async {
    await _flutterLocalNotificationsPlugin.cancelAll();
  }


  Future<List<PendingNotificationRequest>> getPendingNotifications() async {
    return await _flutterLocalNotificationsPlugin.pendingNotificationRequests();
  }


  Future<void> scheduleNotification({
    required int id,
    required String title,
    required String body,
    required DateTime scheduledDate,
    String? payload,
  }) async {
    const AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
          'zenjishoppazz_rider_scheduled_channel',
          'Scheduled Notifications',
          channelDescription:
              'Scheduled reminders for Zenjishoppazz riders',
          importance: Importance.high,
          priority: Priority.high,
          showWhen: true,
          enableVibration: true,
          playSound: true,
        );

    const DarwinNotificationDetails iOSPlatformChannelSpecifics =
        DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
        );

    const NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
      iOS: iOSPlatformChannelSpecifics,
    );

    await _flutterLocalNotificationsPlugin.zonedSchedule(
      id,
      title,
      body,
      tz.TZDateTime.from(scheduledDate, tz.local),
      platformChannelSpecifics,
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      payload: payload,
    );
  }
}
