from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from decimal import Decimal

from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile
from recipes.models import Recipe

import json
import time


class StripeWH_Handler:
    """ Handle Stripe webhooks """

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """ Send the user a confirmation email """
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email],
        )

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment intent succeeded webhook event
        """
        intent = event.data.object
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        stripe_discount = intent.metadata.discount
        stripe_discount_float = float(stripe_discount)
        discount_rounded = round(stripe_discount_float, 2)
        discount = Decimal(discount_rounded).quantize(Decimal('.01'))

        first_recipe = intent.metadata.first_recipe

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount/100, 2)

        # Clean data in the shipping fields
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        # Update profile information if save_info was checked
        profile = None
        username = intent.metadata.username
        if username != 'AnonymousUser':
            profile = UserProfile.objects.get(user__username=username)
            if save_info:
                profile.default_phone_number__iexact = shipping_details.phone
                profile.default_country__iexact = (shipping_details.
                                                   address.country)
                profile.default_postcode__iexact = (shipping_details.
                                                    address.postal_code)
                profile.default_town_or_city__iexact = (shipping_details.
                                                        address.city)
                profile.default_street_address1__iexact = (shipping_details.
                                                           address.line1)
                profile.default_street_address2__iexact = (shipping_details.
                                                           address.line2)
                profile.default_county__iexact = shipping_details.address.state
                profile.save()

        order_exists = False
        attempt = 1
        while attempt < 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    town_or_city__iexact=shipping_details.address.city,
                    county__iexact=shipping_details.address.state,
                    postcode__iexact=shipping_details.address.postal_code,
                    country__iexact=shipping_details.address.country,
                    grand_total=grand_total,
                    original_bag=bag,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                # Increment attempt by 1, pause for 1 second, try again
                attempt += 1
                time.sleep(1)
        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | \
                    SUCCESS: Verified order already in database',
                status=200)
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    town_or_city=shipping_details.address.city,
                    county=shipping_details.address.state,
                    postcode=shipping_details.address.postal_code,
                    country=shipping_details.address.country,
                    original_bag=bag,
                    stripe_pid=pid,
                    vote_discount_applied=discount,
                )
                if first_recipe != "no_recipe":
                    recipe = Recipe.objects.filter(id=first_recipe)[0]
                    recipe.discount_code = ""
                    recipe.save()

                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for gf_option, quantity in item_data[
                                'diet_requirements'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                diet_option=gf_option
                            )
                            order_line_item.save()

            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | \
                        ERROR: {e}',
                    status=500)

        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | \
                SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment intent payment failed webhook event
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200
        )
