/* global Vue */
toLocaleStringSupportsOptions = !!(typeof Intl == 'object' && Intl && typeof Intl.NumberFormat == 'function');
function formatPriceLocaleString(price) {
    return price.toLocaleString('fi', { style: 'currency', currency: 'EUR' });
}
function formatPriceLegacy(price) {
    return price.toFixed(2) + ' €';
}
var formatPrice;
if (toLocaleStringSupportsOptions) {
    formatPrice = formatPriceLocaleString;
}
else {
    formatPrice = formatPriceLegacy;
}
function storeXHR(method, path, data) {
    return new Promise(function (resolve, reject) {
        var xhr = new XMLHttpRequest();
        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(JSON.parse(xhr.responseText));
            }
            else {
                xhr.onerror();
            }
        };
        xhr.onerror = function () {
            reject(xhr.responseText ? JSON.parse(xhr.responseText) : null);
        };
        xhr.open(method, path);
        xhr.setRequestHeader('Accept', 'application/json');
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        xhr.send(data ? JSON.stringify(data) : null);
    });
}
/**
 * Returns true if a cart item is a specific product (and optional variant).
 */
function cartItemEquals(item, product, variant) {
    return item.product.id === product.id && (!variant || (item.variant && (variant.id === item.variant.id)));
}
Vue.filter('formatPrice', formatPrice);
Vue.component('store-messages', {
    props: {
        field: String,
        messages: Object
    },
    computed: {
        localMessages: function () {
            // console.info('get local messages for field', this.field, this.messages);
            var _a = this, messages = _a.messages, field = _a.field;
            if (messages && messages[field] && messages[field].length > 0) {
                // console.info(messages[field]);
                return messages[field];
            }
            return null;
        }
    },
    template: "<div><p v-if=\"localMessages\">\n        <div class=\"alert alert-danger\" role=\"alert\" v-for=\"message in localMessages\">\n            <span class=\"fa fa-times\"></span> {{ message }}\n        </div>\n    </p></div>"
});
Vue.component('store-form-group', {
    props: {
        title: String,
        field: String,
        // type: String,
        messages: Object,
        update: Function,
        data: Object
    },
    methods: {
        onInput: function ($event) {
            this.$emit('update', this.field, $event);
        }
    },
    computed: {
        clazz: function () {
            var _a = this, messages = _a.messages, field = _a.field;
            if (messages && messages[field] && messages[field].length > 0) {
                return 'form-group has-error';
            }
            return 'form-group';
        }
    },
    template: "<div v-bind:class=\"clazz\">\n        <label class=\"col-sm-4 control-label\">{{ title }}</label>\n        <div class=\"col-sm-8\">\n            <input class=\"form-control\" @input=\"onInput\" v-bind:value=\"data[field]\" />\n            <store-messages :field=\"field\" :messages=\"messages\" />\n        </div>\n    </div>"
});
Vue.component('store-information-form', {
    props: {
        /** Field error messages, maps field name -> array */
        messages: Object,
        data: Object
    },
    created: function () {
        this.userInfo = {};
    },
    methods: {
        update: function (fieldName, $event) {
            // console.info('updated!', fieldName, $event.target.value);
            this.data[fieldName] = $event.target.value;
        }
    },
    template: "\n<form class=\"form-horizontal\" @submit.prevent>\n    <p>Huomaathan, ett\u00E4 lippukoodit l\u00E4hetet\u00E4\u00E4n annettuun s\u00E4hk\u00F6postiosoitteeseen.</p>\n    <div class=\"row\"><div class=\"col-lg-6\">\n        <store-form-group title=\"Etunimi\" field=\"first_name\" @update=\"update\" :messages=\"messages\" :data=\"data\" />\n        <store-form-group title=\"Sukunimi\" field=\"last_name\" @update=\"update\" :messages=\"messages\" :data=\"data\" />\n        <store-form-group title=\"S\u00E4hk\u00F6posti\" field=\"email\" @update=\"update\" :messages=\"messages\" :data=\"data\" />\n        <store-form-group title=\"Vahvista s\u00E4hk\u00F6posti\" field=\"email2\" @update=\"update\" :messages=\"messages\" :data=\"data\" />\n        <store-form-group title=\"Matkapuhelin\" field=\"mobile\" @update=\"update\" :messages=\"messages\" :data=\"data\" />\n        <store-form-group title=\"Muu puhelinnumero\" field=\"telephone\" @update=\"update\" :messages=\"messages\" :data=\"data\" />\n    </div>\n    <div class=\"col-lg-6\">\n        <store-form-group title=\"Katuosoite\" field=\"street\" @update=\"update\" :messages=\"messages\" :data=\"data\" />\n        <store-form-group title=\"Postinumero\" field=\"postal_code\" @update=\"update\" :messages=\"messages\" :data=\"data\" />\n        <store-form-group title=\"Kaupunki\" field=\"city\" @update=\"update\" :messages=\"messages\" :data=\"data\" />\n        <store-form-group title=\"Maa\" field=\"country\" @update=\"update\" :messages=\"messages\" :data=\"data\" />\n        <store-form-group title=\"Yritys\" field=\"company\" @update=\"update\" :messages=\"messages\" :data=\"data\" />\n    </div></div>\n    <div class=\"form-group\">\n        <label class=\"col-lg-2 control-label\">Lis\u00E4tietoja</label>\n        <div class=\"col-lg-10\">\n            <textarea class=\"form-control\" @input=\"update('information', $event)\" v-bind:value=\"data.information\"></textarea>\n            <store-messages field=\"information\" :messages=\"messages\" />\n        </div>\n    </div>\n    <div class=\"form-group\">\n        <div class=\"col-sm-12\">\n            <label class=\"control-label\">\n                <input type=\"checkbox\" v-model=\"data.read_terms\" />\n                <span>\n                    Olen lukenut <a target=\"_blank\" href=\"/store/terms\">toimitusehdot</a> ja hyv\u00E4ksyn ne.\n                </span>\n            </label>\n            <store-messages field=\"read_terms\" :messages=\"messages\" />\n        </div>\n    </div>\n    <div class=\"clearfix\"></div>\n</form>\n"
});
Vue.component('store-product', {
    props: {
        product: Object,
        cart: Array,
        messages: Object,
    },
    data: function () {
        return {
            variant: null,
        };
    },
    methods: {
        addItem: function () {
            this.$emit('addItem', this.product, this.variant);
        }
    },
    created: function () {
        var product = this.product;
        if (product.variants && product.variants.length) {
            this.variant = product.variants[0];
        }
    },
    computed: {
        cartCount: function () {
            var product = this.product;
            if (!this.cart) {
                return 0;
            }
            var cartIndex = this.cart.findIndex(function (item) {
                return cartItemEquals(item, product, null);
            });
            if (cartIndex < 0) {
                return 0;
            }
            return this.cart[cartIndex].count;
        }
    },
    template: "\n    <div class=\"product\">\n        <span class=\"pull-right\">\n            <span class=\"product-cart-count\" v-if=\"cartCount > 0\">\n                <span class=\"fa fa-shopping-cart\"></span> {{ cartCount }}\n            </span>\n            <select class=\"product-variants\" v-if=\"product.variants && product.variants.length > 0\" v-model=\"variant\">\n                <option v-for=\"variant in product.variants\" v-bind:value=\"variant\">\n                    {{ variant.title }}\n                </option>\n            </select>\n            <button class=\"btn btn-success\" v-on:click=\"addItem()\">\n                <span class=\"fa fa-plus\" /> Lis\u00E4\u00E4\n            </button>\n        </span>\n        <div>\n            <img :src=\"product.imagefile_thumbnail_url\" width=\"48\" height=\"48\" />\n            {{ product.name }} ({{ product.price | formatPrice }})\n            <p class=\"small\" v-if=\"product.description\" v-html=\"product.description\"></p>\n            <p v-if=\"product.discount_amount > 0\">\n                <span class=\"fa fa-info\"/>\n                {{ product.discount_percentage }} % alennus, jos ostat ainakin {{ product.discount_amount }} kappaletta!\n            </p>\n        </div>\n        <span class=\"clearfix\"></span>\n    </div>\n    ",
});
var app = new Vue({
    el: '#store',
    data: {
        products: [],
        items: [],
        messages: {},
        info: {
            first_name: '',
            last_name: '',
            email: '',
            street: '',
            postal_code: '',
            city: '',
            country: '',
            mobile: '',
            telephone: '',
            company: '',
            information: '',
            read_terms: false
        },
        totalPrice: 0
    },
    template: "\n<div>\n<h3>Tuotteet</h3>\n<div class=\"list-unstyled store-items\">\n    <store-product v-for=\"product in products\"\n        :product=\"product\" :cart=\"items\" :messages=\"messages\"\n        v-on:addItem=\"addItem\" />\n</div>\n<h3>Ostoskori</h3>\n<store-messages field=\"items\" :messages=\"messages\" />\n<div class=\"list-unstyled store-items\">\n    <div v-for=\"item in items\">\n        <div class=\"pull-left\">\n            <span>{{ item.product.name }}</span>\n            <span v-if=\"item.variant\">({{ item.variant.name }})</span>\n        </div>\n        <span class=\"pull-right\">\n            x {{ item.count }} = {{ getSubtotal(item) | formatPrice }}\n            <button class=\"btn btn-secondary\" v-on:click=\"changeItemCount(item, 1)\">+</button>\n            <button class=\"btn btn-secondary\" v-on:click=\"changeItemCount(item, -1)\">-</button>\n            <button class=\"btn btn-danger\" v-on:click=\"removeItem(item)\">\n                <span class=\"fa fa-fw fa-trash\"></span>\n            </button>\n        </span>\n        <span class=\"clearfix\"></span>\n    </div>\n    <div>Yhteens\u00E4: {{ totalPrice | formatPrice }}</div>\n</div>\n<h3>Tiedot</h3>\n<store-information-form v-on:infoUpdate=\"updateInfo\" :data=\"info\" :messages=\"messages\" />\n<span class=\"pull-right\">\n    <button class=\"btn btn-primary\" @click=\"submit\">Jatka &gt;</button>\n</span>\n</div>\n  ",
    created: function () {
        var _this = this;
        storeXHR('GET', '/api/store_items/?format=json').then(function (items) {
            items.forEach(function (item) {
                item.price = parseFloat(item.price);
            });
            _this.products = items;
        }).catch(function (e) {
            console.error('error fetching store items:', e);
        });
        // FIXME: Fetch cart from window.localstorage if it exists
    },
    methods: {
        getSubtotal: function (item) {
            var multiplier = 1;
            var qtyThresh = item.product.discount_amount;
            var discountFactor = (100 - item.product.discount_percentage) / 100;
            if (qtyThresh && item.count >= qtyThresh) {
                multiplier *= discountFactor;
            }
            return item.product.price * item.count * multiplier;
        },
        updateCart: function () {
            var totalPrice = 0;
            var component = this;
            this.items.forEach(function (item) {
                totalPrice += component.getSubtotal(item);
            });
            this.totalPrice = totalPrice;
            // FIXME: Store cart in window.localStorage
        },
        addItem: function (product, variant) {
            // check if product/variant is already in items
            var found = this.items.findIndex(function (item) {
                return cartItemEquals(item, product, variant);
            });
            if (found >= 0) {
                // if it is, splice a new item with a higher count
                var newItem = Object.assign({}, this.items[found]);
                newItem.count++;
                this.items.splice(found, 1, newItem);
            }
            else {
                // if it isn't, push a new item
                this.items.push({
                    count: 1,
                    product: product,
                    variant: variant
                });
            }
            this.updateCart();
        },
        updateInfo: function (info) {
            // Note that this is a shallow copy. Doesn't really harm anything.
            this.userInfo = info;
        },
        removeItem: function (item) {
            var pos = this.items.indexOf(item);
            this.items.splice(pos, 1);
            this.updateCart();
        },
        changeItemCount: function (item, change) {
            // FIXME: Check item product max per order
            var pos = this.items.indexOf(item);
            var item = this.items[pos];
            if (item.count + change <= 0) {
                return this.removeItem(item);
            }
            item.count += change;
            this.items.splice(pos, 1, item);
            this.updateCart();
        },
        submit: function () {
            var _this = this;
            var info = this.info;
            // format store request
            var transaction = Object.assign({}, info);
            transaction.items = this.items.map(function (item) { return ({
                item_id: item.product.id,
                variant_id: item.variant ? item.variant.id : null,
                amount: item.count,
            }); });
            storeXHR('POST', '/api/store_transaction/?format=json', transaction).then(function (res) {
                console.info(res);
            }, function (err) {
                _this.messages = err;
                // Hack error message so both email fields show them.
                if (err) {
                    err.email2 = err.email;
                }
            }).catch(function (err) {
                console.error(err);
            });
        }
    }
});
