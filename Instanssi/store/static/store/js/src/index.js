import Vue from 'vue';
import { formatPrice, storeXHR } from './store_common.js'; 


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
        localMessages: function() {
            // console.info('get local messages for field', this.field, this.messages);
            let { messages, field } = this;
            if(messages && messages[field] && messages[field].length > 0) {
                // console.info(messages[field]);
                return messages[field];
            }
            return null;
        }
    },
    template: `<div><p v-if="localMessages">
        <div class="alert alert-danger" role="alert" v-for="message in localMessages">
            <span class="fa fa-times"></span> {{ message }}
        </div>
    </p></div>`
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
        onInput($event) {
            this.$emit('update', this.field, $event);
        }
    },
    computed: {
        clazz: function() {
            let { messages, field } = this;
            if(messages && messages[field] && messages[field].length > 0) {
                return 'form-group has-error';
            }
            return 'form-group';
        }
    },
    template: `<div v-bind:class="clazz">
        <label class="col-sm-4 control-label">{{ title }}</label>
        <div class="col-sm-8">
            <input class="form-control" @input="onInput" v-bind:value="data[field]" />
            <store-messages :field="field" :messages="messages" />
        </div>
    </div>`
});

Vue.component('store-information-form', {
    props: {
        /** Field error messages, maps field name -> array */
        messages: Object,
        data: Object
    },
    created: function() {
        this.userInfo = {};
    },
    methods: {
        update: function(fieldName, $event) {
            // console.info('updated!', fieldName, $event.target.value);
            this.data[fieldName] = $event.target.value;
        }
    },
    template: `
<form class="form-horizontal" @submit.prevent>
    <p>Huomaathan, että lippukoodit lähetetään annettuun sähköpostiosoitteeseen.</p>
    <div class="row"><div class="col-lg-6">
        <store-form-group title="Etunimi" field="first_name" @update="update" :messages="messages" :data="data" />
        <store-form-group title="Sukunimi" field="last_name" @update="update" :messages="messages" :data="data" />
        <store-form-group title="Sähköposti" field="email" @update="update" :messages="messages" :data="data" />
        <store-form-group title="Vahvista sähköposti" field="email2" @update="update" :messages="messages" :data="data" />
        <store-form-group title="Matkapuhelin" field="mobile" @update="update" :messages="messages" :data="data" />
        <store-form-group title="Muu puhelinnumero" field="telephone" @update="update" :messages="messages" :data="data" />
    </div>
    <div class="col-lg-6">
        <store-form-group title="Katuosoite" field="street" @update="update" :messages="messages" :data="data" />
        <store-form-group title="Postinumero" field="postal_code" @update="update" :messages="messages" :data="data" />
        <store-form-group title="Kaupunki" field="city" @update="update" :messages="messages" :data="data" />
        <store-form-group title="Maa" field="country" @update="update" :messages="messages" :data="data" />
        <store-form-group title="Yritys" field="company" @update="update" :messages="messages" :data="data" />
    </div></div>
    <div class="form-group">
        <label class="col-lg-2 control-label">Lisätietoja</label>
        <div class="col-lg-10">
            <textarea class="form-control" @input="update('information', $event)" v-bind:value="data.information"></textarea>
            <store-messages field="information" :messages="messages" />
        </div>
    </div>
    <div class="form-group">
        <div class="col-sm-12">
            <label class="control-label">
                <input type="checkbox" v-model="data.read_terms" />
                <span>
                    Olen lukenut <a target="_blank" href="/store/terms">toimitusehdot</a> ja hyväksyn ne.
                </span>
            </label>
            <store-messages field="read_terms" :messages="messages" />
        </div>
    </div>
    <div class="clearfix"></div>
</form>
`
});

