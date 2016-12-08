/* global Vue2 */
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
Vue.component('store-product', {
    props: {
        product: Object
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
    template: "\n    <li class=\"product\">\n        <div class=\"pull-left\">\n            <img :src=\"product.imagefile_thumbnail_url\" width=\"48\" height=\"48\" />\n            {{ product.name }} ({{ product.price.toFixed(0) }} \u20AC)\n            <p class=\"small\" v-if=\"product.description\" v-html=\"product.description\"></p>\n            <p v-if=\"product.qtyDiscountThresh\">\n                <span class=\"fa fa-check\"/>\n                Buy at least {{ product.qtyDiscountThresh }} and earn a discount!\n            </p>\n        </div>\n        <span class=\"pull-right\">\n            <select v-if=\"product.variants\" v-model=\"variant\">\n                <option v-for=\"variant in product.variants\" v-bind:value=\"variant\">\n                    {{ variant.title }}\n                </option>\n            </select>\n            <button v-on:click=\"addItem()\">Lis\u00E4\u00E4 <span class=\"fa fa-shopping-cart\"/></button>\n        </span>\n        <span class=\"clearfix\"></span>\n    </li>\n    ",
});
function storeXHR(method, path, data) {
    return new Promise(function (resolve, reject) {
        var xhr = new XMLHttpRequest();
        xhr.onload = function () {
            resolve(JSON.parse(xhr.responseText));
        };
        xhr.onerror = function () {
            reject(xhr.responseText ? JSON.parse(xhr.responseText) : null);
        };
        xhr.open(method, path);
        if (data) {
            xhr.data = JSON.stringify(data);
        }
        xhr.send();
    });
}
var app = new Vue({
    el: '#store',
    data: {
        products: [{
                id: 1,
                title: 'Awesome T-shirt',
                description: 'Instanssi, represent',
                price: 20.00,
                variants: [{
                        id: 1,
                        title: 'Size S'
                    }, {
                        id: 2,
                        title: 'Size M'
                    }, {
                        id: 3,
                        title: 'Size L'
                    }, {
                        id: 4,
                        title: 'Size XL'
                    }]
            }, {
                id: 2,
                title: 'Basic ticket',
                description: 'Gets you through the doors',
                price: 15.00,
                qtyDiscountThresh: 5,
                qtyDiscountFactor: .9
            }, {
                id: 3,
                title: 'Elite ticket',
                description: 'Gets you some more stuff (or not)',
                price: 50.00,
            }],
        items: [],
        totalPrice: 0
    },
    template: "\n<div>\n<h3>Tuotteet</h3>\n<ul class=\"list-unstyled store-items\">\n    <store-product v-for=\"product in products\" :product=\"product\"\n        v-on:addItem=\"addItem\" />\n</ul>\n<h3>Ostoskori</h3>\n<ul class=\"list-unstyled store-items\">\n    <li v-for=\"item in items\">\n        <div class=\"pull-left\">{{ item.product.name }}\n            <span v-if=\"item.variant\">({{ item.variant.name }})</span>\n        </div>\n        <span class=\"pull-right\">\n            x {{ item.count }} = {{ getSubtotal(item) }} \u20AC\n            <button v-on:click=\"changeItemCount(item, 1)\">+</button>\n            <button v-on:click=\"changeItemCount(item, -1)\">-</button>\n            <button v-on:click=\"removeItem(item)\">\n                <span class=\"fa fa-fw fa-trash\"></span>\n            </button>\n        </span>\n        <span class=\"clearfix\"></span>\n    </li>\n    <li>Yhteens\u00E4: {{ totalPrice.toFixed(2) }} \u20AC</li>\n</ul>\n<h3>Tiedot</h3>\n<form class=\"form-horizontal\">\n    <p>Huomaathan, ett\u00E4 lippukoodit l\u00E4hetet\u00E4\u00E4n annettuun s\u00E4hk\u00F6postiosoitteeseen.</p>\n    <div class=\"form-group\">\n        <label class=\"col-sm-4 control-label\">Nimi</label>\n        <div class=\"col-sm-8\">\n            <input class=\"form-control\"></input>\n        </div>\n    </div>\n    <div class=\"form-group\">\n        <label class=\"col-sm-4 control-label\">S\u00E4hk\u00F6posti</label>\n        <div class=\"col-sm-8\">\n            <input class=\"form-control\"></input>\n        </div>\n    </div>\n    <div class=\"form-group\">\n        <label class=\"col-sm-4 control-label\">Katuosoite</label>\n        <div class=\"col-sm-8\">\n            <input class=\"form-control\"></input>\n        </div>\n    </div>\n    <div class=\"form-group\">\n        <label class=\"col-sm-4 control-label\">Postinumero</label>\n        <div class=\"col-sm-8\">\n            <input class=\"form-control\"></input>\n        </div>\n    </div>\n    <div class=\"form-group\">\n        <label class=\"col-sm-4 control-label\">Kaupunki</label>\n        <div class=\"col-sm-8\">\n            <input class=\"form-control\"></input>\n        </div>\n    </div>\n    <div class=\"form-group\">\n        <label class=\"col-sm-4 control-label\">Puhelin</label>\n        <div class=\"col-sm-8\">\n            <input class=\"form-control\"></input>\n        </div>\n    </div>\n    <span class=\"pull-right\">\n        <button class=\"btn btn-primary\">Jatka &gt;</button>\n    </span>\n    <div class=\"clearfix\"></div>\n</form>\n</div>\n  ",
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
    },
    methods: {
        getSubtotal: function (item) {
            var multiplier = 1;
            var qtyThresh = item.product.qtyDiscountThresh;
            var discountFactor = item.product.qtyDiscountFactor;
            if (qtyThresh && item.count >= qtyThresh) {
                multiplier *= discountFactor;
            }
            return item.product.price * item.count * multiplier;
        },
        updateTotal: function () {
            var totalPrice = 0;
            var component = this;
            this.items.forEach(function (item) {
                totalPrice += component.getSubtotal(item);
            });
            this.totalPrice = totalPrice;
        },
        addItem: function (product, variant) {
            // check if product/variant is already in items
            var found = this.items.findIndex(function (item) {
                return item.product.id === product.id && (!variant || (item.variant && (variant.id === item.variant.id)));
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
            this.updateTotal();
        },
        removeItem: function (item) {
            var pos = this.items.indexOf(item);
            this.items.splice(pos, 1);
            this.updateTotal();
        },
        changeItemCount: function (item, change) {
            var pos = this.items.indexOf(item);
            var item = this.items[pos];
            if (item.count + change <= 0) {
                return this.removeItem(item);
            }
            item.count += change;
            this.items.splice(pos, 1, item);
            this.updateTotal();
        }
    }
});
