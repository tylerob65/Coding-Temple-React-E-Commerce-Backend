from app import app
from app.models import Products, Carts, Users, db
from flask import request
from app.auth_helpers import basic_auth, token_auth


@app.post('/signup')
def signUp():
    data = request.json
    
    # Get data from request
    username = data['username']
    email = data['email']
    first_name = data['first_name']
    last_name = data['last_name']
    password = data['password']
    confirm_password = data['confirm_password']

    if password != confirm_password:
        return {
            'status': 'not ok',
            'message': 'Passwords do not match.'
        }, 400
    
    # See if user exists
    user = Users.query.filter_by(username=username).first()
    if user:
        return {
            'status': 'not ok',
            'message': 'Please choose a different username.'
        }, 400
    
    user = Users.query.filter_by(email=email).first()
    if user:
        return {
            'status': 'not ok',
            'message': 'Please choose a different email.'
        }, 400

    
    # Create a new user
    user = Users(username, email, password, first_name,last_name)
    user.saveToDB()

    return {
        'status': 'ok',
        'message': "You have successfully created an account."
    }, 201

@app.post('/login')
@basic_auth.login_required
def login():
    # user = basic_auth.verify_password()
    return {
        'status': 'ok',
        'message': "You have successfully logged in.",
        'data': basic_auth.current_user().to_dict()
    }, 200


@app.route('/products')
def product_list():
    all_products = Products.query.all()
    return {
        "status":"ok",
        "results":len(all_products),
        "products":[prod.to_dict() for prod in all_products]
    }, 200

@app.route('/product/<int:product_id>')
def productPage(product_id):
    product = Products.query.get(product_id)
    
    return {
        "status":"ok",
        "product_info":product.to_dict()
    },200

@app.post('/additem/<int:product_id>')
@token_auth.login_required
def addItemToCart(product_id):
    product = Products.query.get(product_id)
    if not product:
        return {
            "status":"not ok",
            "message":"product, does not exist"
        }, 400
    
    
    user_id = token_auth.current_user().id
    cart_entry = Carts.query.filter(db.and_(Carts.user_id==user_id,Carts.product_id==product_id)).all()
    

    if not cart_entry:
        new_entry = Carts(user_id,product_id,1)
        new_entry.saveToDB()
    else:
        cart_entry[0].item_quantity += 1
        cart_entry[0].saveToDB()
    
    return {
        "status":"ok",
        "message":"You successfully added to your cart"
    }, 200

@app.post('/removeitem/<int:product_id>')
@token_auth.login_required
def removeItemFromCart(product_id):
    product = Products.query.get(product_id)
    if not product:
        return {
            "status":"not ok",
            "message":"product, does not exist"
        }, 400
    
    user_id = token_auth.current_user().id    
    cart_entry = Carts.query.filter(db.and_(Carts.user_id==user_id,Carts.product_id==product_id)).all()
    
    if not cart_entry:
        return {
            "status":"not ok",
            "message":"Item not in cart, can't delete it"
        }, 400
    
    cart_entry = cart_entry[0]
    cart_quantity = cart_entry.item_quantity
    if cart_quantity == 1:
        cart_entry.deleteFromDB()
        return {
            "status":"ok",
            "message":"You successfully removed from cart"
        }, 200

    else:
        cart_entry.item_quantity -= 1
        cart_entry.saveToDB()
        return {
            "status":"ok",
            "message":"You successfully removed item from cart"
        }, 200

# TODO this is not secure - figure out how to only allow people with carts to see their own cart
@app.route('/mycart/<int:user_id>')
# @token_auth.login_required
def mycart(user_id):
    user = Users.query.get(user_id)
    # user = token_auth.current_user()
    # user_id = user.id

    total_cart_cost = 0
    cart = []
    for cart_item in user.cart_items:
        cart_item_dict = cart_item.makeCartDict()
        cart.append(cart_item_dict)
        total_cart_cost += cart_item_dict["total_item_cost_number"]
    
    return {
        "status":"ok",
        "message":"You successfully loaded your cart",
        "cart":cart,
        "cartTotal":"${:,.2f}".format(total_cart_cost),
    }, 200


@app.post('/emptycart')
@token_auth.login_required
def emptyCart():
    user = token_auth.current_user()
    cart_items = user.cart_items
    for cart_item in cart_items:
        cart_item.deleteFromDB()
    return {
        "status":"ok",
        "message":"You removed all items from cart"
    }, 200

    

# @app.route("/")
# def test():
#     description1 = "Experience the magic of the big screen right from your couch. Every LG OLED comes loaded with Dolby Vision™ for extraordinary color, contrast and brightness, plus Dolby Atmos®³ for wrap-around sound. Land in the center of the action with LG's FILMMAKER MODE™, allowing you to see films just as the director intended."
#     url1 = "https://www.lg.com/us/images/tvs/md08003931/gallery/D-1.jpg"
#     item1 = Products("LG OLED evo C3 65 inch 4K Smart TV 2023",2599.99,description1,url1)
#     item1.saveToDB()


#     description2 = "Enjoy outstanding picture powered by the a7 AI Processor 4K Gen6. Experience everything from movies to sports in vibrant color and incredible depth for an immersive viewing experience."
#     url2 = "https://www.lg.com/us/images/tvs/md08004091/gallery/D-1.jpg"
#     item2 = Products("LG 77 Inch Class B3 series OLED 4K UHD Smart webOS 23 w/ ThinQ AI TV",3299.99,description2,url2)
#     item2.saveToDB()


#     description3 = "Experience our greatest of all time. Samsung's Neo QLED 8K delivers unparalleled picture quality and mind-blowing sound.¹ The powerful processor transforms your favorite content into stunning 8K,² and the smallest details come to life with our iconic Quantum Mini LED technology complemented by lifelike sound with Dolby Atmos, Object Tracking Sound Pro and Symphony 3.0.³"
#     url3 = "https://valueelectronics.com/wp-content/uploads/2023/01/Samsung-QN900C-product-shot.png"
#     item3 = Products('85" Class QN900C Samsung Neo QLED 8K Smart TV (2023)',8000,description3,url3)
#     item3.saveToDB()

#     description4 = "Some TVs just have it. They make everything look good—even hard stuff like 4K upscaling, weird viewing angles and daytime sports. But when it's Samsung Neo QLED 4K we're talking about, there's no need to be jealous. Because—thanks to its brilliant picture, dynamic audio and stellar design—it'll make you look good, too."
#     url4 = "https://image-us.samsung.com/SamsungUS/home/television-home-theater/tvs/03242023/QN90C_85_75_65_55.jpg?$product-details-jpg$"
#     item4 = Products('85" Class QN90C Samsung Neo QLED 4K Smart TV (2023)',8000,description4,url4)
#     item4.saveToDB()
#     user = Users.query.filter_by(email="test@test.com").first()
#     print(user)
#     user.password = generate_password_hash('123')
#     print(user.password)
#     user.saveToDB()
#     return
    