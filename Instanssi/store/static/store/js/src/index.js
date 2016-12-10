import Vue from 'vue';
import { formatPrice, storeXHR } from './store_common.js';
import './store_information.js';

/**
 * Returns true if a cart item is a specific product (and optional variant).
 * @param {Object} cartItem - Cart item to compare
 * @param {Object} product - Product to compare
 * @param {Object} [variant] - Variant to compare
 * @returns {Boolean} - True if cart item is the same product (and variant)
 */
function cartItemEquals(cartItem, product, variant) {
    return cartItem.product.id === product.id &&
        (!variant || (cartItem.variant && (variant.id === cartItem.variant.id)));
}

Vue.filter('formatPrice', formatPrice);

/**
 * Displays a single store product with cart counts and "add" button.
 */
Vue.component('store-product', {
    props: {
        product: Object,
        cart: Array,
        messages: Object,
    },
    data() {
        // because there can be many components of the same type, a component's'
        // "data" is a factory function that should return unique objects
        return {
            /** Currently selected item variant */
            variant: null,
        };
    },
    /**
     * Initialize the store product component, auto-selecting variant if available
     */
    created() {
        let product = this.product;
        if (product.variants && product.variants.length) {
            this.variant = product.variants[0];
        }
    },
    methods: {
        /**
         * Signal that a new item should be added to the cart.
         */
        addItem() {
            this.$emit('addItem', this.product, this.variant);
        }
    },
    computed: {
        /**
         * Get number of items (of the current variant type) already in the cart.
         * @returns {number} - Cart amount
         */
        cartCount() {
            let { product, variant } = this;
            if(!this.cart) {
                return 0;
            }
            let cartIndex = this.cart.findIndex((item) => {
                return cartItemEquals(item, product, variant);
            });

            if(cartIndex < 0) {
                return 0;
            }
            return this.cart[cartIndex].count;
        }
    },
    template: require('!raw-loader!./store_product.html'),
});

/**
 * Instanssi.org store frontend application.
 */
let app = new Vue({
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
    template: require('!raw-loader!./store.html'),
    created() {
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
        /**
         * Pick up changes to the customer information.
         * @param {Object} info - Customer info
         */
        updateInfo(info) {
            // Note that this is a shallow copy. Doesn't really harm anything.
            this.info = info;
        },
        /**
         * Calculates subtotal for a specific cart item, considering discounts, etc.
         * @param {Object} cartItem - Existing cart item
         * @return {number} - Subtotal for the item and its count in the cart
         */
        getSubtotal(cartItem) {
            let multiplier = 1;
            let qtyThresh = cartItem.product.discount_amount;
            let discountFactor = (100 - cartItem.product.discount_percentage) / 100;
            if(qtyThresh && cartItem.count >= qtyThresh) {
                multiplier *= discountFactor;
            }
            return cartItem.product.price * cartItem.count * multiplier;
        },
        /**
         * Update cart state, calculating total price and so on.
         */
        updateCart() {
            let totalPrice = 0;
            this.cart.forEach((cartItem) => {
                totalPrice += this.getSubtotal(cartItem);
            });
            this.totalPrice = totalPrice;
            // FIXME: Store cart in window.localStorage
        },
        /**
         * Add an item to the cart.
         * @param {Object} product - Product / StoreItem to add
         * @param {Object} [variant] - Variant to add, if any
         */
        addItem(product, variant) {
            // check if product/variant is already in items
            let found = this.cart.findIndex((item) => {
                return cartItemEquals(item, product, variant);
            });
            if (found >= 0) {
                // if it is, splice a new item with a higher count
                let newItem = Object.assign({}, this.cart[found]);
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
        /**
         * Removes an existing cart item from the cart.
         * @param {Object} cartItem - Cart entry to remove
         */
        removeItemFromCart(cartItem) {
            let pos = this.cart.indexOf(cartItem);
            this.cart.splice(pos, 1);
            this.updateCart();
        },
        /**
         * Updates an item's count in the shopping cart.
         * @param {Object} item - Item to update
         * @param {number} change - Items to add (or remove)
         */
        changeItemCount(item, change) {
            // FIXME: Check item product max per order
            let pos = this.cart.indexOf(item);
            let cartItem = this.cart[pos];
            if (cartItem.count + change <= 0) {
                this.removeItemFromCart(cartItem);
                return;
            }
            cartItem.count += change;
            this.cart.splice(pos, 1, cartItem);
            this.updateCart();
        },
        /**
         * Generates an API transaction object from the store's current state.
         * @returns {Object} - Transaction to submit
         */
        getTransactionObject() {
            let transaction = Object.assign({}, this.info);
            transaction.items = this.cart.map((item) => ({
                item_id: item.product.id,
                variant_id: item.variant ? item.variant.id : null,
                amount: item.count,
            }));
            return transaction;
        },
        /**
         * Sends the current store data to the backend.
         * @returns {Promise} - Request results
         */
        submit() {
            let { info } = this;

            // validate email before doing anything
            if(info.email !== info.email2) {
                this.messages = {
                    email: ['Kirjoita sama sähköpostiosoite kahdesti.'],
                    email2: ['Kirjoita sama sähköpostiosoite kahdesti.']
                }
                return;
            }

            let transaction = this.getTransactionObject();

            return storeXHR('POST', '/api/store_transaction/?format=json', transaction).then((res) => {
                console.info(res);
            }, (err) => {
                this.messages = err;
                // Manipulate error message so both email fields show errors
                if(err) {
                    err.email2 = err.email;
                }
            }).catch(err => {
                console.error(err);
            });

        }
    }
});
