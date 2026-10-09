from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import Task
from .pagination import TaskPagination
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by("-created_at", "-id")
    serializer_class = TaskSerializer
    pagination_class = TaskPagination

    def get_queryset(self):
        queryset = self.queryset
        completed = self.request.query_params.get("completed")
        if completed is None:
            return queryset

        value = completed.strip().lower()
        true_values = {"true", "1", "yes", "on"}
        false_values = {"false", "0", "no", "off"}
        if value not in true_values | false_values:
            raise ValidationError({"completed": "Use true or false."})
        return queryset.filter(completed=value in true_values)