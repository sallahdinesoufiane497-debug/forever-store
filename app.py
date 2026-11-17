from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import sqlite3
from pathlib import Path
from functools import wraps

app = Flask(__name__)
app.secret_key = "salah-forever-2026"
DB_PATH = Path(__file__).with_name("store.db")
ADMIN_PASSWORD = "salah123"
WHATSAPP_NUMBER = "212780034976"

PRODUCTS = [
    {"id": 1, "name": "Forever Active Pro-B", "category": "مكمل غذائي", "price": 483, "image": "/static/p1.jpg", "description": "مكمل غذائي طبيعي على اساس الخمائر اللبنية والزنك. كيعاون على الهضم وكيقوي المناعة. علبة فيها 30 كبسولة.", "tag": "الاكثر طلبا"},
    {"id": 2, "name": "Forever Therm", "category": "حرق و طاقة", "price": 488, "image": "/static/p2.jpg", "description": "مكمل غذائي بالشاي الاخضر، الغوارانا والقهوة الخضراء والفيتامينات. كيعاون على الحرق والطاقة. علبة فيها 60 قرص.", "tag": "الاكثر طلبا"},
    {"id": 3, "name": "Forever Absorbent-C", "category": "فيتامين C", "price": 287, "image": "/static/p3.jpg", "description": "فيتامين C طبيعي مع نخالة الشوفان والاسرولا. كيقوي المناعة والبشرة. علبة فيها 100 قرص.", "tag": "اصلي 100%"},
    {"id": 4, "name": "Forever Aloe Vera Gel", "category": "عصير الالوفيرا", "price": 425, "image": "/static/p4.jpg", "description": "جل الالوفيرا الطبيعي 99.7%، بدون سكر وبدون مواد حافظة. كينقي الجسم وكيعاون على الهضم. قارورة 1 لتر.", "tag": "الاكثر مبيعا"},
    {"id": 5, "name": "Aloe Propolis Creme", "category": "عناية بالبشرة", "price": 322, "image": "/static/p5.jpg", "description": "كريم الالوفيرا والبروبوليس، كيرطب البشرة بعمق وكيغذيها. مناسب لجميع انواع البشرة. 113غ.", "tag": "اصلي 100%"},
]

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT NOT NULL, email TEXT, phone TEXT NOT NULL, city TEXT NOT NULL, address TEXT NOT NULL, items TEXT NOT NULL, total REAL NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
init_db()

