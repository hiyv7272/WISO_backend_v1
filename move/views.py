import json

from django.http import JsonResponse
from django.views import View
from user.utils import login_decorator, sms_service

from move.models import MoveReservation, MoveCategory


class MoveReserve(View):
    @login_decorator
    def post(self, request):
        """Move Reserve POST

            이사 예약

            Authors:
                Inyong Hwang <hiyv7272@gmail.com>

            params:
                - **kwargs

            Response:
                - 200
                - 400

            return:
                - {"message": "SUCCESS"}

            History:
                - [2020-07-28 황인용] refactoring
        """
        data = json.loads(request.body)

        if int(data['move_category_id']) > 3:
            return JsonResponse({'message': 'please choose between three options'})
        if len(data['mobile_number']) != 11:
            return JsonResponse({'message': 'INVALID_PHONE_NUMBER'}, status=400)

        try:
            MoveReservation(
                USER_id=request.user.id,
                MOVE_CATEGORY_id=data['move_category_id'],
                address=data['address'],
                mobile_number=data['mobile_number'],
            ).save()

            user_data = dict()
            user_data['mobile_number'] = data['mobile_number']
            user_data['address'] = data['address']
            sms_service(user_data)

            return JsonResponse({'message': 'SUCCESS'}, status=200)

        except TypeError:
            return JsonResponse({'message': 'FAILED_HASHED'}, status=400)
        except KeyError:
            return JsonResponse({'message': 'INVALID_KEYS'}, status=400)
        except ValueError:
            return JsonResponse({'message': 'INVALID_VALUE'}, status=400)

    @login_decorator
    def get(self, request):
        """Move Reserve GET

            이사 예약 확인

            Authors:
                Inyong Hwang <hiyv7272@gmail.com>

            params:
                - **kwargs

            Response:
                - 200
                - 400

            return:
                - dict
                {
                    "move_orders": [{
                        "id": 3,
                        "name": "pang",
                        "move_category": "사무실이사",
                        "addresss": "서울시 송파구",
                        "phone_number": "01033334444"
                    }]

                }

            History:
                - [2020-07-28 황인용] refactoring
        """
        move_user = MoveReservation.objects.select_related(
            'USER',
            'MOVE_CATEGORY').filter(USER_id=request.user.id).order_by('id')

        try:
            move_orders = list()

            for result in move_user:
                dict_data = dict()
                dict_data['id'] = result.id
                dict_data['name'] = result.USER.name
                dict_data['move_category'] = result.MOVE_CATEGORY.name
                dict_data['address'] = result.address
                dict_data['phone_number'] = result.mobile_number

                move_orders.append(dict_data)

            return JsonResponse({"move_orders": move_orders}, status=200)
        except KeyError:
            return JsonResponse({"message": "INVALID_KEY"}, status=401)


class MoveCategoryInfo(View):
    def get(self, request):
        """Move Category GET

            이사 종류

            Authors:
                Inyong Hwang <hiyv7272@gmail.com>

            params:
                - **kwargs

            Response:
                - 200

            return:
                - dict
                {
                    "move_categories": [
                        {
                            "id": 1,
                            "name": "가정이사"
                        },
                        {
                            "id": 3,
                            "name": "사무실이사"
                        },
                        {
                            "id": 2,
                            "name": "소형이사"
                        }
                    ]
                }

            History:
                - [2020-07-28 황인용] refactoring
        """
        move_categories = list(MoveCategory.objects.values())

        return JsonResponse({'move_categories': move_categories}, status=200)
