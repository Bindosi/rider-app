import 'package:hyper_local/config/api_routes.dart';

import '../../../config/api_base_helper.dart';

class AvailableOrdersRepo {
  Future<Map<String, dynamic>> availableOrdersList({
    int? limit,
    int? offset,
    String? search = "",
  }) async {
    try {
      Map<String, dynamic> body = {};
      // if (limit != null) {
      //   body["limit"] = limit;
      // }
      // if (offset != null) {
      //   body["offset"] = offset;
      // }

      final response = await ApiBaseHelper.getApi(
        url: availableOrdersStatusApi,
        useAuthToken: true,
        params: body,
      );
      return response;
    } catch (error) {

      throw Exception('Error occurred');
    }
  }
}