BASE = """
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} | SALAH FOREVER</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f6f6f6;color:#1a1a1a;font-family:Arial,Tahoma,sans-serif}
a{text-decoration:none;color:inherit}
.top{background:#111;color:white;padding:16px 5%;display:flex;justify-content:space-between;align-items:center;gap:15px;flex-wrap:wrap;position:sticky;top:0;z-index:10}
.logo{font-size:24px;font-weight:900}.logo span{color:#25D366}
.nav{display:flex;gap:16px;align-items:center}.cart-btn{background:#25D366;padding:9px 16px;border-radius:20px;font-weight:bold;color:white}
.hero{padding:60px 6%;background:linear-gradient(100deg,#000000d9,#00000055),url('https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1800&q=85') center/cover;color:white}
.hero h1{font-size:clamp(30px,5vw,50px);margin:0 0 12px}.hero p{font-size:18px;line-height:1.8;max-width:600px}
.badges{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}.badge{background:white;color:#111;padding:9px 14px;border-radius:20px;font-weight:bold;font-size:14px}
.wrap{max-width:1200px;margin:28px auto;padding:0 18px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:20px}
.card{background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 16px #00000010;transition:.2s}.card:hover{transform:translateY(-4px)}
.card img{width:100%;height:280px;object-fit:cover;background:white}.pad{padding:16px}
.muted{color:#888;font-size:13px}.price{font-weight:900;font-size:22px;margin:10px 0;color:#111}
.btn{display:inline-block;background:#111;color:white;padding:13px 18px;border:0;border-radius:10px;cursor:pointer;font-size:15px;font-weight:bold;text-align:center}
.btn.green{background:#25D366}.btn.full{width:100%}.btn.light{background:#eee;color:#222}
.panel{background:white;border-radius:16px;padding:24px;box-shadow:0 4px 16px #00000010}
.formgrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.formgrid .wide{grid-column:1/-1}
input,select,textarea{padding:13px;border:1px solid #ddd;border-radius:10px;font-size:15px;width:100%;background:white}
.notice{padding:12px;background:#e8f5e9;border-radius:10px;margin:12px 0}
.footer{text-align:center;padding:35px;color:#888;background:white;margin-top:40px;line-height:2}
.row{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
table{width:100%;border-collapse:collapse}td,th{padding:12px;border-bottom:1px solid #eee;text-align:right}
@media(max-width:650px){.formgrid{grid-template-columns:1fr}.hero{padding:40px 6%}}
</style>
</head>
<body>
<header class="top">
<a class="logo" href="{{ url_for('home') }}">SALAH <span>FOREVER</span></a>
<nav class="nav">
<a href="{{ url_for('home') }}">الرئيسية</a>
<a href="{{ url_for('home') }}#products">المنتجات</a>
<a class="cart-btn" href="{{ url_for('cart') }}">السلة ({{ cart_count }})</a>
<a href="{{ url_for('admin') }}">الإدارة</a>
</nav>
</header>
{% with messages = get_flashed_messages() %}
{% if messages %}<div class="wrap">{% for m in messages %}<div class="notice">{{ m }}</div>{% endfor %}</div>{% endif %}
{% endwith %}
{{ body|safe }}
<footer class="footer"><b>SALAH FOREVER</b><br>التوصيل لجميع مدن المغرب | منتجات اصلية 100%<br>واتساب: 0780034976</footer>
</body></html>
"""

def page(title, body, **context):
    from datetime import datetime
    return render_template_string(BASE, title=title, body=body, cart_count=sum(session.get("cart", {}).values()), year=datetime.now().year, **context)

@app.route("/")
def home():
    body = render_template_string("""
    <section class="hero"><h1>صحتك تبدا من هنا</h1><p>منتجات Forever الاصلية 100%، مختارة بعناية. التوصيل لجميع مدن المغرب.</p>
    <div class="badges"><span class="badge">التوصيل لجميع المدن</span><span class="badge">اصلي 100%</span><span class="badge">الدفع عند الاستلام</span></div>
    <p style="margin-top:20px"><a class="btn green" href="#products">تسوق الان</a></p></section>
    <main class="wrap" id="products"><h2>منتجاتنا المختارة</h2><p class="muted">5 منتجات اصلية، اختار اللي عجبك واطلب دابا.</p>
    <div class="grid">{% for p in products %}
    <article class="card"><a href="{{ url_for('product', pid=p.id) }}"><img src="{{ p.image }}" alt="{{ p.name }}"></a>
    <div class="pad"><div class="muted">{{ p.category }} | {{ p.tag }}</div><h3 style="margin:6px 0">{{ p.name }}</h3><div>اصلي 100%</div><div class="price">{{ p.price }} درهم</div><a class="btn full" href="{{ url_for('product', pid=p.id) }}">شوف التفاصيل</a></div></article>
    {% endfor %}</div></main>
    """, products=PRODUCTS)
    return page("الرئيسية", body)