Vue.component('store-product', {
    props: {
        product: Object,
        cart: Array,
        messages: Object,
    },
    data: function () {
        // because there can be many components of the same type, a component's'
        // "data" is a factory function that should return unique objects
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
    computed: {
        cartCount: function() {
            let { product, variant } = this;
            if(!this.cart) {
                return 0;
            }
            var cartIndex = this.cart.findIndex((item) => {
                return cartItemEquals(item, product, variant);
            });

            if(cartIndex < 0) {
                return 0;
            }
            return this.cart[cartIndex].count;
        }
    },
    template: `
    <div class="product">
        <span class="pull-right">
            <span class="product-cart-count" v-if="cartCount > 0">
                <span class="fa fa-shopping-cart"></span> {{ cartCount }}
            </span>
            <select class="product-variants" v-if="product.variants && product.variants.length > 0" v-model="variant">
                <option v-for="variant in product.variants" v-bind:value="variant">
                    {{ variant.name }}
                </option>
            </select>
            <button class="btn btn-success" v-on:click="addItem()">
                <span class="fa fa-plus" /> Lisää
            </button>
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


var app = new Vue({
    el: '#store',
    data: {
        products: [],
        cart: [],
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
    template: `
<div>
<h3>Tuotteet</h3>
<div class="list-unstyled store-items">
    <store-product v-for="product in products"
        :product="product" :cart="cart" :messages="messages"
        v-on:addItem="addItem" />
</div>
<h3>Ostoskori</h3>
<store-messages field="items" :messages="messages" />
<div class="list-unstyled store-items">
    <div v-for="item in cart">
        <div class="pull-left">
            <span>{{ item.product.name }}</span>
            <span v-if="item.variant">({{ item.variant.name }})</span>
        </div>
        <span class="pull-right">
            x {{ item.count }} = {{ getSubtotal(item) | formatPrice }}
            <button class="btn btn-secondary" v-on:click="changeItemCount(item, 1)">+</button>
            <button class="btn btn-secondary" v-on:click="changeItemCount(item, -1)">-</button>
            <button class="btn btn-danger" v-on:click="removeItem(item)">
                <span class="fa fa-fw fa-trash"></span>
            </button>
        </span>
        <span class="clearfix"></span>
    </div>
    <div>Yhteensä: {{ totalPrice | formatPrice }}</div>
</div>
<h3>Tiedot</h3>
<store-information-form v-on:infoUpdate="updateInfo" :data="info" :messages="messages" />
<span class="pull-right">
    <button class="btn btn-primary" @click="submit">Jatka &gt;</button>
</span>
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
            this.cart.forEach(function (item) {
                totalPrice += component.getSubtotal(item);
            });
            this.totalPrice = totalPrice;
            // FIXME: Store cart in window.localStorage
        },
        addItem: function (product, variant) {
            // check if product/variant is already in items
            var found = this.cart.findIndex(function (item) {
                return cartItemEquals(item, product, variant);
            });
            if (found >= 0) {
                // if it is, splice a new item with a higher count
                var newItem = Object.assign({}, this.cart[found]);
                newItem.count++;
                this.cart.splice(found, 1, newItem);
            } else {
                // if it isn't, push a new item
                this.cart.push({
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
            var pos = this.cart.indexOf(item);
            this.cart.splice(pos, 1);
            this.updateCart();
        },
        changeItemCount: function (item, change) {
            // FIXME: Check item product max per order
            var pos = this.cart.indexOf(item);
            var item = this.cart[pos];
            if (item.count + change <= 0) {
                return this.removeItem(item);
            }
            item.count += change;
            this.cart.splice(pos, 1, item);
            this.updateCart();
        },
        getTransactionObject() {
            let transaction = Object.assign({}, info);
            transaction.items = this.cart.map((item) => ({
                item_id: item.product.id,
                variant_id: item.variant ? item.variant.id : null,
                amount: item.count,
            }));
        },
        submit: function() {
            let { info } = this;
            let { email, email2 } = info;

            // validate email before doing anything
            if(email !== email2) {
                this.messages = {
                    email: ['Kirjoita sama sähköpostiosoite kahdesti.'],
                    email2: ['Kirjoita sama sähköpostiosoite kahdesti.']
                }
                return;
            }

            let transaction = this.getTransactionObject();

            storeXHR('POST', '/api/store_transaction/?format=json', transaction).then((res) => {
                console.info(res);
            }, (err) => {
                this.messages = err;
                // Hack error message so both email fields show them.
                if(err) {
                    err.email2 = err.email;
                }
            }).catch(err => {
                console.error(err);
            });

        }
    }
});
