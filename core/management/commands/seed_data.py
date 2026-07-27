from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Category, Product, Wishlist, Review
from cart.models import Coupon
from orders.models import Order, OrderItem, Payment
from accounts.models import UserProfile, Address
from decimal import Decimal
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Seeds Savo Mart supermarket with realistic categories, products, coupons, and demo users.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting Savo Mart database seeding...'))

        # 1. Create Admin & Demo Customer Users
        admin_user, created_admin = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@savomart.com',
                'first_name': 'Savo',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created_admin:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created Admin user: admin / admin123'))

        demo_user, created_user = User.objects.get_or_create(
            username='user',
            defaults={
                'email': 'customer@savomart.com',
                'first_name': 'Rahul',
                'last_name': 'Sharma',
            }
        )
        if created_user:
            demo_user.set_password('user123')
            demo_user.save()
            Address.objects.create(
                user=demo_user,
                title='HOME',
                recipient_name='Rahul Sharma',
                phone='+91 98765 43210',
                street_address='Flat 402, Green Valley Apartments, MG Road',
                city='Bengaluru',
                state='Karnataka',
                postal_code='560001',
                is_default=True
            )
            self.stdout.write(self.style.SUCCESS('Created Customer user: user / user123'))

        # 2. Categories
        categories_data = [
            {
                'name': 'Fruits & Vegetables',
                'icon': 'fa-apple-whole',
                'image_url': 'https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=600&q=80',
                'description': 'Farm-fresh organic fruits, green leafy vegetables, and seasonal produce delivered daily.',
                'is_featured': True,
                'order': 1
            },
            {
                'name': 'Dairy & Eggs',
                'icon': 'fa-cow',
                'image_url': 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?auto=format&fit=crop&w=600&q=80',
                'description': 'Fresh milk, farm eggs, artisan butter, cheese, ghee, and probiotic yogurt.',
                'is_featured': True,
                'order': 2
            },
            {
                'name': 'Bakery & Bread',
                'icon': 'fa-bread-slice',
                'image_url': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=600&q=80',
                'description': 'Oven-fresh artisan bread, croissants, muffins, whole wheat buns, and cakes.',
                'is_featured': True,
                'order': 3
            },
            {
                'name': 'Snacks & Munchies',
                'icon': 'fa-cookie',
                'image_url': 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?auto=format&fit=crop&w=600&q=80',
                'description': 'Crispy chips, roasted nuts, healthy granola bars, chocolates, and cookies.',
                'is_featured': True,
                'order': 4
            },
            {
                'name': 'Beverages',
                'icon': 'fa-glass-water',
                'image_url': 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=600&q=80',
                'description': 'Fresh cold-pressed juices, sparkling water, herbal tea, coffee beans, and sodas.',
                'is_featured': True,
                'order': 5
            },
            {
                'name': 'Frozen Foods',
                'icon': 'fa-snowflake',
                'image_url': 'https://images.unsplash.com/photo-1585238342024-78d387f4a707?auto=format&fit=crop&w=600&q=80',
                'description': 'Ready-to-cook frozen snacks, french fries, frozen veggies, and gourmet ice cream.',
                'is_featured': True,
                'order': 6
            },
            {
                'name': 'Household Essentials',
                'icon': 'fa-spray-can-sparkles',
                'image_url': 'https://images.unsplash.com/photo-1585421514284-efb74c2b69ba?auto=format&fit=crop&w=600&q=80',
                'description': 'Detergents, surface cleaners, dishwashing liquids, paper towels, and trash bags.',
                'is_featured': False,
                'order': 7
            },
            {
                'name': 'Personal Care',
                'icon': 'fa-pump-soap',
                'image_url': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80',
                'description': 'Organic soaps, herbal shampoos, toothpaste, skin moisturizers, and hygiene care.',
                'is_featured': False,
                'order': 8
            },
        ]

        cat_objs = {}
        for cdata in categories_data:
            cat, _ = Category.objects.get_or_create(
                name=cdata['name'],
                defaults=cdata
            )
            cat_objs[cdata['name']] = cat
        self.stdout.write(self.style.SUCCESS(f'Created {len(cat_objs)} categories.'))

        # 3. Products
        products_data = [
            # Fruits & Veggies
            {
                'name': 'Organic Cavendish Bananas',
                'category': cat_objs['Fruits & Vegetables'],
                'short_description': 'Sweet, rich in potassium, 100% organic farm fresh bananas.',
                'description': 'Sourced directly from certified organic farms. Sweet, creamy, and packed with essential nutrients and dietary fiber.',
                'price': Decimal('60.00'),
                'discount_price': Decimal('48.00'),
                'unit': '1 Bunch (approx 1 kg)',
                'image_url': 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=600&q=80',
                'stock': 85,
                'rating': Decimal('4.80'),
                'review_count': 42,
                'is_featured': True,
                'is_best_seller': True,
                'is_organic': True
            },
            {
                'name': 'Fresh Royal Gala Apples',
                'category': cat_objs['Fruits & Vegetables'],
                'short_description': 'Crisp, juicy red Gala apples imported fresh.',
                'description': 'Crisp texture with a naturally sweet floral flavor. Perfect for snacking, salads, or homemade apple pie.',
                'price': Decimal('180.00'),
                'discount_price': Decimal('149.00'),
                'unit': '4 Pcs (approx 600g)',
                'image_url': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=600&q=80',
                'stock': 60,
                'rating': Decimal('4.70'),
                'review_count': 28,
                'is_featured': True,
                'is_best_seller': True,
                'is_organic': False
            },
            {
                'name': 'Farm Fresh Hass Avocados',
                'category': cat_objs['Fruits & Vegetables'],
                'short_description': 'Rich, creamy Hass avocados ready to eat.',
                'description': 'Loaded with healthy monounsaturated fats and vitamins. Ideal for guacamole, toast spreads, and fresh salads.',
                'price': Decimal('220.00'),
                'discount_price': Decimal('185.00'),
                'unit': '2 Pcs',
                'image_url': 'https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?auto=format&fit=crop&w=600&q=80',
                'stock': 40,
                'rating': Decimal('4.90'),
                'review_count': 56,
                'is_featured': True,
                'is_best_seller': True,
                'is_organic': True
            },
            {
                'name': 'Organic Hydroponic Spinach',
                'category': cat_objs['Fruits & Vegetables'],
                'short_description': 'Tender, washed organic spinach leaves.',
                'description': 'Pesticide-free hydroponically grown baby spinach. Nutrient dense and triple washed, ready to cook or blend into smoothies.',
                'price': Decimal('45.00'),
                'discount_price': Decimal('35.00'),
                'unit': '250 g Pack',
                'image_url': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=600&q=80',
                'stock': 70,
                'rating': Decimal('4.60'),
                'review_count': 19,
                'is_featured': False,
                'is_best_seller': False,
                'is_organic': True
            },
            {
                'name': 'Fresh Red Tomatoes',
                'category': cat_objs['Fruits & Vegetables'],
                'short_description': 'Ripe, juicy local vine tomatoes.',
                'description': 'Sun-ripened tomatoes sourced daily from local farmers. Great for curry bases, salads, and fresh salsa.',
                'price': Decimal('38.00'),
                'discount_price': None,
                'unit': '1 kg',
                'image_url': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=600&q=80',
                'stock': 120,
                'rating': Decimal('4.50'),
                'review_count': 35,
                'is_featured': False,
                'is_best_seller': True,
                'is_organic': False
            },

            # Dairy & Eggs
            {
                'name': 'Farm Fresh Pasteurized Whole Milk',
                'category': cat_objs['Dairy & Eggs'],
                'short_description': '100% pure cow milk with rich cream.',
                'description': 'Homogenized and pasteurized farm fresh milk delivered within hours of milking. Rich in calcium and protein.',
                'price': Decimal('70.00'),
                'discount_price': Decimal('62.00'),
                'unit': '1 Liter Bottle',
                'image_url': 'https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&w=600&q=80',
                'stock': 100,
                'rating': Decimal('4.90'),
                'review_count': 88,
                'is_featured': True,
                'is_best_seller': True,
                'is_organic': True
            },
            {
                'name': 'Greek Style Natural Yogurt',
                'category': cat_objs['Dairy & Eggs'],
                'short_description': 'Thick, high-protein probiotic yogurt.',
                'description': 'Strained authentic Greek yogurt with zero added sugar. High in probiotic cultures for digestive wellness.',
                'price': Decimal('130.00'),
                'discount_price': Decimal('110.00'),
                'unit': '400 g Tub',
                'image_url': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=600&q=80',
                'stock': 50,
                'rating': Decimal('4.85'),
                'review_count': 31,
                'is_featured': True,
                'is_best_seller': False,
                'is_organic': True
            },
            {
                'name': 'Organic Brown Farm Eggs',
                'category': cat_objs['Dairy & Eggs'],
                'short_description': 'Free-range organic brown eggs rich in Omega-3.',
                'description': 'From free-range hens fed a 100% vegetarian diet. Rich orange yolks, high protein, and antibiotic-free.',
                'price': Decimal('120.00'),
                'discount_price': Decimal('99.00'),
                'unit': '6 Eggs Pack',
                'image_url': 'https://images.unsplash.com/photo-1516467508483-a7212febe31a?auto=format&fit=crop&w=600&q=80',
                'stock': 75,
                'rating': Decimal('4.90'),
                'review_count': 64,
                'is_featured': True,
                'is_best_seller': True,
                'is_organic': True
            },

            # Bakery
            {
                'name': 'Artisan Whole Wheat Sourdough Bread',
                'category': cat_objs['Bakery & Bread'],
                'short_description': 'Freshly baked sourdough with a crisp crust.',
                'description': 'Handcrafted sourdough fermented naturally over 24 hours. Crusty exterior with a light, chewy crumb inside.',
                'price': Decimal('150.00'),
                'discount_price': Decimal('125.00'),
                'unit': '1 Loaf (400g)',
                'image_url': 'https://images.unsplash.com/photo-1586444248902-2f64eddc13df?auto=format&fit=crop&w=600&q=80',
                'stock': 30,
                'rating': Decimal('4.88'),
                'review_count': 45,
                'is_featured': True,
                'is_best_seller': True,
                'is_organic': False
            },
            {
                'name': 'Flaky Butter Croissants',
                'category': cat_objs['Bakery & Bread'],
                'short_description': 'French style butter croissants baked daily.',
                'description': 'Golden, flaky layers made with pure French butter. Heavenly breakfast treat best served warm.',
                'price': Decimal('140.00'),
                'discount_price': Decimal('120.00'),
                'unit': '2 Pcs Pack',
                'image_url': 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=600&q=80',
                'stock': 25,
                'rating': Decimal('4.75'),
                'review_count': 22,
                'is_featured': False,
                'is_best_seller': False,
                'is_organic': False
            },

            # Snacks
            {
                'name': 'Roasted Himalayan Salted Almonds',
                'category': cat_objs['Snacks & Munchies'],
                'short_description': 'Crunchy almonds lightly salted with Pink Salt.',
                'description': 'Premium California almonds dry-roasted to perfection and seasoned with authentic Pink Himalayan salt.',
                'price': Decimal('320.00'),
                'discount_price': Decimal('275.00'),
                'unit': '200 g Pack',
                'image_url': 'https://images.unsplash.com/photo-1508061252966-f72007804473?auto=format&fit=crop&w=600&q=80',
                'stock': 45,
                'rating': Decimal('4.80'),
                'review_count': 38,
                'is_featured': True,
                'is_best_seller': True,
                'is_organic': True
            },
            {
                'name': 'Dark Chocolate Sea Salt Cookies',
                'category': cat_objs['Snacks & Munchies'],
                'short_description': 'Rich 70% dark chocolate cookies with sea salt flakes.',
                'description': 'Indulgent gourmet cookies baked with Belgian dark chocolate chunks and sprinkled with Maldon sea salt.',
                'price': Decimal('190.00'),
                'discount_price': Decimal('160.00'),
                'unit': '150 g Box',
                'image_url': 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=600&q=80',
                'stock': 35,
                'rating': Decimal('4.92'),
                'review_count': 50,
                'is_featured': True,
                'is_best_seller': True,
                'is_organic': False
            },

            # Beverages
            {
                'name': 'Cold-Pressed Valencia Orange Juice',
                'category': cat_objs['Beverages'],
                'short_description': '100% natural, unpasteurized cold-pressed orange juice.',
                'description': 'Made from 100% pure Valencia oranges. No added sugar, water, or preservatives. Packed with natural Vitamin C.',
                'price': Decimal('160.00'),
                'discount_price': Decimal('135.00'),
                'unit': '500 ml Bottle',
                'image_url': 'https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?auto=format&fit=crop&w=600&q=80',
                'stock': 50,
                'rating': Decimal('4.85'),
                'review_count': 29,
                'is_featured': True,
                'is_best_seller': True,
                'is_organic': True
            },
            {
                'name': 'Organic Chamomile Green Tea Bags',
                'category': cat_objs['Beverages'],
                'short_description': 'Soothing herbal tea infused with whole chamomile flowers.',
                'description': 'Single-origin green tea leaves blended with whole Egyptian chamomile blossoms. Calming and refreshing.',
                'price': Decimal('240.00'),
                'discount_price': Decimal('199.00'),
                'unit': '25 Tea Bags',
                'image_url': 'https://images.unsplash.com/photo-1597481499750-3e6b22637e12?auto=format&fit=crop&w=600&q=80',
                'stock': 60,
                'rating': Decimal('4.70'),
                'review_count': 17,
                'is_featured': False,
                'is_best_seller': False,
                'is_organic': True
            },

            # Frozen Foods
            {
                'name': 'Crispy Golden Potato French Fries',
                'category': cat_objs['Frozen Foods'],
                'short_description': 'Ready-to-fry golden potato fries.',
                'description': 'Crispy outside, fluffy inside. Flash frozen to retain freshness. Bake or deep fry in minutes.',
                'price': Decimal('175.00'),
                'discount_price': Decimal('145.00'),
                'unit': '750 g Pack',
                'image_url': 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=600&q=80',
                'stock': 40,
                'rating': Decimal('4.65'),
                'review_count': 33,
                'is_featured': False,
                'is_best_seller': True,
                'is_organic': False
            },

            # Household & Personal
            {
                'name': 'Eco-Friendly Plant Soap Cleaner',
                'category': cat_objs['Household Essentials'],
                'short_description': 'Non-toxic citrus multi-surface cleaner.',
                'description': 'Plant-derived cleaning formula safe for kids and pets. Tough on grease and grime with a natural lemon aroma.',
                'price': Decimal('210.00'),
                'discount_price': Decimal('180.00'),
                'unit': '500 ml Spray',
                'image_url': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=600&q=80',
                'stock': 55,
                'rating': Decimal('4.78'),
                'review_count': 26,
                'is_featured': False,
                'is_best_seller': False,
                'is_organic': True
            },
            {
                'name': 'Herbal Honey & Oats Moisturizing Body Wash',
                'category': cat_objs['Personal Care'],
                'short_description': 'Hydrating organic body wash for sensitive skin.',
                'description': 'Infused with real wildflower honey and colloidal oatmeal. Sulfate-free formula that nourishes and soothes skin.',
                'price': Decimal('290.00'),
                'discount_price': Decimal('245.00'),
                'unit': '300 ml Bottle',
                'image_url': 'https://images.unsplash.com/photo-1608248597261-833257647009?auto=format&fit=crop&w=600&q=80',
                'stock': 45,
                'rating': Decimal('4.88'),
                'review_count': 41,
                'is_featured': False,
                'is_best_seller': True,
                'is_organic': True
            },
        ]

        p_count = 0
        for pdata in products_data:
            p, created = Product.objects.get_or_create(
                name=pdata['name'],
                defaults=pdata
            )
            if created:
                p_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {p_count} products.'))

        # 4. Coupons
        Coupon.objects.get_or_create(
            code='FRESH10',
            defaults={
                'discount_percent': Decimal('10.00'),
                'max_discount': Decimal('150.00'),
                'min_order_amount': Decimal('300.00'),
                'is_active': True
            }
        )
        Coupon.objects.get_or_create(
            code='SAVO20',
            defaults={
                'discount_percent': Decimal('20.00'),
                'max_discount': Decimal('300.00'),
                'min_order_amount': Decimal('600.00'),
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('Created coupons: FRESH10 and SAVO20'))

        # 5. Sample Order for demo tracking
        sample_order, o_created = Order.objects.get_or_create(
            order_number='SAVO-884219',
            defaults={
                'user': demo_user,
                'full_name': 'Rahul Sharma',
                'email': 'customer@savomart.com',
                'phone': '+91 98765 43210',
                'shipping_address': 'Flat 402, Green Valley Apartments, MG Road',
                'city': 'Bengaluru',
                'state': 'Karnataka',
                'postal_code': '560001',
                'delivery_slot': 'Standard Delivery (Today within 2 hrs)',
                'payment_method': 'UPI',
                'payment_status': 'PAID',
                'order_status': 'OUT_FOR_DELIVERY',
                'subtotal': Decimal('640.00'),
                'discount_amount': Decimal('64.00'),
                'delivery_fee': Decimal('0.00'),
                'tax_amount': Decimal('32.00'),
                'grand_total': Decimal('608.00'),
                'tracking_note': 'Delivery Executive Suresh is on his way with your Savo Mart insulated grocery bag.'
            }
        )
        if o_created:
            p1 = Product.objects.filter(name__icontains='Bananas').first()
            p2 = Product.objects.filter(name__icontains='Avocados').first()
            p3 = Product.objects.filter(name__icontains='Sourdough').first()
            
            if p1:
                OrderItem.objects.create(order=sample_order, product=p1, product_name=p1.name, product_image=p1.image_url, unit=p1.unit, price=p1.effective_price, quantity=2, total_price=p1.effective_price * 2)
            if p2:
                OrderItem.objects.create(order=sample_order, product=p2, product_name=p2.name, product_image=p2.image_url, unit=p2.unit, price=p2.effective_price, quantity=1, total_price=p2.effective_price)
            if p3:
                OrderItem.objects.create(order=sample_order, product=p3, product_name=p3.name, product_image=p3.image_url, unit=p3.unit, price=p3.effective_price, quantity=2, total_price=p3.effective_price * 2)

            Payment.objects.create(
                order=sample_order,
                transaction_id='TXN-UPI994821',
                payment_method='UPI',
                amount=Decimal('608.00'),
                status='SUCCESS'
            )
            self.stdout.write(self.style.SUCCESS('Created sample tracking order SAVO-884219.'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