@app.route("/product/<int:pid>")
def product(pid):
    p = next((x for x in PRODUCTS if x["id"] == pid), None)
    if not p: return "Product not found", 404
    body = render_template_string("""
    <main class="wrap"><div class="panel row" style="align-items:flex-start">
    <img src="{{ p.image }}" alt="{{ p.name }}" style="width:min(100%,440px);border-radius:12px">
    <div style="flex:1;min-width:260px"><div class="muted">{{ p.category }}</div><h1 style="margin:8px 0">{{ p.name }}</h1>
    <div class="price">{{ p.price }} درهم</div>
    <p>منتج اصلي 100%<br>التوصيل لجميع مدن المغرب<br>الدفع عند الاستلام</p>
    <p style="line-height:1.8">{{ p.description }}</p>
    <form method="post" action="{{ url_for('add_to_cart', pid=p.id) }}">
    <p><label>شحال بغيتي؟</label><select name="quantity"><option value="1">1 قطعة</option><option value="2">2 قطع</option><option value="3">3 قطع</option><option value="4">4 قطع</option></select></p>
    <button class="btn green full">زيد للسلة</button>
    </form>
    <p style="margin-top:12px"><a class="btn light full" href="https://wa.me/{{ whatsapp }}?text=سلام، بغيت نسول على {{ p.name }}" target="_blank">سولنا فواتساب</a></p>
    </div></div></main>
    """, p=p, whatsapp=WHATSAPP_NUMBER)
    return page(p["name"], body)

@app.post("/add/<int:pid>")
def add_to_cart(pid):
    if not any(p["id"] == pid for p in PRODUCTS):
        return redirect(url_for("home"))
    cart = session.get("cart", {})
    key = f"{pid}"
    try: qty = max(1, min(10, int(request.form.get("quantity", 1))))
    except: qty = 1
    cart[key] = cart.get(key, 0) + qty
    session["cart"] = cart
    flash("تزاد المنتج للسلة بنجاح")
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    cart = session.get("cart", {})
    rows, total = [], 0
    for key, qty in cart.items():
        p = next((x for x in PRODUCTS if x["id"] == int(key)), None)
        if p:
            subtotal = p["price"] * qty; total += subtotal
            rows.append({"name": p["name"], "price": p["price"], "qty": qty, "subtotal": subtotal, "key": key, "image": p["image"]})
    body = render_template_string("""
    <main class="wrap"><h1>سلة المشتريات</h1><div class="panel">
    {% if rows %}<table><tr><th>المنتج</th><th>الثمن</th><th>الكمية</th><th>المجموع</th><th></th></tr>
    {% for r in rows %}<tr><td><div class="row"><img src="{{ r.image }}" style="width:55px;height:55px;object-fit:cover;border-radius:8px"><b>{{ r.name }}</b></div></td><td>{{ r.price }} د.م</td><td>{{ r.qty }}</td><td>{{ r.subtotal }} د.م</td><td><a href="{{ url_for('remove_from_cart', key=r.key) }}" style="color:red">حيد</a></td></tr>{% endfor %}</table>
    <h2>المجموع: {{ total }} درهم</h2><p>مصاريف التوصيل كتحدد حسب المدينة وكيخلصها الزبون.</p><a class="btn green" href="{{ url_for('checkout') }}">كمل الطلب</a> <a class="btn light" href="{{ url_for('home') }}">زيد تسوق</a>
    {% else %}<p>السلة خاوية دابا.</p><a class="btn" href="{{ url_for('home') }}">شوف المنتجات</a>{% endif %}
    </div></main>
    """, rows=rows, total=total)
    return page("السلة", body)

