from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.catalog.models import Book
from .models import Loan
from .serializers import LoanSerializer


class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        queryset = Loan.objects.select_related("user", "book").all()
        user = self.request.user

        show_all = self.request.query_params.get("all", "").lower() in ("true", "1", "yes")
        if not (getattr(user, "is_admin_role", False) and show_all):
            queryset = queryset.filter(user=user)

        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        if "book" not in data and "book_id" in data:
            data["book"] = data["book_id"]

        book_id = data.get("book")
        if not book_id:
            return Response(
                {"detail": "Необходимо указать ID книги (book или book_id)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        book = get_object_or_404(Book, pk=book_id)

        if Loan.objects.filter(user=request.user, book=book, status=Loan.STATUS_ACTIVE).exists():
            return Response(
                {"detail": "Эта книга уже находится у вас на руках."},
                status=status.HTTP_409_CONFLICT,
            )

        if book.available_copies <= 0:
            return Response(
                {"detail": "К сожалению, сейчас нет свободных экземпляров этой книги."},
                status=status.HTTP_409_CONFLICT,
            )

        if not data.get("due_at"):
            data["due_at"] = (timezone.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        loan = serializer.save(user=request.user, book=book, status=Loan.STATUS_ACTIVE)

        book.available_copies -= 1
        book.save(update_fields=["available_copies"])

        return Response(self.get_serializer(loan).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        loan = get_object_or_404(Loan.objects.select_related("book", "user"), pk=pk)

        if loan.user_id != request.user.id and not getattr(request.user, "is_admin_role", False):
            return Response(
                {"detail": "Вы не можете вернуть чужую книгу."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if loan.status == Loan.STATUS_RETURNED:
            return Response(
                {"detail": "Эта книга уже была возвращена в библиотеку."},
                status=status.HTTP_409_CONFLICT,
            )

        loan.status = Loan.STATUS_RETURNED
        loan.returned_at = timezone.now()
        loan.save(update_fields=["status", "returned_at"])

        book = loan.book
        if book.available_copies < book.total_copies:
            book.available_copies += 1
        else:
            book.available_copies = book.total_copies
        book.save(update_fields=["available_copies"])

        return Response(self.get_serializer(loan).data, status=status.HTTP_200_OK)
