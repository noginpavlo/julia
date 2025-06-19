# from .models import Deck
# from django.http import JsonResponse
# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from rest_framework import status


# @api_view(["GET"])
# def deck_list(request):
#     if request.user.is_authenticated:
#         decks = Deck.objects.filter(user=request.user)
#         deck_data = [{"id": deck.id, "deck_name": deck.deck_name} for deck in decks]
#         return Response(deck_data)
#     else:
#         return JsonResponse(
#             {"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED
#         )
