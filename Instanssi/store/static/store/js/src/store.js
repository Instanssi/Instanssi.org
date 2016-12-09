/* global Vue */

toLocaleStringSupportsOptions = !!(typeof Intl == 'object' && Intl && typeof Intl.NumberFormat == 'function');

function formatPriceLocaleString(price) {
    return price.toLocaleString('fi', { style: 'currency', currency: 'EUR'});
}
function formatPriceLegacy(price) {
    return price.toFixed(2) + ' €';
}
let formatPrice;
if(toLocaleStringSupportsOptions) {
    formatPrice = formatPriceLocaleString;
} else {
    formatPrice = formatPriceLegacy;
}

Vue.filter('formatPrice', formatPrice);

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
        addItem: function() {
            this.$emit('addItem', this.product, this.variant);
        }
    },
    created: function () {
        var product = this.product;
        if (product.variants && product.variants.length) {
            this.variant = product.variants[0];
        }
    },
    template: `
    <div class="product">
        <span class="pull-right">
            <select v-if="product.variants" v-model="variant">
                <option v-for="variant in product.variants" v-bind:value="variant">
                    {{ variant.title }}
                </option>
            </select>
            <button v-on:click="addItem()">Lisää <span class="fa fa-shopping-cart"/></button>
        </span>
        <div>
            <img :src="product.imagefile_thumbnail_url" width="48" height="48" />
            {{ product.name }} ({{ product.price | formatPrice }})
            <p class="small" v-if="product.description" v-html="product.description"></p>
            <p v-if="product.discount_amount > 0">
                <span class="fa fa-info"/>
                {{ product.discount_percentage }} % alennus, jos ostat ainakin {{ product.discount_amount }} kappaletta!
            </p>
        </div>
        <span class="clearfix"></span>
    </div>
    `,
});

function storeXHR(method, path, data) {
    return new Promise((resolve, reject) => {
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
        products: [],
        items: [],
        totalPrice: 0
    },
    template: `
<div>
<h3>Tuotteet</h3>
<div class="list-unstyled store-items">
    <store-product v-for="product in products" :product="product"
        v-on:addItem="addItem" />
</div>
<h3>Ostoskori</h3>
<div class="list-unstyled store-items">
    <div v-for="item in items">
        <div class="pull-left">
            <span>{{ item.product.name }}</span>
            <span v-if="item.variant">({{ item.variant.name }})</span>
        </div>
        <span class="pull-right">
            x {{ item.count }} = {{ getSubtotal(item) | formatPrice }}
            <button v-on:click="changeItemCount(item, 1)">+</button>
            <button v-on:click="changeItemCount(item, -1)">-</button>
            <button v-on:click="removeItem(item)">
                <span class="fa fa-fw fa-trash"></span>
            </button>
        </span>
        <span class="clearfix"></span>
    </div>
    <div>Yhteensä: {{ totalPrice | formatPrice }}</div>
</div>
<h3>Tiedot</h3>
<form class="form-horizontal">
    <p>Huomaathan, että lippukoodit lähetetään annettuun sähköpostiosoitteeseen.</p>
    <div class="form-group">
        <label class="col-sm-4 control-label">Nimi</label>
        <div class="col-sm-8">
            <input class="form-control"></input>
        </div>
    </div>
    <div class="form-group">
        <label class="col-sm-4 control-label">Sähköposti</label>
        <div class="col-sm-8">
            <input class="form-control"></input>
        </div>
    </div>
    <div class="form-group">
        <label class="col-sm-4 control-label">Katuosoite</label>
        <div class="col-sm-8">
            <input class="form-control"></input>
        </div>
    </div>
    <div class="form-group">
        <label class="col-sm-4 control-label">Postinumero</label>
        <div class="col-sm-8">
            <input class="form-control"></input>
        </div>
    </div>
    <div class="form-group">
        <label class="col-sm-4 control-label">Kaupunki</label>
        <div class="col-sm-8">
            <input class="form-control"></input>
        </div>
    </div>
    <div class="form-group">
        <label class="col-sm-4 control-label">Puhelin</label>
        <div class="col-sm-8">
            <input class="form-control"></input>
        </div>
    </div>
    <span class="pull-right">
        <button class="btn btn-primary">Jatka &gt;</button>
    </span>
    <div class="clearfix"></div>
</form>
</div>
  `,
    created: function() {
        storeXHR('GET', '/api/store_items/?format=json').then((items) => {
            items.forEach((item) => {
                item.price = parseFloat(item.price);
            });
            this.products = items;
        }).catch((e) => {
            console.error('error fetching store items:', e);
        });

        // FIXME: Fetch cart from window.localstorage if it exists
    },
    methods: {
        getSubtotal: function(item) {
            var multiplier = 1;
            var qtyThresh = item.product.discount_amount;
            var discountFactor = (100 - item.product.discount_percentage) / 100;
            if(qtyThresh && item.count >= qtyThresh) {
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
                return item.product.id === product.id && (!variant || (item.variant && (variant.id === item.variant.id)));
            });
            if (found >= 0) {
                // if it is, splice a new item with a higher count
                var newItem = Object.assign({}, this.items[found]);
                newItem.count++;
                this.items.splice(found, 1, newItem);
            } else {
                // if it isn't, push a new item
                this.items.push({
                    count: 1,
                    product: product,
                    variant: variant
                });
            }
            this.updateCart();
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
        submit: function() {
            // send request to API, get payment methods, whatever.
            // clear localStorage afterwards
        }
    }
});
