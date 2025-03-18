from django.shortcuts import render, redirect

from addresses.models import Address
from users.models import UserProfile


# Create your views here.
def modify_address(request, address_id):
    address = Address.objects.get(id=address_id)
    consumer_id = address.consumer.user.id
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        province_1 = request.POST.get('province')
        city_1 = request.POST.get('city')
        district_1 = request.POST.get('district')
        detail = request.POST.get('detail')

        address = Address.objects.update(receiver_name=name,
                                         receiver_phone=phone,
                                         province=province_1,
                                         city=city_1,
                                         district=district_1,
                                         detail_address=detail)
        return redirect('modify_address', address_id=address_id)
    return render(request, 'modify_address.html', {'address': address, 'consumer_id': consumer_id})


def add_address(request, id):
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
                                         consumer=userprofile,
                                         is_default=True)

        return redirect("add_address", id=id)

    return render(request, 'add_address.html', {'id': id})


def delete_address(request, address_id):
    address = Address.objects.get(id=address_id)
    address.is_default = False
    address.save()
    consumer_id = address.consumer.user.id
    return redirect("profiles", id=consumer_id)
