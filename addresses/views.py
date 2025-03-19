from django.shortcuts import render, redirect

from addresses.models import Address
from users.models import UserProfile


# Create your views here.
def modify_address(request, address_id):
    address = Address.objects.get(id=address_id)
    user_id = address.user.id
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        province_1 = request.POST.get('province')
        city_1 = request.POST.get('city')
        district_1 = request.POST.get('district')
        detail = request.POST.get('detail')

        address.receiver_name = name
        address.receiver_phone = phone
        address.province = province_1
        address.city = city_1
        address.district = district_1
        address.detail_address = detail
        address.save()
        return redirect('profiles', id=user_id)
    return render(request, 'modify_address.html', {'address': address, 'user_id': user_id})


def add_address(request, id=None):
    if id is None:
        id = request.user.id
    if request.method == 'POST':
        userprofile = UserProfile.objects.get(user_id=id)
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        province_1 = request.POST.get('province')
        city_1 = request.POST.get('city')
        district_1 = request.POST.get('district')
        detail = request.POST.get('detail')

        address = Address.objects.create(receiver_name=name,
                                         receiver_phone=phone,
                                         province=province_1,
                                         city=city_1,
                                         district=district_1,
                                         detail_address=detail,
                                         user=request.user,
                                         is_default=True)

        return redirect("profiles", id=id)

    return render(request, 'add_address.html', {'id': id})


def delete_address(request, address_id):
    address = Address.objects.get(id=address_id)
    user_id = address.user.id
    address.delete()
    return redirect("profiles", id=user_id)
