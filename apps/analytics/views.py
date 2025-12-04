from rest_framework import views, response, permissions


class AnalyticsOverview(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return response.Response({"status": "ok"})