@app.route("/remove/<path:key>")
def remove_from_cart(key):
    cart = session.get("cart", {})
    cart.pop(key, None)
    session["cart"] = cart
    flash("تحيد المنتج من السلة")
    return redirect(url_for("cart"))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = session.get("cart", {})
    if not cart:
        flash("السلة خاوية.")
        return redirect(url_for("home"))
    rows, total = [], 0
    for key, qty in cart.items():
        p = next((x for x in PRODUCTS if x["id"] == int(key)), None)
        if p:
            total += p["price"] * qty
            rows.append(f'{p["name"]} x{qty}')
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        city = request.form.get("city", "").strip()
        address = request.form.get("address", "").strip()
        if not all([name, phone, city, address]):
            flash("عمر جميع الخانات من فضلك.")
        else:
            with db() as con:
                cur = con.execute("INSERT INTO orders (customer_name,email,phone,city,address,items,total) VALUES (?,?,?,?,?,?,?)", (name, email, phone, city, address, "\\n".join(rows), total))
                order_id = cur.lastrowid
            session["cart"] = {}
            return redirect(url_for("success", order_id=order_id))
    body = render_template_string("""
    <main class="wrap"><h1>معلومات التوصيل</h1><div class="panel"><p>المجموع: <b>{{ total }} درهم</b> + مصاريف التوصيل حسب المدينة</p>
    <form method="post" class="formgrid">
    <div><label>الاسم الكامل *</label><input name="name" placeholder="مثال: صلاح العلوي" required></div>
    <div><label>رقم الهاتف *</label><input name="phone" type="tel" placeholder="07 80 03 49 76" required></div>
    <div><label>الايميل</label><input name="email" type="email" placeholder="example@gmail.com"></div>
    <div><label>المدينة *</label><input name="city" placeholder="طنجة" required></div>
    <div class="wide"><label>فين ساكن بالضبط؟ الحي، الزنقة، رقم العمارة *</label><textarea name="address" rows="3" placeholder="مثال: حي...، زنقة...، عمارة رقم..." required></textarea></div>
    <div class="wide"><button class="btn green full">اكد الطلب - الدفع عند الاستلام</button></div>
    </form><p class="muted">غادي نعيطو ليك فالنمرة ديالك باش ناكدو الطلب.</p></div></main>
    """, total=total)
    return page("اتمام الطلب", body)

@app.route("/success/<int:order_id>")
def success(order_id):
    body = f'<main class="wrap"><div class="panel" style="text-align:center"><h1>شكرا على طلبك!</h1><p>رقم الطلب ديالك هو <b>#{order_id}</b>.</p><p>التوصيل لجميع مدن المغرب.<br>غادي نتواصلو معاك قريبا باش ناكدو الطلب.</p><a class="btn" href="/">رجع للمتجر</a> <a class="btn green" href="https://wa.me/{WHATSAPP_NUMBER}?text=سلام، بغيت ناكد الطلب رقم {order_id}" target="_blank">اكد فواتساب</a></div></main>'
    return page("تم الطلب", body)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"): return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
        flash("كلمة السر غير صحيحة.")
    body = """<main class="wrap"><div class="panel" style="max-width:420px;margin:auto"><h1>دخول الادارة</h1>
    <form method="post"><input type="password" name="password" placeholder="كلمة سر الادارة" required><p><button class="btn full">دخول</button></p></form></div></main>"""
    return page("دخول الادارة", body)

@app.route("/admin")
@admin_required
def admin():
    with db() as con:
        orders = con.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    body = render_template_string("""
    <main class="wrap"><div class="row" style="justify-content:space-between"><h1>لوحة الادارة</h1><a class="btn light" href="{{ url_for('admin_logout') }}">خروج</a></div>
    <div class="panel"><h2>الطلبات ({{ orders|length }})</h2>{% if orders %}<table><tr><th>رقم</th><th>الزبون</th><th>الهاتف</th><th>المدينة</th><th>المجموع</th><th>التاريخ</th></tr>
    {% for o in orders %}<tr><td>#{{ o.id }}</td><td>{{ o.customer_name }}</td><td>{{ o.phone }}</td><td>{{ o.city }}</td><td>{{ o.total }} د.م</td><td>{{ o.created_at }}</td></tr><tr><td colspan="6"><b>الايميل:</b> {{ o.email }}<br><b>العنوان:</b> {{ o.address }}<br><b>المنتجات:</b><pre>{{ o.items }}</pre></td></tr>{% endfor %}</table>{% else %}<p>ما كاين حتى طلب دابا.</p>{% endif %}</div></main>
    """, orders=orders)
    return page("الادارة", body)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)